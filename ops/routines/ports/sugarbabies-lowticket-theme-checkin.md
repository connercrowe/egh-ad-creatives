# Routine port: sugarbabies-lowticket-theme-checkin
Source description: Weekly check-in on the SugarBabies Low Ticket PMax search-theme rebuild (applied 2026-07-29): catch disapprovals, track ROAS vs frozen baseline, watch Diaper Bags feed recovery.
Ported mechanically by port_task.py; review before creating the routine.

BLOCKERS (paths that do not exist in the cloud; give each a repo home or drop the step):
  - C:/Users/Admin/Projects/sugarbabies/_intel/lowticket-search-themes
  - C:/Users/Admin/Projects/sugarbabies/_intel/lowticket-search-themes/RUNBOOK.md

---
You are running unattended as a cloud Routine: a fresh clone of the google-ads-mcp repository is your working directory, PYTHONPATH=src and the Google Ads credentials are set as environment variables, and there is no browser and no access to Conner's desktop files. If `python -c "import google_ads_mcp"` fails or the credentials are missing, say so in one line as your entire report and stop. GOOGLE_ADS_ALLOW_WRITES is not set in the environment; a task that is permitted one write sets it inline on that command only, exactly as written below.

Weekly check-in on the SugarBabies Low Ticket PMax search-theme rebuild applied 2026-07-29 (206 themes, 7 asset groups, campaign `US | PMax | Low Ticket` 22910863662, account 3904628695).

## Run this first (READ ONLY)

```
cd C:/Users/Admin/Projects/sugarbabies/_intel/lowticket-search-themes
python checkin.py
```

It compares against a frozen pre-change baseline (30d: ROAS 3.43, cost $4,550.12, 38.7 conv, $15,584.77 value) and reports:

1. **Theme health** — live count vs the intended 206, plus any theme that came back DISAPPROVED.
2. **Performance** — last 30d vs baseline. It self-suppresses with "TOO EARLY" until 14 days post-rebuild; PMax needs ~2 weeks to settle after a signal change. Read nothing into movement before then.
3. **Group health** — every asset group's serving status and primary_status, including Diaper Bags (LIMITED as of 2026-07-29).

Each run also writes a dated snapshot to `snapshots/YYYY-MM-DD.json` (theme counts per group, group statuses, 30d perf, feed counts). Google's `change_event` API logs **neither** ASSET_GROUP nor ASSET_GROUP_SIGNAL edits, so these snapshots are the only way to date a future change. When drift appears, diff the last two snapshots first.

## Escalate to Conner ONLY if

**The script decides this for you.** It ends with either `!! ESCALATE TO CONNER — N issue(s)` and a bullet per issue, or `NO ESCALATION`. Trust that block; do not re-derive the verdict from the sections above it. The triggers it enforces:

- any theme not APPROVED, or
- live theme count != 206 (drift — fix with `python apply_themes.py --execute`, which is idempotent), or
- **any asset group not ENABLED, or a group missing / newly appeared**, or
- 14+ days have passed and it prints DEGRADED.

Read the whole output anyway. On 2026-08-04 the `All Products $150 - $500` group — ~80% of campaign spend, 456 of ~470 products — was found PAUSED, and the original three-trigger contract would have let that pass silently. That is why the asset-group trigger now exists. If something material shows up that no trigger covers, escalate it and say so.

**Otherwise stay quiet.** A flat or improving week needs no message. Do not send a "nothing to report" ping.

If DEGRADED after 14+ days, diagnose before alarming: did spend shift between asset groups, did High Ticket cannibalise, did anything else change that week? Report the likely cause, not just the number.

## Context — carry this, do not re-derive it

- Four groups are deliberately UNDER 50 themes (Car Seat Base 10, Travel Bags 16, Mattresses 24, Carriers 28) because their listing filters admit only 1–5 products. Intentional, not drift. Only a change in the **total (206)** signals a problem.
- **NEVER report on out-of-stock, feed availability, or NOT_ELIGIBLE counts.** Per Conner 2026-08-04: what is out of stock is out of stock on purpose. What is in stock is in stock, and that is the whole story. This is not a problem to solve, a metric to trend, or a cause to cite when diagnosing performance. Do not raise it, do not work around it, do not bring it back as "context."
- Diaper Bags being LIMITED is a stock condition, **not** a content policy — so it is expected and permanently quiet. The "dating and companionship" flag belongs to an unlinked Google Business Profile LOCATION asset (id 109240774865). See memory note `project_sugarbabies_diaper_bags_policy_flag`. Do not re-diagnose from scratch.
- One item is owed to Andrew, not Claude's to fix: appealing that GBP LOCATION asset.
- **NEVER touch the IL campaigns** (24006003345, 24010832369). Hard rule.
- No live writes without Conner's explicit approval; note that the auto-mode classifier refuses live Google Ads mutates anyway, so Conner runs any fix command himself.

## Housekeeping

Once themes have been stable and approved ~4 consecutive weeks and ROAS has a clear verdict, propose downgrading this to monthly or retiring it — say so in the run output rather than running weekly forever.

Runbook: `C:/Users/Admin/Projects/sugarbabies/_intel/lowticket-search-themes/RUNBOOK.md`. Memory: `project_sugarbabies_pmax_search_themes`.

## Output rule for the cloud
You cannot append to any account-management log or local report file from here. Put the dated log entry, in the log's established format, at the end of your final message so it can be pasted in by hand. The final message is the deliverable.
