# Routine: EGH Klaviyo cart metric watch (weekly)

Ported from the desktop task `egh-cart-flow-build`, reduced to what a cloud session can do: the Klaviyo metric check. Building the flow needs the Klaviyo UI in a browser and stays a desktop step, triggered by this routine's report. Cadence reduced from daily to weekly because the blocker is a dead Shopify pixel, not a waiting game.

Schedule: Mondays 15:00 UTC (08:00 Pacific during PDT). Model: claude-sonnet-5.

---

Check whether Emma Grace Home's Klaviyo account has an "Added to Cart" metric yet. You are running unattended in a cloud session with the Klaviyo connector only; no browser, no Shopify admin, no local files. READ-ONLY.

## The blocker, so you interpret correctly
As of 2026-08-10 the Klaviyo customer-events pixel in Shopify is dead and has been since June: Shopify shows "Klaviyo: Email Marketing & SMS" as inactive with an empty Data column, and its activity log shows access granted then paused for "No signals detected" repeatedly (Jun 2, 14, 26, 30, Jul 3). An attempt on 2026-08-10 to enable "Track behavioral events" in Klaviyo appeared to save and then reverted. The Klaviyo app embed on the storefront DOES work (window.klaviyo present); that is a different mechanism from the customer-events pixel and masked the dead pixel. Do not confuse the two.

## STEP 1
Use the Klaviyo connector get_metrics (EGH account Su6NaT, organization "Emma Grace Home"). Look for a metric named "Added to Cart". Also note whether ANY behavioral-event metric has appeared (for example "Searched Site"). As of 2026-08-10: 60 metrics, newest created 2026-07-06, none behavioral.

## STEP 2
If NOT there: report the metric count, the newest metric date, and how many days it has been since 2026-08-10. Do not build anything. Restate the escalation path: (1) repair the Klaviyo customer-events pixel in Shopify, which has flapped since June and likely needs the store owner and Klaviyo support; (2) manual onsite snippet per Klaviyo help article 115001396711; (3) most reliable given this history, server-side: the storefront already emits add_to_cart_stape through the sGTM container at data.emmagracehome.com, proven working for GA4 and Meta, so forward it to Klaviyo's Track API and sidestep the pixel.

If IT IS there: capture the metric ID and report it prominently. The flow is then built on the desktop, not here. Spec for that step, so it travels with the report: flow name "Added to Cart Reminder"; trigger the Added to Cart metric; flow filters Checkout Started zero times since starting this flow AND Placed Order zero times since starting this flow (prevents collision with the LIVE Abandoned Checkout flow T9A4iK); steps: 4h delay, email template Vm5Xhv subject "You left something in your cart", 20h delay, email template TmnyVH subject "Your cart is still waiting"; smart sending ON; EMAIL ONLY, no SMS; LEAVE IN DRAFT. Activation requires Conner's explicit approval.

## Hard constraints
Do not activate any flow. Do not touch Google Ads, ad settings, or the Text Messaging List opt-in setting.

## Output
Three lines: metric state, days since 2026-08-10, next action. Nothing else unless the metric appeared.
