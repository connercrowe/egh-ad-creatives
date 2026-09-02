# Execution log: fleet re-tiering runbook

Executor: Claude Code on the Windows desktop, 2026-09-02. Appended after every step.

## 2026-09-02 A1 - get the branch
- Ran: repo was not cloned locally; `git clone https://github.com/connercrowe/egh-ad-creatives.git` into `C:\Users\Admin\Projects\egh-ad-creatives`, then fetch + checkout `claude/mac-mini-agent-optimization-7tut4s`.
- Verification: `git log --oneline -1` prints `10de29a Add executor brief for a desktop Claude Code session`. RUNBOOK.md, EXECUTE.md, PRUNE.md, PUSH.md, ROUTINE-ENV.md, DEPLOY.md, STEP5.md, CREATE.md read in full.
- Result: PASS

## 2026-09-02 Console settings
- Ran: opened platform.claude.com Billing (Chrome tools, already signed in). Spend limits section shows a monthly spend limit of $100 already set, $0.30 spent this period, resets Oct 1 2026, admin email notifications at $100/200/300/400/500. Left as is; no value was specified in the runbook and a cap already exists. Per-key cap: Console offers none, only the org-level limit.
- Ran: opened claude.ai/code/routines (signed in). Neither the routines list nor the New routine form displays a daily run cap. Recorded as "no cap shown"; one routine exists today (`connercrowe GEO batch (monthly)`).
- Result: PASS (cap present; run cap not displayed anywhere on the page)

## 2026-09-02 A2 - prune the desktop tasks
- Ran: `list_scheduled_tasks` before-table. The desktop task store (`AppData/Roaming/Claude/claude-code-sessions/.../scheduled-tasks.json`) registers 22 tasks, not 38. 16 SKILL.md folders on disk are not registered and therefore cannot fire: autoair-mockup-visit-check, brandit-rsa-approval-recheck, cc-shopify-ads-reach-check, ecom-ad-group-search-terms-check, egh-cart-flow-build, egh-free-freight-day14-verdict, egh-free-freight-day7-pulse, egh-geo-attribution-recheck, egh-google-ads-cutover-check, egh-meta-tracking-health, ezpanl-deck-analytics-check, ezpanl-deck-analytics-check-monday, ezpanl-wednesday-regroup-prep, greenacre-litigation-7day-review, higgsfield-trial-cancel-check, linkedin-engagement.
- Before state, enabled=true (4): ezpanl-meta-launch-watch, ezpanl-weekly-readiness-sweep, ezpanl-watchdog, egh-labor-day-price-revert. All other 18 registered tasks already disabled.
- Ran: `update_scheduled_task enabled=false` on the 3 of the 14 that are registered: gsc-day14-crawl-check, egh-labor-day-day2-delivery-check, ezpanl-budget-drift-check-2026-08-26 (each already disabled; call confirmed "updated: disabled"). The other 11 of the 14 are unregistered, so there is nothing to disable; none can fire.
- egh-geo-attribution-recheck: unregistered, no run record anywhere in the store. Never completed a run. Not changed.
- After-table: 22 registered, 4 enabled (the 3 EZpanl recurring watchers + egh-labor-day-price-revert), 18 disabled, 0 deleted. egh-labor-day-price-revert untouched (enabled, fires 2026-09-08 03:00 PT). refresh-microsoft-partner-badge-2027 untouched (registered but disabled, pre-existing state).
- FINDING for Conner: egh-free-freight-day14-verdict (due 2026-09-03) is NOT registered in the desktop store, so it will not fire on its own. Untouched per the runbook; needs a manual run or re-registration.
- Result: PASS (all 14 are inert: 3 disabled in the store, 11 never registered; nothing deleted)

## 2026-09-02 A3 - push google-ads-mcp to a private repo
- Section 1: helpers copied to `C:\Users\Admin\Projects\_push-tools\`.
- Section 2 pre-flight: no remote, branch `master`, HEAD `106f625`. Working tree was dirty (11 tracked files modified, incl. `src/`, `scripts/ezpanl_watchdog.py`, `.env.example`, two `profiles/*.json`; plus untracked `_reports/`, `_watchdog/snap-*`, two `*_STRESS_TEST_*.md`). Committed the tracked modifications as `856b3ec Snapshot tracked working-tree changes before first push`; untracked files were left untracked (all match the new ignore list).
- Section 3: template appended to `.gitignore`. `.env.bak-preclean-20260729122456` does not exist in the folder (nothing to move). The only `.bak` file present, `scripts/ezpanl_watchdog.py.bak-20260901`, was moved (not deleted) to `C:\Users\Admin\Projects\_secrets-parked\google-ads-mcp.scripts.ezpanl_watchdog.py.bak-20260901`. `git rm --cached` untracked 23 files: `.mcp.json` and 22 `profiles/*.json` (all still on disk). `ls-files` suspect check printed nothing. Committed as `b22acfa` and `a3cb2e4`.
- Deviation, recorded: the tree scan first exited 1 flagging `.env.example` as "secret-shaped" because the template's `.env.*` glob covers it and the scanner treats every ignored `.env*` file as a backup. `.env.example` is the committed placeholder template (no values; verified by scanning its content). Fix applied in `ops/google-ads-mcp-repo/`: `scan_secrets.py` now scans `.env.example` / `.env.sample` / `.env.template` content instead of flagging them, and the ignore template gained `!.env.example`. Same line added to the repo `.gitignore`. Helpers re-copied to `_push-tools`.
- Section 4 verification: `tree scan: clean` (exit 0) and `history scan: clean` (exit 0), both run against the final history (`a3cb2e4`).
- Section 5: `gh repo create connercrowe/google-ads-mcp --private` -> https://github.com/connercrowe/google-ads-mcp ; `git push -u origin master` -> new branch master. API: `private: true`, `visibility: private`, `default_branch: master`. Contents listing has no `.env`, `audit.log`, `profiles`, `rsa_drafts.json`, `.mcp.json`, `snippets`, `rec_scan`, `_reports`, or `greenacre_lp`.
- Note for Conner: one previously tracked file under `_watchdog/` (`ezpanl_proposed_negatives.json`, EZpanl proposed negatives, no secrets) shipped because the PUSH.md exclusion list does not name `_watchdog/`. Left as is; untrack and add `_watchdog/` to the ignore list if that should stay local too.
- Section 6: `.env` holds exactly six names: GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_LOGIN_CUSTOMER_ID, GOOGLE_ADS_ALLOW_WRITES. Recorded in ROUTINE-ENV.md section 1 (names only).
- Result: PASS

## 2026-09-02 A4 - ship steps one and five to the Mac
- Ran: `ssh macmini mkdir -p ...`, scp of fleet_check.py / fleet-check.json / test_fleet_check.py to `~/Projects/fleet-check/`, run-fleet-check.sh to `~/bin/`, com.conner.fleet-check.plist to `~/Library/LaunchAgents/`, six `roger-step5/*.sh` to `~/step5/`, then `chmod +x`.
- Verification: remote `ls -l` shows all 11 files with today's timestamp, scripts executable; md5 of fleet_check.py, run-fleet-check.sh, run-step5.sh identical on both machines (802005ee..., 33ca35ef..., 94fcc6fc...).
- Result: PASS

Section A complete. Committing and pushing the branch.

## 2026-09-02 B1 - fleet checker on the Mac
- Ran: `/usr/bin/python3 -m unittest test_fleet_check.py` -> `Ran 23 tests ... OK`.
- Deviation, recorded: first `~/bin/run-fleet-check.sh --no-send` failed with `bad interpreter: /bin/bash^M`. The Windows clone checks files out with CRLF, so every scp'd script carried CR. Fixed on the Mac with `sed -i '' 's/\r$//'` on all 11 copied files (re-verified: 0 CR bytes, shebang clean). Added `ops/.gitattributes` (`*.sh`, `*.plist`, `*.py`, `*.json` -> `eol=lf`) so future checkouts ship LF; committed as `3034f4f`.
- Discovery pass 1: 27 jobs scanned, 16 issues. 13 of them were config noise: jobs launched through `ops-brief/runner.sh` write `~/Library/Logs/<name>.log` while their plist `StandardOutPath` points at an empty `.out` file, `opswatchdog` writes `Projects/ops-watchdog/state/run.log`, and `sugarabies-report` logs to its `.err.log`. `com.connercrowe.ezpanl-report` was listed in `expected_unloaded` but is loaded and ran 2026-08-31, so it was removed from that list.
- `fleet-check.json` tuned (14 `log` overrides, 2 `skip_log`, 3 `expected_unloaded`), committed in `ops/mac-fleet-check/`, copied to `~/Projects/fleet-check/`.
- Discovery pass 2: 27 jobs scanned, 3 issues, all genuine: `com.conner.ops-brief` STALE (its `ops-brief.log` has been empty since 2026-06-09; the plist is loaded but the digest writes nothing), `com.conner.sb-pmax-report` NOT_LOADED (last log 2026-07-23), `com.connercrowe.brandit-monthly` NOT_LOADED (last ran 2026-08-01). Left visible on purpose; these are for Conner to confirm as parked or fix.
- Real send: `~/bin/run-fleet-check.sh` exit 0. Verification: Gmail thread `1a0633aba5b40f12` from ops@connercrowe.com to hi@connercrowe.com at 2026-09-02T17:46:27Z, subject `[fleet-check] 3 ISSUES: STALE ops-brief, NOT_LOADED sb-pmax-report, NOT_LOADED brandit-monthly`.
- Bootstrap: see next line.
