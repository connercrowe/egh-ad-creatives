# Routine: EGH Meta tracking health (daily)

Ported from the desktop task `egh-meta-tracking-health`. Changes from the desktop version: runs unattended in a cloud session with the Meta Ads and Klaviyo connectors; the local intel-log append and rotation script are replaced by the final message; the sanctioned browser cart test is out of reach and is listed as an escalation for Conner. Everything else is verbatim.

Schedule: daily 15:00 UTC (08:00 Pacific during PDT). Model: claude-sonnet-5.

---

Run the daily Emma Grace Home (EGH) Meta tracking-health check. You start with NO memory of prior conversations and you are running unattended in a cloud session with no repository and no browser. Everything you need is below. Tools: the Meta Ads connector (ads_get_dataset_stats, ads_get_ad_entities) and the Klaviyo connector (query_metric_aggregates). Load them via ToolSearch first.

READ-ONLY. Make no changes to the ad account, GTM, Shopify, or Klaviyo. Report problems; do not fix them.

## BACKGROUND
On 2026-08-04 at 15:49:10 PDT (unix 1785883750) a change went live in EGH's GTM web container adding event_id to the GA4 shared event settings. Forensics on 2026-08-05 established that this change improved the GA4 / Google Ads path only. Meta's dedup path was already wired and never reads that variable, so the Meta ratio is NOT expected to move because of it. The ~4.7-5.4x Meta Purchase inflation has NO established cause. Treat it as an open diagnosis.

RESOLVED 2026-08-12 by controlled runtime test (3 add-to-cart clicks produced AddToCart = 9: WEB 3 / SERVER 6): every conversion action produces 1 browser + 2 server copies. Shopify native Meta sends a browser copy and a server copy; the Stape CAPIG at capig.stape.vip adds a third, redundant server copy. GTM sends Meta NOTHING (all Meta tags in both containers have empty firing triggers). The transport is HEALTHY: a zero bucket means no real user action, not broken tracking.

THE ONE OPEN QUESTION: do all three copies carry the same event_id? Same id means the duplication is cosmetic; divergent ids mean genuine 3x inflation. ads_get_dataset_stats returns counts, not event IDs, so this is NOT answerable from this routine. Report the shape; escalate the ID question.

SEPARATE LIVE REGRESSION, Google Ads not Meta: Consent Mode v2 defaults to denied, the Data Tags are consent-gated, live storefront shows gcs=G100, so Google Ads server-side conversions are suppressed for every non-consenting visitor. Mention it once per report as a standing item.

TREAT THE 4.7-5.4x BASELINE AS SUSPECT: historical ATC peaks are burst-shaped (Aug 10 15:00 = 18 WEB/36 SERVER in one hour) and Clarity logged 860 bot sessions on Aug 11. Some "inflation" may be non-human traffic.

MEASURED PRE-FIX BASELINE (2026-07-28 to 2026-08-04): Meta Purchase 38 vs 7 real Klaviyo orders = ~5.4x (an earlier pull read 33/7 = 4.7x; treat 4.7-5.4x as the band). AddToCart 626, InitiateCheckout 82.

## WINDOWING RULE
Compute BOTH: (1) trailing 7-day window, the trend metric; (2) POST-FIX-ONLY window from unix 1785883750 to now, Klaviyo filter 2026-08-04T15:49:10. Meta echoes the resolved start_time back; it should read 2026-08-04T15:49:10-0700. Judge the verdict on the post-fix window and state how many days of post-fix data exist.

KNOWN ARTIFACT, do not re-flag: on 2026-08-04 15:49-16:00 PDT the dataset logged 5 WEB_ONLY Purchases and 0 SERVER_ONLY against zero real orders (republish re-fire). They sit in the 2026-08-04T15:00:00-0700 bucket inside the post-fix window. Subtract them by hand from every Purchase count until Aug 4 ages out of Meta's 28-day lookback (about 2026-09-01). If the post-fix window no longer reaches back to Aug 4, say so and stop subtracting. If a similar single-hour burst appears right after any future container publish, treat it the same way.

Timebase mismatch: ads_get_dataset_stats buckets by receipt time; Klaviyo buckets by event time. CAPI retries can land an older order in today's Meta bucket. Check timestamps before calling anything phantom.

## KEY IDS
Meta ad account 868029352962275, dataset/pixel 1684971312527785. Klaviyo Placed Order XYBXeB, Checkout Started XmAUBY, Ordered Product SBkiHa, Fulfilled Order TLK9B2, Viewed Product XTYGTd. Campaigns: C1 Cold 120247802557810101, C2 Retargeting 120247802577370101, C3 Catalog DPA 120248189720690101.

## STEPS
1. Meta events, BOTH windows: ads_get_dataset_stats, dataset_id 1684971312527785, aggregation "event_total_counts". Events arrive in multiple parallel streams; SUM all rows per event name. Record Purchase, AddToCart, InitiateCheckout.
2. WEB vs SERVER split on Purchase, post-fix window, EVERY run: two calls with start_time 1785883750, aggregation "event" (the event_source filter is ignored otherwise), event_name "Purchase", once with event_source "WEB_ONLY" and once "SERVER_ONLY". Record both counts AND the hourly bucket timestamps. Repeat for AddToCart when Purchase volume is too thin to read (it usually is).
3. Real orders, BOTH windows: Klaviyo query_metric_aggregates on XYBXeB, measurements ["count","sum_value"], interval day, timezone America/Los_Angeles. Also pull XmAUBY. If Placed Order is ZERO for a day, do NOT conclude Klaviyo is broken: EGH runs ~1 order/day. Cross-check siblings SBkiHa, TLK9B2, XTYGTd; non-zero Fulfilled/Viewed alongside zero Placed Order means the zero is REAL. This false alarm was raised and cleared on 2026-08-05.
4. Ratio = Meta Purchase events / real Klaviyo orders, per window, against the 4.7-5.4x band. If the denominator is 0 the ratio is uncomputable; say so and judge on the split instead. Never report a ratio against zero.
5. Meta's REPORTED conversions: ads_get_ad_entities, level campaign, date_preset "last_7d", fields daily_budget, amount_spent, ctr, cpm, omni_add_to_cart, cost_per_omni_add_to_cart, omni_initiated_checkout, actions:omni_purchase. This matters MORE than raw received events; reported conversions feed bidding and AdPulse.
6. AdPulse budget drift: report the C1/C2/C3 daily_budget split from step 5. AdPulse rewrites these nightly around 03:03 against a ~$3,000/month target. Flag any single-campaign swing above 30% versus the split you see in the most recent previous run if it is available to you; otherwise report the split as the baseline. Do NOT change budgets; AdPulse owns them.

## HOW TO READ THE WEB/SERVER SPLIT
On a real order both senders fire with the SAME event_id and Meta counts ONE. WEB ≈ SERVER ≈ real orders: dedup working. WEB ≈ SERVER but both ≈ 2x orders: a third sender duplicates both. WEB >> SERVER: browser pixel firing on events CAPI never saw (second browser sender or re-firing tag). SERVER >> WEB: ragged non-integer excess is blocked browser events, normal; a clean integer multiple holding across buckets of different sizes (4/8, 6/12, 2/4) is a mechanical duplicate server-side sender, a DEFECT. Either side with no real orders behind it: check bucket timestamps; events clustered in one hour that coincides with a GTM publish are a deployment artifact.

## HOW TO INTERPRET (post-fix window)
PASS: ratio toward ~1x. PARTIAL: ratio near ~2x, a third sender remains; prime suspect is Shopify's native Facebook & Instagram sales-channel pixel (domain cweied-ny.myshopify.com sending since 2026-06-04), which is a BROWSER sender and shows as WEB materially above SERVER. FAIL / NO CHANGE is the EXPECTED result: the Aug 4 change never touched Meta's dedup path. Do not keep re-reporting PROVISIONAL as though a fix is still landing. The open work is the event_id question, which needs GTM Preview or Events Manager Test Events in a browser; list it as the escalation for Conner.

## CAVEATS
Cost-per-result roughly DOUBLING is the metric becoming CORRECT, not a regression; state this in every report. Meta ingestion lags up to 30 minutes and hourly buckets do not exist until the hour closes; never trust the current partial hour. EGH does ~1 order/day; prefer multi-day windows; AddToCart (~80/day) corroborates sooner. C3 runs attribution 1d_view_7d_click_1d_ev while C1/C2 run 7d_click, so C3's cost-per-result is not comparable. EGH's Shopify Admin token CANNOT read orders; do not try; Klaviyo is the only programmatic order ground truth. The controlled cart test (load a product page, add to cart, confirm capig.stape.vip/events returns 200, clear the cart) needs a browser and is not available in this session; recommend it to Conner when a bucket reads zero and the sibling checks do not resolve it.

## OUTPUT
A short report (at most 12 lines) as your final message: post-fix ratio and days of post-fix data, the WEB vs SERVER Purchase split with its hour buckets, trailing-7d ratio, verdict (PASS / PARTIAL / FAIL), reported conversions and cost-per-ATC by campaign, the C1/C2/C3 budget split, and the recommended next action. Format the numbers so the entry can be pasted into the account-management log by hand; you cannot write that log from here.
