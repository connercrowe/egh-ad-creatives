# Routine port: ezpanl-watchdog
Source description: Twice-daily EZpanl GOOGLE watchdog: ad-copy drift, claim compliance, auto-apply, search terms, spend
Ported mechanically by port_task.py; review before creating the routine.

BLOCKERS resolved 2026-09-02 by dropping the two desktop-file steps (per RUNBOOK C3):
  - C:/Users/Admin/Desktop/EZpanl-GTM/CLAIM_LIBRARY.md: the sync-the-PROHIBITED-dict
    chore stays on the desktop; the cloud prompt now only says the dict may lag the library.
  - C:/Users/Admin/Desktop/EZpanl-GTM/_intel/ezpanl/account-management-log.md: the
    append is replaced by the "Output rule for the cloud" section (paste-in log entry).

---
You are running unattended as a cloud Routine: a fresh clone of the google-ads-mcp repository is your working directory, PYTHONPATH=src and the Google Ads credentials are set as environment variables, and there is no browser and no access to Conner's desktop files. If `python -c "import google_ads_mcp"` fails or the credentials are missing, say so in one line as your entire report and stop. GOOGLE_ADS_ALLOW_WRITES is not set in the environment; a task that is permitted one write sets it inline on that command only, exactly as written below.

Run the EZpanl **Google Ads** watchdog. Google went live 2026-08-06 and is in its first weeks, so treat anything anomalous as worth surfacing.

⚠️ **SCOPE: Google only.** Meta is owned by the `ezpanl-meta-launch-watch` task (daily) and `ezpanl-weekly-readiness-sweep` (Wednesdays), which are more detailed than anything you would do here. **Do not check Meta. Do not duplicate their alerts.**

## Step 1 — run the watchdog

```
python scripts/ezpanl_watchdog.py
```

READ-ONLY, never mutates. Exit 0 = clean, 1 = AMBER, 2 = RED.

What it checks, in priority order:
1. **Ad copy diff** — hashes every live ad line and compares to the previous snapshot. ADDED text is RED: **if nobody on our side wrote it, Google auto-apply did.** This is the single highest-consequence check on the account.
2. **Claim compliance** — every live line re-scanned against the CLAIM_LIBRARY prohibitions.
3. **Auto-apply subscriptions** — must stay at zero.
4. **Eligibility + policy** — campaigns ELIGIBLE, ads APPROVED.
5. **Spend + CPC** — overdelivery past the 2x cap; CPC above the $0.90–$1.50 band.
6. **Search terms** — Christmas-decoration category, DIY/homeowner intent, solo-install queries, the other "EZ Panel" companies, job seekers.
7. **Conversions** — the primary conversion set must not change.
8. **Audiences** — remarketing lists must grow, never shrink.
9. **Structure** — new campaigns, budget changes, and whether archived campaign `24084078629` got enabled or its $1.00 budget raised.

## Step 2 — act on what it says

If the run is clean, say so in two lines. Do not pad.

**If there are RED findings, state plainly what you would do and ask before doing anything.** Never mutate the account from this task. This is a monitor, not an optimiser.

Two judgement calls worth making rather than just reporting:
- **New search terms** that are clearly wrong-buyer are worth proposing as negatives — but check them against the live keyword list first so a negative cannot block one of our own keywords. Token semantics: EXACT = equality, PHRASE = ordered subsequence, BROAD = all tokens present. Google does **not** apply close variants to negatives.
- **Zero impressions** in the first several days is normal for a near-zero-volume brand term. Do not raise it as a fault before day 5.

## Standing context

- Claim rules live in the EZpanl CLAIM_LIBRARY on Conner's desktop, which you cannot read from here. The watchdog's `PROHIBITED` pattern dict in `scripts/ezpanl_watchdog.py` is the cloud copy of those rules and may lag the library; if a live line looks like a claim the dict does not cover, flag it in the report so Conner can update the script.
- **Never propose solo-install / "one person" / "by yourself" / hands-free framing.** EZpanl's published safety guidance requires a minimum two-person crew, and a solo-install claim under EZpanl's name is what got the previous agency fired.
- The **Demand Test** (`24100553474`, $10/day) is a **learning** budget with a hard stop at 30 days or 150 clicks. Success = a clean search-terms report, **not** CPA. **Never recommend optimising it for efficiency or raising its budget on good early numbers** — that corrupts the experiment.
- Known-open, do not re-report as new: advertiser identity verification has not cleared (`customer_asset` = 0), and prohibited copy remains on the live storefront pending a Shopify write token.

## Output rule for the cloud
You cannot append to any account-management log or local report file from here. Put the dated log entry, in the log's established format, at the end of your final message so it can be pasted in by hand. The final message is the deliverable.
