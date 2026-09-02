# Routine port: cc-budget-guard
Source description: Daily guard: re-assert $15.00/day on Conner's Lead Gen campaign budget after AdPulse's ~03:22 pacer write, until the AdPulse target is corrected.
Ported mechanically by port_task.py; review before creating the routine.

---
You are running unattended as a cloud Routine: a fresh clone of the google-ads-mcp repository is your working directory, PYTHONPATH=src and the Google Ads credentials are set as environment variables, and there is no browser and no access to Conner's desktop files. If `python -c "import google_ads_mcp"` fails or the credentials are missing, say so in one line as your entire report and stop. GOOGLE_ADS_ALLOW_WRITES is not set in the environment; a task that is permitted one write sets it inline on that command only, exactly as written below.

Re-assert the approved daily budget on Conner Crowe's own Google Ads campaign. This task exists because AdPulse Responsive Pacing rewrites this budget every morning ~03:22 PT against a stale monthly target, and the strategy approved 2026-08-14 (full dissection, Conner's explicit sign-off) sets $15.00/day.

ACCOUNT: customer 5294557080, login/MCC 4727088547. Campaign "Lead Gen - Site Rebuilds - Search" id 24096546152, budget resource customers/5294557080/campaignBudgets/15770936107.

DO THIS:
1. Read the current budget:
   PYTHONPATH="src" python with build_client(load_config(), login_customer_id='4727088547'), query: SELECT campaign_budget.amount_micros FROM campaign WHERE campaign.id = 24096546152
2. If amount_micros == 15000000: report one line "budget already $15.00, no write" and stop.
3. Otherwise mutate it back to 15000000 via CampaignBudgetService (update mask amount_micros). This single write is pre-approved by Conner (2026-08-14) — it is the ONLY write this task may perform. Do not touch keywords, negatives, ad groups, or anything else.
4. Report one line: "corrected $X -> $15.00; AdPulse pacer still on stale target".

RETIREMENT CONDITION: the correct fix is in AdPulse (dashboard.adpulse.app -> Budgets/KPIs -> "Conner Crowe | Google" bdg_yg755gxpura5dgqthyq2liuvpa): August 2026 schedule Budget Target should be $665 (was $1,000); the Future monthly schedule of $500 from 2026-09-01 already exists and is fine. Once two consecutive runs report "no write" after Conner edits AdPulse, tell Conner this task can be deleted.

If the campaign or budget resource is missing, or any API error occurs, report the error verbatim and make no other changes.

## Output rule for the cloud
You cannot append to any account-management log or local report file from here. Put the dated log entry, in the log's established format, at the end of your final message so it can be pasted in by hand. The final message is the deliverable.
