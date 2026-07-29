# Diagnosis Playbooks — Purple Belt

Use these only after date-matched CEO math, or when diagnosis is explicitly requested. Phillip's order is fixed:

> “Check search terms first. Then ad quality. Then bids.”

Choose the leading issue and recommend one move only.

## 1. Search-term scan

### Keywords versus search terms

- **Keywords** are what the account bids on inside Ad Groups.
- **Search terms** are what people actually typed and appear in the Search Terms report.

“The gap between these two is where your money gets wasted, or gets well spent.”

### Scan procedure

1. Open the same-date Search Terms export.
2. Sort by Cost or Clicks descending.
3. Review top-spend terms first.
4. Mark each term:
   - **Green:** clear quote/shopping intent for installed product and carrier.
   - **Yellow:** ambiguous; monitor before blocking.
   - **Red:** a red-flag category with almost no quote intent.
5. Sum dollars actually spent on Red terms.
6. Compare Red-term spend with total spend before acting.

### Six red-flag categories

| Category | Workshop examples |
|---|---|
| Existing customers | State Farm login; pay bill; claims; app download; policy number |
| Competitor brands | Geico quote; Progressive insurance; Allstate near me; USAA auto |
| Job seekers | State Farm careers; hiring; how to become an agent; employment |
| Wrong products | pet insurance; Medicare; commercial trucking; SR-22; salvage title |
| Low intent / research | reviews; ratings; Wikipedia; Reddit; complaints; BBB |
| Service/support | roadside assistance; tow truck; customer service |

### Proportion before panic

Do not call the whole campaign waste because four junk clicks exist. Calculate dollars. In Matt's review, suspicious clicks were only about $110 of roughly $1,100. But cheap junk is not harmless: “we've seen a whole campaign worth of wasted ad spend... 50 cents a click added up to $700 of nothing.”

If traffic looks odd but profitable quotes arrive, “we cannot argue with the result.” If terms are odd **and** outcomes are poor, act.

### Add-as-negative mechanics

For a clearly Red term:

1. Select it in **Insights and Reports > Search Terms**.
2. Choose **Add as negative keyword**.
3. Add it to the appropriate existing list or carefully named custom list.
4. Confirm the list is applied to the campaign.
5. Prefer a reversible, precise exclusion; do not casually block Yellow terms.

The member executes this manually. Never claim it was done.

### Four installed master exclusion lists

- **301+ List** — broad exclusions: educational, career, informational, cheapskate terms.
- **Master Common Negative** — frequent service terms: claims, DUI, login, renewals.
- **Competitor List** — 33 competitor brand names.
- **Negative General** — 89 terms: existing-customer actions, corporate, high-risk, specialty.

Go to **Tools > Shared Library > Exclusion Lists**. Verify all four exist **and are applied**. A list tied to zero campaigns does nothing.

### Search Term Guardian

AIAI's Search Term Guardian scans search terms daily, auto-blocks high-confidence waste according to protection level, and alerts on clicks costing $50+. Obvious waste includes phone numbers, login, pay bill, claims, careers, corporate, competitor names, wrong-state terms, and carrier-entertainment searches. Medium-confidence patterns such as 5+ clicks with zero conversions are flagged for review.

Monitoring does not replace the CEO's monthly review.

## 2. Ad quality

Check quality only after search terms.

### Ad Strength

Path: **Campaign > Ads > open the main ad**. Record **Poor, Average, Good, or Excellent**.

When outcomes are weak and Ad Strength is below Excellent, allowed workshop improvements are:

- add headline variations containing state or city;
- use agency-specific language consistent with the installed template;
- after the account has run 30+ days, upload agency photos such as a professional headshot or office photo.

The workbook action is “Improve ad strength to Excellent.” Do not rewrite the campaign from scratch.

### Quality Score

Quality Score **8+** is a supporting target in the CEO grid. It can explain auction cost/relevance, but never replaces spend, leads, households, CPQ, or CPA.

## 3. Match types and modes

### Match types

- **Exact:** `[State Farm auto insurance quote]` — tightest filter, highest intent, lowest volume.
- **Phrase:** `"State Farm auto insurance quote"` — medium filter; includes the phrase's meaning.
- **Broad:** `State Farm auto insurance quote` — widest reach, highest noise.

Google may make close variations even on Exact. Do not promise literal-only matching.

### Volume Mode — Shotgun

- Phrase + Broad.
- CPC commonly **$8–$20**.
- More clicks and faster data collection.
- More claims, service, and junk noise.
- Best for new campaigns and first **30–60 days**.
- Requires tight negative-keyword defense.

### Precision Mode — Sniper

- Exact + limited Phrase.
- CPC commonly **$25–$40+**.
- Fewer clicks, higher intent, cleaner traffic.
- Best for established campaigns or tighter budgets after data exists.

“Most agents start in Volume Mode to train Google's algorithm, then graduate to Precision Mode.” Both can work; economics decides.

### Shotgun-to-sniper switch

Use only when data supports it and it is the single approved move. Per campaign, about 15 minutes:

1. Open campaign and enter an Ad Group.
2. Open Keywords.
3. Change every keyword to Exact Match with brackets.
4. Pick **ONE** highest-converting keyword and set it to Phrase as the volume control.
5. Repeat for each Ad Group.
6. Save and walk away for **14 days**.

Post-switch expectations, verbatim:

- **Clicks drop 40–70%** — “That is the entire point.”
- **CPC rises +$10–25** — each click costs more but is more qualified; CPQ often stays flat or drops.
- **Quality goes up** — clicks should be more serious shoppers.
- **“Wait 14 days before judging.”** Then check CPQ.

### Reverse move for low volume

Tony's case supports moving Precision toward Phrase when search volume is too low. First verify geography and Keyword Planner volume, then bring the change to the Wednesday Huddle. Allow 7–14 days afterward.

### Restart heuristic

Phillip observed that adding a major direction change to a learned campaign can take longer and sometimes disrupt it; “a new campaign is a different story.” Also: “sometimes we literally just reboot and relaunch — we did nothing new and the campaign worked.”

This skill does not create or relaunch campaigns. Refer that decision to `aiaimastermind.com/adsmasteryzoom` or `aiaimastermind.com/adextracare`.

## 4. Bids and budget

### Bid-cap tactic

When CPC spikes from competition and outcome data supports intervention, Tony's case used a max bid near **70–75% of the highest bid**. This is case-based, not universal. It must be the one move, followed by a wait.

### CPC versus CPQ

> CPC is the price of one click. CPQ is what you paid for an actual lead action. CPA versus LTV tells whether the investment worked.

High CPC with a strong clicks-to-quote-start ratio and acceptable CPQ may be fine. CPC above the supplied regional range plus weak outcomes deserves action.

### Budget realism

- **$300/month:** too little to judge reliably; only a few calls may occur.
- **About $1,000–$1,500/month:** typical starting context.
- **$2,000–$3,000:** scaling context.
- **$12,000–$60,000:** big-player context, not a recommendation.

Never spend to win an ego contest. “Know your number and stay true to it.”

Never split one working budget to imitate expansion. “$50 auto $50 fire is not expanding, that's robbing yourself.”

## 5. Competition — Auction Insights

Path: **Campaign > Insights and Reports > Auction Insights**.

- **Impression share:** appearance share from eligible opportunities.
- **Top-of-page rate:** frequency above organic results.
- **Position-above rate:** when both showed, how often the other ranked higher.
- **Outranking share:** how often yours ranked above theirs or showed alone.

Separate national aggregators from local agents. The practical comparison is usually local agents.

### Matt Davis example

NerdWallet and Insurify appeared more often, but top-of-page rates were around 2% and 8%. More visibility did not mean better position. An opposing position-above figure of 21% meant Matt's ad was higher roughly 80% of the time when both appeared.

### NetQuote reality

NetQuote is corporate-subsidized and can use custom destination pages unavailable to captive agents. Phillip: it is “almost hopeless to compete against” directly. Captive agents can adjust ads and use the carrier microsite. Judge against local agents, not aggregator resources.

### Conquest and defensive awareness

Other agents may bid on the member's name. Much own-name traffic consists of existing customers trying to pay bills, so keep own-name/service terms excluded from lead campaigns. A Defensive campaign protects local branded demand, but creation/configuration goes to the Wednesday Huddle/support.

### Ad Transparency Center

Go to `adstransparency.google.com`, search the biggest local competitor, and record its active message. Reconnaissance only.

## 6. Ad not showing — checklist in order

1. **Advertiser verification:** complete?
2. **Ad review:** still under review? It “usually shows 6–8 hours later.”
3. **Location/search volume:** geography too small?

Use **Tools > Keyword Planner** to compare city, county, and state. A city with “only 10 people a month” searching may be the cause. Phillip's heuristic: start with the whole state, see which area converts, then hone in.

Because geographic restructuring alters the installed template, diagnose here but send execution to the Wednesday Huddle/support.

## 7. Destination page — the one allowed lever

Check whether installed ad traffic goes directly to the carrier's **quote-start page**, not the homepage. Do not propose redesigning the carrier microsite.

Bundle caution: bundle traffic attracts rate shoppers, requires an extra click, and may convert lower. Phillip preferred auto and home separately first, with a $500/$500 example. Campaign separation or destination correction is a support decision, not a build task for this skill.
