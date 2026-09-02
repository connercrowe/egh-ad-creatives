# Routine port: cc-shopify-ads-weekly-review
Source description: Weekly STRATEGY review of the Shopify lead-gen search campaign (negatives are handled daily by cc-search-terms-daily)
Ported mechanically by port_task.py; review before creating the routine.

---
You are running unattended as a cloud Routine: a fresh clone of the google-ads-mcp repository is your working directory, PYTHONPATH=src and the Google Ads credentials are set as environment variables, and there is no browser and no access to Conner's desktop files. If `python -c "import google_ads_mcp"` fails or the credentials are missing, say so in one line as your entire report and stop. GOOGLE_ADS_ALLOW_WRITES is not set in the environment; a task that is permitted one write sets it inline on that command only, exactly as written below.

Run the weekly STRATEGY review of Conner Crowe's Shopify lead-gen Google Ads campaign. READ-ONLY.
Propose changes; do not apply them without Conner's explicit approval in the conversation.

SCOPE BOUNDARY — READ THIS FIRST
Search-term cleanup and negatives belong to the daily task `cc-search-terms-daily` (08:15). Budget re-assertion belongs to `cc-budget-guard` (04:33). Do not duplicate either. Spend this review on: keywords, bids, ad copy, conversion tracking, and the leading indicator below.

STRATEGY STATE (rebuilt 2026-08-14 — full five-workstream dissection, executed with Conner's sign-off; supersedes ALL earlier strategy notes in this file's history)
- Verdict that drove the rebuild: the commodity head terms ("ecommerce web design" etc.) were arithmetically unwinnable at this budget ($17-20k/mo table stakes, 76-84% of visible spend on theme shoppers/competitor navigation), while thin high-bid-floor auctions (migration, Plus, CRO) hold the qualified demand.
- Budget: $15.00/day approved. AdPulse still paces to a stale $1,000 August target until Conner edits it (Aug target should be $665; the Sept-forward $500/mo schedule already exists in AdPulse). The guard task corrects drift daily at 04:33. Report budget as fact; propose nothing about it.
- Killed (deliberately PAUSED 2026-08-14, do not propose re-enabling without new evidence): PHRASE "ecommerce web design", "custom shopify theme", "shopify web design", "shopify website design"; EXACT "e commerce web designer"; the duplicate EXACT "ecommerce website design services" in Ecommerce Web Design (the converter copy lives ENABLED in Shopify Ecommerce Design 199913427098, routing that query family to /shopify-store-design/, the page that holds desktop traffic 50s/98% scroll).
- Mobile bid adjustment -100% (43% of spend, 0 conversions, 5-6s sessions). Revisit only after the mobile consent-bar fix has 60 days of desktop baseline behind it.
- NEW ad groups (2026-08-14): Migration (EXACT: woocommerce to shopify migration, migrate to shopify, shopify migration agency, bigcommerce to shopify migration -> /shopify-migration/) and Shopify Plus (EXACT: shopify plus agency -> /shopify-store-design/). The old migration-keyword prohibition is LIFTED via its own exit clause: /shopify-migration/ is written for replatform intent. The two older LPs still argue against replatforming, which is correct for THEIR traffic.
- Brand hard rule made structural: shared list "CC Neg 00 - Brand" (9 spellings PHRASE) attached to both campaigns; ad group "Name" (185959195189) PAUSED. Never propose brand bidding.
- In-market audiences attached in OBSERVATION mode (4). They restrict nothing; use their segment data.
- Conversion values: Form lead = $100, Call booked = $250 (relative weights, not revenue). MANUAL_CPC stays until recorded conversions reach ~15/30d sustained; do not propose tCPA/MaxConv before that.

ACCOUNT
Customer 5294557080, login/MCC 4727088547. Campaign 24096546152, MANUAL_CPC, geo PRESENCE US.
Campaign first served 2026-08-03; baseline RESET 2026-08-14 (the rebuild). Weekly comparisons against pre-rebuild data measure the strategy change, not performance drift — label them as such.
Landing pages (all noindex, paid-only): /shopify-store-design/ (merchants already on Shopify), /ecommerce-website-design/ (platform-agnostic), /shopify-migration/ (replatform intent, added 2026-08-14).
Offer: custom Shopify storefront builds from $5,000, 2-4 weeks, free homepage mockup in 24 hours (changed from three business days 2026-08-14; Conner confirmed deliverable, proven on the AutoAir mockup). Secondary path Calendly. If any ad copy, sitelink, or lander still says "3 days" or "three business days", that is a regression worth flagging.
AD COVERAGE: every enabled ad group carries THREE enabled RSAs, each on a distinct angle (offer, credibility, and a third specific to the group: theme problem / price transparency / zero downtime / platform proof / Plus technical). If any enabled ad group drops below three, flag it and name the missing angle.
Campaign "Branded - Conner Crowe" 23078888311 intentionally PAUSED. Do not enable.

GOTCHA: `shopify` PHRASE is an AD-GROUP-level negative (id 3778115140) inside Ecommerce Web Design — deliberate traffic shaping. Negative-conflict checks must be scoped PER AD GROUP.

HOW TO QUERY (read-only):
  stay in the repository root
  PYTHONPATH="src" python -c "from google_ads_mcp.client import build_client; from google_ads_mcp.config import load_config; ..."
NEVER set GOOGLE_ADS_ALLOW_WRITES=true in this task and never run a connercrowe_*.py script with --execute unless Conner approves that specific change in the conversation first.

WEEKLY PULL
1. Last 7 days: impressions, clicks, cost, conversions, CTR, avg CPC, cost/conv. Compare to prior 7 days WITH the baseline-reset caveat.
2. THE LEADING INDICATOR (open the report with this): in-ICP share of visible search-term spend. Pre-rebuild it was 12.4%. Target: above 60% within two weeks of 2026-08-14. If it is above 60% and leads are still zero at 60+ days, the auction thesis holds and the offer/LP is the suspect. If it is stuck below 40%, the keyword thesis is wrong — say so plainly.
3. Keyword performance BY AD GROUP, keyed by criterion_id (same text exists in multiple ad groups). Watch the Migration/Plus EXACT groups: at $12-15 bid floors and $15/day they may serve thinly — days with zero impressions are expected, a full zero WEEK on all of them means bids are below the floor and needs flagging with position_estimates data.
4. Conversion actions: "Form lead (all site forms)" 7707923469 ($100) and "Call booked (Calendly)" 7708134618 ($250) still ENABLED/primary; any recordings.
5. change_event for the last 7 days: GOOGLE_ADS_WEB_CLIENT = human, GOOGLE_ADS_API = scripts (03:22 = AdPulse pacer, 04:33 = budget guard, 08:15 = autopilot). Flag manual UI edits and any API write outside those windows.
6. Skim the week's autopilot JSON reports (_reports/cc_search_terms/) for hold/refused arrays. Mine HOLD for buyer-intent keyword candidates — HOLD has no promotion path, so clean buyer queries sit there.

KILL CRITERIA (set 2026-08-14, do not move the goalposts)
- Day 60 (2026-10-13): 2+ qualified leads at sub-$200 CPA -> propose scaling toward the full migration+Plus+CRO cluster (~$1,550/mo). Zero leads with in-ICP >60% -> propose the offer test (ad-level outcome-plus-price vs free-mockup). In-ICP still <40% -> propose exiting paid search.
- Any storefront build closing from any channel earns that channel the next dollar.

NOT TRIGGERED. READ THIS BEFORE JUDGING THE CAMPAIGN: the only lead so far (Ron Ahearn, owner of Auto Air Online, form fill 2026-08-10 on /shopify-store-design/, paid-attributed with gclid) received the storefront design **FREE in exchange for a Google review**. Conner calls it a deliberate one-off. **No money changed hands, so no kill criterion fired and the campaign's record is 1 lead, $0 revenue on $396.48.** Report it that way. If any earlier note or memory claims AutoAir was a sale or a close, that claim was corrected on 2026-08-14 and is wrong. What the engagement did produce is a 5-star public review (GBP went 8 -> 9 reviews) and a portfolio piece, both real but neither revenue. Watch the offer question it sharpens: the free mockup drew someone who took the free work and had his own web team. That is the tire-kicker failure mode the dissection predicted, at n=1, and it raises rather than settles the value of the day-60 offer test.

CONTEXT THAT PREVENTS WRONG ADVICE
- No speed/page-performance ad claims (live builds POOR on LCP).
- Never propose negatives on bare "theme"/"themes"/"template"/"free"/"hiring"/platform names.
- Conversion counting is goal-governed: GOOGLE_HOSTED local actions are non-biddable at customer-goal level and never hit the Conversions column; primary_for_goal on them is a legacy field the API refuses to change. Read customer_conversion_goal before concluding anything.
- Consent banner gates the dataLayer push; genuine-lead loss measured at zero as of 2026-08-14, cross-check with cc-lead-conversion-reconcile.
- Do not suggest publishing SugarBabies' unpublished products (out-of-stock, POS-synced).

TONE
Lead with numbers, direct, no preamble. Uneventful week = three lines. Flag uncertainty honestly.

## Output rule for the cloud
You cannot append to any account-management log or local report file from here. Put the dated log entry, in the log's established format, at the end of your final message so it can be pasted in by hand. The final message is the deliverable.
