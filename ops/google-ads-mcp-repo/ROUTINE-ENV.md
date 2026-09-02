# Cloud environment for Google Ads Routines

Input to step four. One Claude Code cloud environment, shared by every Google
Ads Routine, built once at claude.ai/code/environments.

## 1. Environment variables (names only; values pasted in the UI)

Confirm the exact names from `.env` with the command in PUSH.md section 6.
The `google-ads` library's own loader expects these five; the package's
`config.py` may alias them.

```
GOOGLE_ADS_DEVELOPER_TOKEN
GOOGLE_ADS_CLIENT_ID
GOOGLE_ADS_CLIENT_SECRET
GOOGLE_ADS_REFRESH_TOKEN
GOOGLE_ADS_LOGIN_CUSTOMER_ID      # MCC 4727088547
PYTHONPATH=src
```

Confirmed 2026-09-02 (PUSH.md section 6, names only): the local `.env` holds
exactly six keys, the five above plus `GOOGLE_ADS_ALLOW_WRITES`. No aliasing;
the names match the library loader as written. `GOOGLE_ADS_ALLOW_WRITES` is
deliberately not carried into the environment (see below). The `.env.example`
also documents `RRD_WC_*` and `MICROSOFT_ADS_*` keys; neither set exists in the
live `.env` today, so neither goes into the environment.

Not set at the environment level, ever: `GOOGLE_ADS_ALLOW_WRITES`. The three
write tasks set it inline on the one command that writes, exactly as their
desktop prompts do today.

Environment variables are copied into the sandbox as a file readable by any
command, so the model can read them. That is the same exposure as the desktop
today. Anthropic's "API credentials" feature injects a key at the proxy so
Claude never sees it, but it targets HTTP header auth and does not fit OAuth
refresh tokens for the Google Ads gRPC client. Use plain environment variables
here and keep the developer token at Explorer or Basic access, which it is.

## 2. Network access

The default "Trusted" allowlist blocks arbitrary hosts and fails with
`403 host_not_allowed`. Set the environment to **Custom** and add:

```
googleads.googleapis.com
oauth2.googleapis.com
accounts.google.com
www.googleapis.com
```

Routines that also use the Gmail, Meta Ads, Shopify, or PostHog connectors
need nothing extra; connector traffic routes through Anthropic and bypasses
the allowlist.

## 3. Setup script

Runs on every session before the prompt. Pin to what the Mac runs.

```bash
pip install "google-ads==31.0.0" "fastmcp==3.3.1" python-dotenv
```

If the repo gains a `pyproject.toml` or `requirements.txt` later, replace the
line with `pip install -e .` or `pip install -r requirements.txt`.

## 4. Repository

`connercrowe/google-ads-mcp`, default branch. Routines clone fresh each run,
so anything a task writes to the checkout is discarded when the session ends.

Two things that matters for:

- **`audit.log`.** The write path appends every mutation to an append-only
  log in the repo folder. In a fresh clone that log is lost at session end.
  Before any write task moves to a Routine, point the audit log at a durable
  sink: commit it back on a dedicated branch at the end of the run, or write a
  one-line summary to the report instead. Decide this in step four, not by
  accident.
- **`profiles/` and `rsa_drafts.json`.** Excluded from the repo. The negatives
  autopilot (killed 2026-08-02) and the RSA recheck (expired) are the only
  consumers. Nothing moving to a Routine needs them.

## 5. Model

`claude-sonnet-5` for every scripted check. These tasks run a Python script
and interpret a table; they do not need Opus at a 1M window, which is what the
desktop tasks were burning against the weekly cap.

## 6. What a migrated task looks like

The desktop prompt bodies port almost verbatim. Replace every
`C:/Users/Admin/Projects/google-ads-mcp` with the checkout path (the repo
root is the working directory in a cloud session), drop the `cd`, and keep
`PYTHONPATH=src` from the environment. Example, from `cc-budget-guard`:

```
PYTHONPATH=src python -c "from google_ads_mcp.client import build_client; ..."
```

Tasks that read files from `C:/Users/Admin/Desktop/EZpanl-GTM/` or write
`_intel` logs need those files in a repo the Routine also clones. That is
the one real port cost, and it is listed per task in step four.
