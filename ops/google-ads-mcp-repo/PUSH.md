# google-ads-mcp: first push to a private repo (step three)

Goal: `github.com/connercrowe/google-ads-mcp`, private, so cloud Routines can
clone the package instead of depending on the Windows box. Source of truth
stays `C:\Users\Admin\Projects\google-ads-mcp` (already a local git repo,
branch `master`, no GitHub remote today).

What must not leave the machine: the four Google Ads credentials in `.env`,
the stale `.env.bak-preclean-20260729122456`, the append-only `audit.log`,
per-client search-term `profiles/`, `rsa_drafts.json`, and the client
landing-page and rollback dumps. The ignore list handles the future; the
history scan handles the past.

Everything below is Windows PowerShell 5.1, one line at a time. `gh` is
already authenticated as `connercrowe` with repo scope.

## 1. Stage the helper files

Fetch this branch into the egh-ad-creatives clone, then copy the two helpers
next to the repo (not inside it).

```powershell
git -C "C:\Users\Admin\Projects\egh-ad-creatives" fetch origin claude/mac-mini-agent-optimization-7tut4s
git -C "C:\Users\Admin\Projects\egh-ad-creatives" checkout claude/mac-mini-agent-optimization-7tut4s
New-Item -ItemType Directory -Force -Path "C:\Users\Admin\Projects\_push-tools"
Copy-Item "C:\Users\Admin\Projects\egh-ad-creatives\ops\google-ads-mcp-repo\scan_secrets.py" "C:\Users\Admin\Projects\_push-tools\scan_secrets.py"
Copy-Item "C:\Users\Admin\Projects\egh-ad-creatives\ops\google-ads-mcp-repo\gitignore.google-ads-mcp" "C:\Users\Admin\Projects\_push-tools\gitignore.google-ads-mcp"
```

## 2. Pre-flight

```powershell
git -C "C:\Users\Admin\Projects\google-ads-mcp" status --short
git -C "C:\Users\Admin\Projects\google-ads-mcp" remote -v
git -C "C:\Users\Admin\Projects\google-ads-mcp" log --oneline -5
```

Expect: no remote listed. If the working tree is dirty, commit or stash it
first; the push should carry only what is deliberately committed.

## 3. Ignore list and the stale secret backup

Append the template to the existing `.gitignore` (creates it if absent), then
move the secret backup out of the repo entirely. Ignoring it is not enough
because a future `git add -f` or a tool that reads the folder would still see it.

```powershell
Get-Content "C:\Users\Admin\Projects\_push-tools\gitignore.google-ads-mcp" | Add-Content "C:\Users\Admin\Projects\google-ads-mcp\.gitignore"
New-Item -ItemType Directory -Force -Path "C:\Users\Admin\Projects\_secrets-parked"
Move-Item "C:\Users\Admin\Projects\google-ads-mcp\.env.bak-preclean-20260729122456" "C:\Users\Admin\Projects\_secrets-parked\google-ads-mcp.env.bak-preclean-20260729122456"
git -C "C:\Users\Admin\Projects\google-ads-mcp" rm -r --cached --ignore-unmatch audit.log profiles rsa_drafts.json greenacre_lp norco_lp_repoint_rollback.json _reports rec_scan snippets .mcp.json
git -C "C:\Users\Admin\Projects\google-ads-mcp" status --short
```

The `rm --cached` line only untracks files that were already committed; it
does not delete them from disk. If it prints nothing, nothing was tracked.

## 4. Scan, twice

Working tree:

```powershell
python "C:\Users\Admin\Projects\_push-tools\scan_secrets.py" --tree "C:\Users\Admin\Projects\google-ads-mcp"
```

Full history:

```powershell
git -C "C:\Users\Admin\Projects\google-ads-mcp" log --all -p | python "C:\Users\Admin\Projects\_push-tools\scan_secrets.py" --stdin
```

Both must print `clean`. The scanner lists any secret-shaped file it skipped
so it can be moved out, and exits nonzero on any finding.

### 4a. Tree hit

Remove the value from the file, reference `.env` instead, commit, re-scan.

### 4b. History hit

Do not rewrite history in place and do not push `master`. Push a clean
snapshot instead; the full history stays on the machine.

```powershell
Set-Location "C:\Users\Admin\Projects\google-ads-mcp"
git checkout --orphan clean-main
git add -A
git -c user.name="Conner Crowe" -c user.email="hi@connercrowe.com" commit -m "Clean snapshot for hosted repo"
python "C:\Users\Admin\Projects\_push-tools\scan_secrets.py" --tree "C:\Users\Admin\Projects\google-ads-mcp"
```

Then in section 5 push `clean-main` as `main` instead of `master`.

## 5. Create the private repo and push

```powershell
gh repo create connercrowe/google-ads-mcp --private --description "Self-hosted Google Ads MCP + autopilot scripts"
git -C "C:\Users\Admin\Projects\google-ads-mcp" remote add origin https://github.com/connercrowe/google-ads-mcp.git
git -C "C:\Users\Admin\Projects\google-ads-mcp" push -u origin master
```

If you took the 4b path: `git -C "C:\Users\Admin\Projects\google-ads-mcp" push -u origin clean-main:main`.

Verify:

```powershell
gh repo view connercrowe/google-ads-mcp --json visibility,defaultBranchRef
gh api repos/connercrowe/google-ads-mcp/contents --jq ".[].name"
```

The listing must not show `.env`, `audit.log`, `profiles`, or `rsa_drafts.json`.

## 6. Record the environment variable names for Routines

The cloud environment needs the credential names, not values. Print them:

```powershell
Select-String -Path "C:\Users\Admin\Projects\google-ads-mcp\.env" -Pattern "^[A-Z_]+=" | ForEach-Object { ($_.Line -split "=")[0] }
```

Paste that list into `ROUTINE-ENV.md` section 1 (names only). Then commit the
file to this branch or keep it with the repo README.

## Not done in this step

- The Mac copy at `~/brand-it/google-ads-mcp` keeps running from its local
  files. Pointing it at the new remote with a read-only deploy key (same
  recipe as call-scorer and lead-engine) is optional and can wait.
- No Routine is created yet. That is step four; `ROUTINE-ENV.md` is its input.
- `GOOGLE_ADS_ALLOW_WRITES` stays off everywhere except inside the three
  write tasks, per run.
