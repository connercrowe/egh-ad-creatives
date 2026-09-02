# Desktop scheduled tasks: prune roster (step two)

Scope: the 38 Claude Code desktop scheduled tasks on the Windows box
(`~/.claude/scheduled-tasks/*/SKILL.md`). Their enabled state, cron
expressions, and run history live in the desktop app's task store, reachable
only through the scheduled-tasks MCP on that machine. This file is the
classification; the paste-ready prompt at the bottom executes it there.

Rule: **disable, never delete.** Every prompt and cron expression stays
intact. Re-enabling is a one-field change.

Known state caveat: the vault records all 19 active tasks disabled on
2026-08-17. Session history shows `ezpanl-watchdog`, `ezpanl-meta-launch-watch`
and `egh-labor-day-day2-delivery-check` firing on 2026-08-31 through 09-02, so
some were re-enabled since. Step one of the prompt below lists the live state
before anything changes.

## A. Disable now: expired one-offs (14)

| Task | Why it is done |
|---|---|
| `autoair-mockup-visit-check` | Pre-call check for a call in mid-August |
| `brandit-rsa-approval-recheck` | 24h recheck of RSAs enabled 2026-06-18 |
| `cc-shopify-ads-reach-check` | 48h check after the 2026-08-03 launch |
| `ecom-ad-group-search-terms-check` | 3-day check after the 2026-08-09 ad group launch |
| `egh-free-freight-day7-pulse` | Day 7 of a test started 2026-08-20; passed 08-27 |
| `egh-google-ads-cutover-check` | Day-21 verification from 2026-06-24; passed mid-July |
| `egh-labor-day-day2-delivery-check` | Day 2 of a 2026-08-25 launch; ran 08-27 and 08-31 |
| `ezpanl-budget-drift-check-2026-08-26` | Dated one-time check |
| `ezpanl-deck-analytics-check` | July deck-view check |
| `ezpanl-deck-analytics-check-monday` | Pre-call intel for a July call |
| `ezpanl-wednesday-regroup-prep` | Pre-call brief for 2026-07-22 |
| `greenacre-litigation-7day-review` | First-week review of a 2026-07-15 launch |
| `gsc-day14-crawl-check` | Due 2026-08-25, already missed while disabled |
| `higgsfield-trial-cancel-check` | Day 2 of a trial that started 2026-07-20 |

Confirm before disabling (1): `egh-geo-attribution-recheck`. Its prompt is a
one-time re-read after the 2026-08-10 lookback change but mentions a monthly
cadence. If it has produced its report, disable it. If it has never run, run
it once by hand, then disable.

## B. Leave alone: pending, time-bound (3)

| Task | Fires | Note |
|---|---|---|
| `egh-free-freight-day14-verdict` | 2026-09-03 | Keep/kill/extend verdict on the copy test. Read-only. Disable after it reports. |
| `egh-labor-day-price-revert` | 2026-09-08 | **Live Shopify write**: reverts five SKUs to full price. Must fire. Disable after it reports. |
| `refresh-microsoft-partner-badge-2027` | January 2027 | One-shot, far future. Leave enabled. |

## C. Keep: recurring (20)

Destination is decided in step four. Nothing here changes in step two.

**Live-money writes, Routines candidates (3):**
`cc-budget-guard` (daily 04:33, re-asserts $15/day), `cc-search-terms-daily`
(daily 08:15, tiered auto-negatives), `cc-lead-conversion-reconcile` (daily,
offline conversion upload).

**Read-only watchers, Routines candidates (10):**
`ezpanl-watchdog` (2x daily), `ezpanl-meta-launch-watch` (daily),
`ezpanl-weekly-readiness-sweep` (Wed), `egh-meta-tracking-health` (daily),
`rrd-bidding-migration-watch` (daily), `sugarbabies-lowticket-theme-checkin`
(weekly), `connercrowe-index-watch` (daily), `connercrowe-citation-remeasure`
(monthly), `cc-shopify-ads-weekly-review` (weekly), `egh-cart-flow-build`
(polls for a Klaviyo metric behind a pixel that has been dead since June;
consider disabling until the pixel is fixed, it can only report the blocker).

**Stays on the desktop (7):**
`brand-it-monthly-autopilot` (1st; Dropbox sign-in and Outlook drafts),
`linkedin-engagement` (daily, Chrome), `pre-call-briefs` (daily, vault via
memory-bridge), `gemini-notes-weekly-ingest` (Drive, vault, scp to the Mac),
`vault-health-weekly`, `vault-keeper-monthly`, `weekly-content-harvest`
(all write the vault through the bridge).

## Paste into Claude Code on the Windows desktop

```
Use the scheduled-tasks MCP. Make no other changes.

1. List every scheduled task with its enabled state, cron expression, and last run time. Show it as a table before touching anything.

2. DISABLE (do not delete, do not edit prompts or cron) exactly these 14:
autoair-mockup-visit-check, brandit-rsa-approval-recheck, cc-shopify-ads-reach-check, ecom-ad-group-search-terms-check, egh-free-freight-day7-pulse, egh-google-ads-cutover-check, egh-labor-day-day2-delivery-check, ezpanl-budget-drift-check-2026-08-26, ezpanl-deck-analytics-check, ezpanl-deck-analytics-check-monday, ezpanl-wednesday-regroup-prep, greenacre-litigation-7day-review, gsc-day14-crawl-check, higgsfield-trial-cancel-check.

3. For egh-geo-attribution-recheck: report whether it has ever completed a run. Do not change it; I will decide.

4. Do NOT touch: egh-free-freight-day14-verdict, egh-labor-day-price-revert, refresh-microsoft-partner-badge-2027, or any task not named in step 2.

5. Show the after table and confirm nothing was deleted.
```

## After 2026-09-08

Once `egh-labor-day-price-revert` has reported the five SKUs reverted and
`egh-free-freight-day14-verdict` has delivered its verdict, disable both the
same way. That brings the roster to 20 recurring tasks plus one far-future
one-shot.
