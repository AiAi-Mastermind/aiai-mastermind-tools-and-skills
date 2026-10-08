"""Shared helpers for deterministic site drivers that run on Agent Chrome.

Everything goes through the agent-chrome wrapper (`agent-chrome pw <session> ...`), so the
wrapper's guards still apply: own tab only, no eval, no cookies, no raw CDP. This module only
parses the accessibility snapshots the wrapper returns and turns them into refs and markdown.

Runs on macOS's built-in Python 3.9; standard library only.
"""

from __future__ import annotations

import contextlib
import datetime
import json
import os
import re
import subprocess
import sys
import time



def _find_launcher():
    """The agent-chrome launcher from the aiai-agent-chrome kit (installed to ~/.local/share/agent-chrome)."""
    env = os.environ.get("AGENT_CHROME_BIN")
    candidates = [env] if env else []
    candidates += [os.path.expanduser(p) for p in (
        "~/.local/share/agent-chrome/bin/agent-chrome",
        "~/.claude/skills/agent-chrome/bin/agent-chrome",
        "~/.codex/skills/agent-chrome/bin/agent-chrome",
        "~/.agents/skills/agent-chrome/bin/agent-chrome")]
    for path in candidates:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return candidates[0] if env else os.path.expanduser("~/.local/share/agent-chrome/bin/agent-chrome")


AC = _find_launcher()
SESSION_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
OUT_ROOT = os.environ.get("BROWSER_RESEARCH_DIR") or os.path.expanduser(
    "~/Library/Application Support/BrowserResearch/runs")


class Stopped(BaseException):
    """Raised on SIGTERM/SIGHUP. Not an Exception, so retry loops can't swallow it; `with Session`
    still closes the tab on the way out."""


class DriverError(Exception):
    """A failure with a machine-readable status for the caller."""

    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


# ---------------------------------------------------------------- snapshot parsing

LINE = re.compile(r"^(?P<indent>\s*)- (?P<body>.*)$")
HEAD = re.compile(r'^(?P<role>[A-Za-z/][\w/-]*)(?: "(?P<name>(?:[^"\\]|\\.)*)")?(?P<rest>.*)$')
ATTR = re.compile(r"\[([^\]=]+)(?:=([^\]]*))?\]")


class Node:
    __slots__ = ("role", "name", "ref", "attrs", "text", "url", "children", "parent", "depth")

    def __init__(self, role, name, ref, attrs, text, depth):
        self.role, self.name, self.ref, self.attrs = role, name, ref, attrs
        self.text, self.url, self.children, self.parent, self.depth = text, None, [], None, depth

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def __repr__(self):
        return f"<{self.role} {self.name!r} ref={self.ref}>"


def _unquote_yaml(body):
    body = body.strip()
    if len(body) >= 2 and body[0] == "'" and body[-1] == "'":
        return body[1:-1].replace("''", "'")
    if len(body) >= 2 and body[0] == "'" and "':" in body:
        # 'button "x" [ref=e1]': text  -> quoted head followed by inline text
        end = body.index("':")
        return body[1:end].replace("''", "'") + body[end + 1:]
    return body


def _split_text(rest):
    """Split the part after attributes into attrs text and inline text (after ': ')."""
    depth, i = 0, 0
    while i < len(rest):
        ch = rest[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == ":" and depth == 0:
            return rest[:i], rest[i + 1:].strip()
        i += 1
    return rest, None


def _unescape(value):
    """Decode the escapes playwright writes into double-quoted YAML values (\\n, \\t, \\", \\xNN)."""
    if "\\" not in value:
        return value
    try:
        return json.loads('"' + re.sub(r"\\x([0-9A-Fa-f]{2})", r"\\u00\1", value) + '"')
    except ValueError:
        return value.replace('\\"', '"').replace("\\\\", "\\")


class Page:
    def __init__(self, raw):
        self.raw = raw
        self.url = self.title = ""
        self.roots = []
        head = raw.split("### Snapshot", 1)[0].split("### Modal state", 1)[0]
        m = re.search(r"^- Page URL: (.*)$", head, re.M)
        self.url = m.group(1).strip() if m else ""
        m = re.search(r"^- Page Title: (.*)$", head, re.M)
        self.title = m.group(1).strip() if m else ""
        # Split on section headers and use the LAST "Snapshot" section: a page-controlled alert()
        # text is echoed in "### Modal state" before it and could forge an earlier fence.
        sections = re.split(r"^### ", raw, flags=re.M)
        snap = [x for x in sections if x.startswith("Snapshot\n")]
        self.modal = any(x.startswith("Modal state") for x in sections)
        block = re.search(r"```yaml\n(.*)\n```", snap[-1], re.S) if snap else None
        self._parse(block.group(1) if block else "")

    def _parse(self, yaml_text):
        stack = []  # (indent, node)
        for line in yaml_text.splitlines():
            m = LINE.match(line)
            if not m:
                continue
            indent = len(m.group("indent"))
            body = _unquote_yaml(m.group("body"))
            if body.startswith("/url:"):
                if stack:
                    stack[-1][1].url = body[5:].strip().strip('"')
                continue
            if body.startswith("/"):  # /placeholder and other properties are not content
                continue
            head = HEAD.match(body)
            if not head:
                continue
            role, name = head.group("role"), head.group("name")
            if name is not None:
                name = _unescape(name)
            attrs_part, text = _split_text(head.group("rest"))
            attrs = {m.group(1).strip(): (m.group(2) if m.group(2) is not None else True)
                     for m in ATTR.finditer(attrs_part)}
            ref = attrs.pop("ref", None)
            if text is not None:
                text = text.strip()
                if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
                    text = _unescape(text[1:-1])
                text = text or None
            if role == "text" and name is None and text is None:
                continue
            node = Node(role, name, ref, attrs, text, indent)
            while stack and stack[-1][0] >= indent:
                stack.pop()
            if stack:
                node.parent = stack[-1][1]
                stack[-1][1].children.append(node)
            else:
                self.roots.append(node)
            stack.append((indent, node))

    def nodes(self):
        for root in self.roots:
            yield from root.walk()

    def find_all(self, role=None, name=None, pred=None, within=None):
        pool = within.walk() if within is not None else self.nodes()
        out = []
        for node in pool:
            if role is not None and node.role not in ((role,) if isinstance(role, str) else role):
                continue
            if name is not None:
                label = node.name or ""
                if isinstance(name, str):
                    if label != name:
                        continue
                elif not name.search(label):
                    continue
            if pred is not None and not pred(node):
                continue
            out.append(node)
        return out

    def find(self, role=None, name=None, pred=None, within=None):
        found = self.find_all(role, name, pred, within)
        return found[0] if found else None

    def has_text(self, pattern):
        rx = pattern if hasattr(pattern, "search") else re.compile(pattern)
        return any(rx.search((n.name or "") + " " + (n.text or "")) for n in self.nodes())


# ---------------------------------------------------------------- markdown rendering

BLOCK = {"heading", "paragraph", "listitem", "list", "table", "row", "rowgroup", "blockquote",
         "separator", "article", "region", "main", "code", "figure", "term", "definition"}
SKIP = {"button", "img", "textbox", "combobox", "checkbox", "radio", "switch", "slider",
        "menu", "menubar", "menuitem", "tablist", "tab", "toolbar", "navigation", "banner",
        "contentinfo", "dialog", "status", "progressbar", "search", "iframe", "listbox", "option"}


NAMED_TEXT = {"cell", "columnheader", "rowheader", "gridcell", "term", "definition", "code",
              "strong", "emphasis", "heading", "time", "mark", "insertion", "deletion", "subscript", "superscript"}
CONTAINERS = {"article", "region", "main", "complementary", "list", "table", "row", "rowgroup", "group",
              "feed", "form", "document", "application", "log"}


def _inline(node):
    if node.role in SKIP:
        return ""
    if node.role == "link":
        label = (node.name or node.text or "".join(_inline(c) for c in node.children)).strip()
        label = label.replace("\u2060", "").strip()
        if node.url and label:
            return f"[{label}]({clean_url(absolute(node.url))})"
        return label
    parts = []
    if node.role == "text":
        parts.append(node.text or node.name or "")
    elif node.text:
        parts.append(node.text)
    elif node.name and not node.children and node.role not in CONTAINERS:
        # Table cells, headers and leaf nodes carry their text as the accessible name. When the node
        # has rendered children, those are the text (the name would repeat it).
        parts.append(node.name)
    for child in node.children:
        piece = _inline(child)
        if piece:
            parts.append(piece)
    joined = " ".join(p.strip() for p in parts if p and p.strip())
    joined = re.sub(r"\s+([.,;:!?%)\]])", r"\1", joined)
    joined = re.sub(r"([(\[])\s+", r"\1", joined)
    if node.role in ("strong", "emphasis") and joined:
        mark = "**" if node.role == "strong" else "*"
        return f"{mark}{joined}{mark}"
    if node.role == "code" and joined and "\n" not in joined:
        return f"`{joined}`"
    return joined


_BASE = [""]


def absolute(url):
    if url.startswith("/") and _BASE[0]:
        m = re.match(r"^(https?://[^/]+)", _BASE[0])
        return (m.group(1) if m else "") + url
    return url


TRACKING_EXACT = {"igsh", "igshid", "mibextid", "rdid", "fbclid", "gclid", "ref_src", "ref_url", "referrer",
                  "share_url", "sfnsn", "extid"}
TRACKING_PREFIX = ("utm_", "__cft__", "__tn__", "__xts__", "__eep__", "__rsidv2__", "__eps__")
X_HOSTS = ("x.com", "twitter.com")


def clean_url(url):
    """Drop tracking and share-context parameters that can identify who shared or clicked."""
    import urllib.parse
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return url
    if not parts.query:
        return url
    on_x = parts.netloc.lower().endswith(X_HOSTS)
    keep = []
    for key, value in urllib.parse.parse_qsl(parts.query, keep_blank_values=True):
        bare = key.lower()
        if bare in TRACKING_EXACT or bare.startswith(TRACKING_PREFIX) or (on_x and bare in ("s", "t")):
            continue
        keep.append((key, value))
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(keep)))


def _has_block(node):
    return any(child.role in BLOCK or _has_block(child) for child in node.children)


def to_markdown(node, base_url="", _level=0):
    """Render a snapshot subtree as readable markdown (answer text + inline links)."""
    _BASE[0] = base_url or _BASE[0]
    lines = []
    role = node.role
    if role in SKIP:
        return ""
    if role == "heading":
        level = int(node.attrs.get("level", 2)) if str(node.attrs.get("level", "2")).isdigit() else 2
        text = node.name or _inline(node)
        return ("#" * min(level, 6) + " " + text.strip()) if text.strip() else ""
    if role == "paragraph":
        return _inline(node)
    if role == "list":
        items = []
        for child in node.children:
            if child.role == "listitem":
                if _has_block(child):
                    inner = [to_markdown(c, base_url, _level + 1) for c in child.children]
                    inner = [x for x in inner if x.strip()]
                    first = inner[0] if inner else ""
                    rest = ["  " + ln for x in inner[1:] for ln in x.splitlines()]
                    items.append("  " * _level + "- " + first + ("\n" + "\n".join(rest) if rest else ""))
                else:
                    text = _inline(child)
                    if text:
                        items.append("  " * _level + "- " + text)
            else:
                sub = to_markdown(child, base_url, _level)
                if sub:
                    items.append(sub)
        return "\n".join(items)
    if role == "table":
        rows = [r for r in node.walk() if r.role == "row"]
        grid = []
        for row in rows:
            cells = [c for c in row.children if c.role in ("cell", "columnheader", "rowheader", "gridcell")]
            grid.append([_inline(c).replace("|", "\\|") for c in cells])
        grid = [g for g in grid if any(x.strip() for x in g)]
        if not grid:
            return ""
        width = max(len(g) for g in grid)
        grid = [g + [""] * (width - len(g)) for g in grid]
        out = ["| " + " | ".join(grid[0]) + " |", "|" + "---|" * width]
        out += ["| " + " | ".join(g) + " |" for g in grid[1:]]
        return "\n".join(out)
    if role == "code" and _inline(node).count(" ") > 12:
        raw = node.text or node.name or " ".join(_inline(c) for c in node.children)
        return "```\n" + raw.strip().strip("`") + "\n```"
    if role == "blockquote":
        return "\n".join("> " + ln for ln in _inline(node).splitlines())
    if not _has_block(node):
        return _inline(node)
    for child in node.children:
        piece = to_markdown(child, base_url, _level)
        if piece and piece.strip():
            lines.append(piece)
    if node.text:
        lines.insert(0, node.text)
    return "\n\n".join(lines)


def between(root, start, end):
    """Maximal subtrees that lie strictly after `start` (and outside it) and before `end`, in
    document order. Used to cut an answer out of a page between two landmarks."""
    order = list(root.walk())
    index = {id(n): i for i, n in enumerate(order)}
    first = index[id(start)] + sum(1 for _ in start.walk())  # skip start and its subtree
    last = index[id(end)]

    def span(node):
        i = index[id(node)]
        return i, i + sum(1 for _ in node.walk()) - 1

    out = []

    def visit(node):
        lo, hi = span(node)
        if hi < first or lo >= last:
            return
        if lo >= first and hi < last:
            out.append(node)
            return
        for child in node.children:
            visit(child)

    visit(root)
    return out


def links_in(node, host_filter=None):
    """Unique (label, absolute url) pairs inside a subtree, in document order."""
    seen, out = set(), []
    for n in node.walk():
        if n.role == "link" and n.url:
            url = clean_url(absolute(n.url))
            if host_filter and not re.search(host_filter, url):
                continue
            if url in seen:
                continue
            seen.add(url)
            out.append({"title": (n.name or _inline(n) or "").replace("\u2060", "").strip(), "url": url})
    return out


# ---------------------------------------------------------------- the wrapper session

def run_ac(args, timeout=60):
    # Own process group, so a timeout kills the wrapper and its playwright-cli client together.
    # (The one-close-per-tab rule in Session is what prevents a second tab-close.)
    try:
        proc = subprocess.Popen([AC] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                start_new_session=True)
    except OSError:
        raise DriverError("not_installed", "agent-chrome launcher not found; install the aiai-agent-chrome kit "
                          "(or set AGENT_CHROME_BIN)")
    try:
        out, err = proc.communicate(timeout=timeout)
    except BaseException as exc:
        import signal
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
        proc.communicate()
        if isinstance(exc, subprocess.TimeoutExpired):
            raise DriverError("error", f"agent-chrome {args[0]} timed out after {timeout}s")
        raise
    return proc.returncode, out, err


@contextlib.contextmanager
def site_lock(name, timeout=600):
    """Serialize a critical section across processes (e.g. Perplexity's shared Incognito toggle)."""
    import fcntl
    folder = os.path.expanduser("~/Library/Caches/agent-chrome")
    os.makedirs(folder, mode=0o700, exist_ok=True)
    fd = os.open(os.path.join(folder, f"{name}.lock"), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    deadline = time.time() + timeout
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.time() >= deadline:
                    raise DriverError("busy", f"another {name} run held the lock for {timeout}s")
                time.sleep(2)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def install_sigterm():
    """Turn SIGTERM into an exception so `with Session(...)` still closes the tab and detaches."""
    import signal

    def _raise(signum, frame):
        raise Stopped("stopped by the caller (signal %d)" % signum)

    signal.signal(signal.SIGTERM, _raise)
    signal.signal(signal.SIGHUP, _raise)
    os.umask(0o077)  # everything this process writes (answers, manifests) is private


class Session:
    """One task tab in Agent Chrome. Use as a context manager so the tab always closes."""

    def __init__(self, prefix, debug=False):
        name = f"{prefix}-{os.getpid()}-{int(time.time()) % 100000}"
        if not SESSION_NAME.fullmatch(name):
            raise DriverError("error", "bad session name")
        self.name, self.debug, self.opened = name, debug, False

    def log(self, message):
        if self.debug:
            print(f"[{self.name}] {message}", file=sys.stderr)

    def __enter__(self):
        install_sigterm()
        code, _, err = run_ac(["attach", self.name], timeout=90)
        if code:
            raise DriverError("not_running" if code == 5 else "error",
                              "could not attach to Agent Chrome (run agent-chrome doctor)")
        return self

    def __exit__(self, *exc):
        # Best effort and never raising: a hung tab-close must not skip detach (which wipes the
        # session's private snapshots) or turn a finished run into an error.
        try:
            if self.opened:
                self.opened = False  # one attempt only: never send a second tab-close for this tab
                run_ac(["pw", self.name, "tab-close"], timeout=45)
        except DriverError:
            pass
        finally:
            try:
                run_ac(["pw", self.name, "detach"], timeout=45)
            except DriverError:
                pass
        return False

    def pw(self, *args, timeout=60, check=True):
        code, out, err = run_ac(["pw", self.name] + list(args), timeout=timeout)
        if code and check:
            detail = (err or out).strip().splitlines()[-1:] or [""]
            raise DriverError("error", f"pw {args[0]} failed ({code}): {detail[0][:200]}")
        return out

    def open(self, url):
        try:
            self.pw("tab-new", url, timeout=90)
        finally:
            # The wrapper records the tab as ours even when navigation failed; always try to close it.
            self.opened = True
        self.log(f"opened {url}")

    def snapshot(self):
        page = Page(self.pw("snapshot", timeout=90))
        if page.modal:
            # A JavaScript alert/confirm is open: the page is blocked and its text is page-controlled.
            raise DriverError("ui_changed", "a page dialog (alert/confirm) is open; nothing was read")
        return page

    def click(self, node_or_ref):
        ref = node_or_ref.ref if isinstance(node_or_ref, Node) else node_or_ref
        if not ref:
            raise DriverError("ui_changed", "element has no ref to click")
        self.pw("click", ref)

    def fill(self, node_or_ref, text):
        ref = node_or_ref.ref if isinstance(node_or_ref, Node) else node_or_ref
        if not ref:
            raise DriverError("ui_changed", "element to fill was not found")
        # The wrapper refuses any argument that starts with "-"; never lose the question over that.
        self.pw("fill", ref, safe_arg(text))

    def type(self, text):
        self.pw("type", safe_arg(text))

    def press(self, key):
        self.pw("press", key)

    def wait(self, predicate, timeout, interval=3.0, on_tick=None):
        """Poll snapshots until predicate(page) is truthy; returns (page, value)."""
        deadline = time.time() + timeout
        page = None
        while True:
            page = self.snapshot()
            value = predicate(page)
            if value:
                return page, value
            if on_tick:
                on_tick(page)
            if time.time() >= deadline:
                return page, None
            time.sleep(interval)


def focus_walk(session, start_box, is_target, key="Tab", max_steps=40, pause=0.3):
    """Reach a control without clicking: focus a textbox with fill, then press Tab (or Shift+Tab)
    until the snapshot marks the wanted element [active]. Clicks need the tab in front; keys don't."""
    session.fill(start_box, "")
    for _ in range(max_steps):
        page = session.snapshot()
        node = next((n for n in page.nodes() if n.attrs.get("active")), None)
        if node is not None and is_target(node):
            return page, node
        session.press(key)
        time.sleep(pause)
    raise DriverError("ui_changed", "could not reach the control by keyboard")


BENIGN_DIALOG = re.compile(r"cookie", re.I)


def composer_ready(page, box, must_contain):
    """True when Enter will submit this box: it holds our text, it isn't inside a dialog, and it has
    keyboard focus. Playwright marks focus ([active]) only when it can see it; when no node on the
    page is marked at all, focus is unknowable, so accept only if no blocking dialog is open."""
    if box is None or any(a.role in ("dialog", "alertdialog") for a in box.ancestors()):
        return False
    text = " ".join((n.text or "") for n in box.walk())
    if must_contain[:40] not in " ".join(text.split()):
        return False
    if box.attrs.get("active"):
        return True
    if any(n.attrs.get("active") for n in page.nodes()):
        return False  # focus is known and it is somewhere else
    return not any(n.role in ("dialog", "alertdialog") and not BENIGN_DIALOG.search(n.name or "")
                   for n in page.nodes())


LANDMARKS = ("navigation", "complementary", "banner", "contentinfo", "log", "textbox", "article")


def banner_text(page, skip_ids=()):
    """Text of alerts, status lines and dialogs only, outside navigation/sidebars/chat logs/textboxes:
    where a usage-limit notice appears, and never our own question or old chat titles."""
    skip = set(skip_ids)
    for n in page.nodes():
        if n.role in LANDMARKS:
            skip.update(id(x) for x in n.walk())
    out = []
    for n in page.nodes():
        if n.role in ("alert", "status", "dialog", "alertdialog") and id(n) not in skip:
            out += [f"{x.name or ''} {x.text or ''}" for x in n.walk() if x.role != "link" and id(x) not in skip]
    return " ".join(out)


def safe_arg(text):
    text = " ".join(str(text).split()) if "\n" not in str(text) else str(text)
    return text if not text.startswith("-") else "‐" + text[1:]


# ---------------------------------------------------------------- sign-in and output

SIGNIN_URL = re.compile(r"^https?://[^/]+/(login|signin|sign-in|sign_in|checkpoint|i/flow/login|"
                        r"i/jf/onboarding|accounts/login|aymh)(?:[/?#.]|$)", re.I)


def looks_signed_out(page, extra=None):
    if SIGNIN_URL.search(page.url):
        return True
    if page.find("textbox", re.compile(r"^(Password|Email or mobile number|Mobile number, username or email)$")):
        return True
    if extra and extra(page):
        return True
    return False


def slug(text, limit=48):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s[:limit].rstrip("-") or "query")


def write_result(lane, query, result, out=None):
    """Write the markdown evidence file and return its path. Private dir, 0600 files."""
    now = datetime.datetime.now()
    if out:
        path = os.path.abspath(os.path.expanduser(out))
        private_dirs(os.path.dirname(path))
    else:
        folder = os.path.join(OUT_ROOT, now.strftime("%Y-%m-%d"))
        private_dirs(folder)
        path = os.path.join(folder, f"{now.strftime('%H%M%S')}-{lane}-{slug(query)}.md")
    front = {
        "lane": lane, "query": query, "status": result.get("status"),
        "mode": result.get("mode"), "isolation": result.get("isolation"),
        "retrieved_at": now.astimezone().isoformat(timespec="seconds"),
        "thread_url": result.get("thread_url"), "elapsed_s": result.get("elapsed_s"),
    }
    body = ["---"] + [f"{k}: {json.dumps(v)}" for k, v in front.items() if v is not None] + ["---", ""]
    body.append(f"# {lane}: {query}\n")
    body.append(result.get("answer_markdown") or "_No answer captured._")
    sources = result.get("sources") or []
    if sources:
        body.append("\n## Sources\n")
        body += [f"{i}. [{s.get('title') or s['url']}]({s['url']})" for i, s in enumerate(sources, 1)]
    write_private(path, "\n".join(body).rstrip() + "\n")
    return path


def private_dirs(folder):
    """Create folder as 0700. Tighten existing folders only inside the research root: a caller's
    --out path in their own folder (a repo, the home folder) is left as it is."""
    os.makedirs(folder, mode=0o700, exist_ok=True)
    root = os.path.abspath(OUT_ROOT)
    here = os.path.abspath(folder)
    if not (here == root or here.startswith(root + os.sep)):
        return
    while True:
        if os.path.isdir(here) and not os.path.islink(here) and os.stat(here).st_uid == os.getuid():
            os.chmod(here, 0o700)
        if here == root or not here.startswith(root) or os.path.dirname(here) == here:
            break
        here = os.path.dirname(here)


def write_private(path, text):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(text)


def emit(result, as_json):
    if as_json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"status: {result.get('status')}")
        if result.get("file"):
            print(f"file: {result['file']}")
        if result.get("message"):
            print(f"message: {result['message']}")
        if result.get("answer_markdown"):
            print()
            print(result["answer_markdown"])
            for i, s in enumerate(result.get("sources") or [], 1):
                print(f"[{i}] {s.get('title') or ''} {s['url']}")
    return 0 if result.get("status") == "done" else 1
