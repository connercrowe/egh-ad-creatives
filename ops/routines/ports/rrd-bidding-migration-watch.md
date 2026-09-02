# Routine port: rrd-bidding-migration-watch
Source description: Daily check on Robert Russell Designs: has conversion tracking ever fired, and is the campaign ready to move from Maximize Clicks to Maximize Conversions.
Ported mechanically by port_task.py; review before creating the routine.

---
You are running unattended as a cloud Routine: a fresh clone of the google-ads-mcp repository is your working directory, PYTHONPATH=src and the Google Ads credentials are set as environment variables, and there is no browser and no access to Conner's desktop files. If `python -c "import google_ads_mcp"` fails or the credentials are missing, say so in one line as your entire report and stop. GOOGLE_ADS_ALLOW_WRITES is not set in the environment; a task that is permitted one write sets it inline on that command only, exactly as written below.

Check whether the Robert Russell Designs Google Ads campaign is ready to move off Maximize Clicks, and whether its conversion tracking is working at all.

Run this and report the output:

```
python rrd_bidding_migration_watch.py
```

Context you need (this run has no memory of the conversation that created it):

- Account 429-484-8443, MCC 472-708-8547, campaign 24106423096 "RRD | Search | Custom Dining | US".
- It launched 2026-08-05 on Maximize Clicks with a $3.25 max-CPC ceiling. Enhanced CPC is NOT available (Google sunset it for Search; the API returns OPERATION_NOT_PERMITTED_FOR_CONTEXT). Target CPA is also refused until conversion history exists. So the only fork is Maximize Clicks vs Maximize Conversions.
- The script only reports. It does NOT change bidding unless run with `--auto-switch --commit`. Never add those flags on your own; a bid-strategy change is a live-account write that needs Conner's explicit approval each time.

How to report:

1. If the script exits 3 (TRIGGER MET) — lead with that. Quote the conversion count, cost per lead, and the recommendation. Ask Conner whether to apply it. Do not apply it yourself.

2. If the gate "conversion tracking has EVER fired" is still unmet AND the campaign has now spent real money, that is the finding worth leading with, not the migration status. As of 2026-08-05 this account had recorded ZERO counted conversions in its entire history, and the campaign is live at a daily budget AdPulse moves on its own (read it from the output, do not assume; it was $64.52/day on 2026-08-10). Every day that passes with spend and no conversion is either lost leads or broken measurement. Flag it prominently and state how much has been spent with zero conversions.

   The two things that were still outstanding at setup time:
     - rob@robertrusselldesigns.com needed adding to the WhatConverts profile's lead-notification recipients (WhatConverts > profile > Settings > Notifications; not a code change, not in their v1 API)
     - one real submission through the live form at https://design.robertrusselldesigns.com/ to confirm the lead lands in WhatConverts, the email arrives, and a conversion records on action 7708330936

   Neither is confirmable from Google Ads data alone. Do NOT report either as done or likely-done on the strength of a clean-looking run. Report only what the output states.

   Read the "WhatConverts leads since launch" line to tell the two failure modes apart:
     - `N lead(s)` with N > 0 and still zero Google Ads conversions -> the form works and Rob is getting inquiries; what is broken is the wiring to conversion action 7708330936. Lead with that; it is a measurement bug, not lost leads.
     - `0 lead(s)` -> nothing has ever reached the profile. Either nobody has submitted, or the submission path is failing.
     - `UNKNOWN` -> the check is not configured or the API refused. Say so plainly and do not infer anything from it. To enable it, Conner creates a read-only key at WhatConverts > Robert Russell Designs profile > Integrations > API Keys and sets `RRD_WC_TOKEN` / `RRD_WC_SECRET` / `RRD_WC_PROFILE_ID` in `the environment variables (no .env file exists in the cloud)`. The landing page's own WhatConverts credentials live as Cloudflare Pages secrets and are write-only, so they cannot be reused here.

   The notification-recipient list is NOT exposed in the WhatConverts v1 API and never will be checkable by this script. It can only be confirmed in their UI.

3. If it is simply not ready yet and conversions are accruing normally, keep it to two or three lines: conversions so far against the threshold of 15, and the projected clicks needed.

Also sanity-check the landing page gate in the output. If "landing page still deployment-mode=production" is NOT met, treat that as urgent: it means the page regressed to preview mode, in which case the form silently stops submitting and every click is wasted. That exact failure has happened on this project before. Recommend pausing immediately with:

```
python rrd_emergency_pause.py --commit
```

Keep the report short. No preamble.

## Output rule for the cloud
You cannot append to any account-management log or local report file from here. Put the dated log entry, in the log's established format, at the end of your final message so it can be pasted in by hand. The final message is the deliverable.
