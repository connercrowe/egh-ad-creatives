# Routine port: cc-lead-conversion-reconcile
Source description: Daily lead reconciliation: verify lead emails recorded conversions, and upload the offline backstop conversion (gclid from the lead email) when consent suppressed the tag.
Ported mechanically by port_task.py; review before creating the routine.

---
You are running unattended as a cloud Routine: a fresh clone of the google-ads-mcp repository is your working directory, PYTHONPATH=src and the Google Ads credentials are set as environment variables, and there is no browser and no access to Conner's desktop files. If `python -c "import google_ads_mcp"` fails or the credentials are missing, say so in one line as your entire report and stop. GOOGLE_ADS_ALLOW_WRITES is not set in the environment; a task that is permitted one write sets it inline on that command only, exactly as written below.

Reconcile Conner Crowe's inbound leads against Google Ads conversions, and close the consent gap with an offline upload when needed. The ONLY permitted write is the offline click-conversion upload defined in Step 3 (pre-approved by Conner 2026-08-14). No other ad-account writes, no site changes, no email sends.

WHY THIS EXISTS
The lead path is: form submit -> generate_lead dataLayer event -> GTM tag 94 -> Google Ads conversion action 7707923469 "Form lead (all site forms)" (AW-17247064642 / oTbHCI2ottscEMKkhaBA). The site's consent banner gates the dataLayer push, so a visitor who declines or ignores it submits successfully and emails Conner but records NO conversion. Since 2026-08-14 every lead email from the three paid landers (/shopify-store-design/, /ecommerce-website-design/, /shopify-migration/) carries hidden gclid and attribution fields captured from the landing URL. That gclid is the backstop: it lets the missing conversion be uploaded offline, so the Conversions column stays complete without weakening consent.

STEP 1 - LEADS THAT ARRIVED (email)
Gmail search: from:notify@web3forms.com newer_than:3d
(3d not 2d: Gmail evaluates newer_than in local time while Ads reports account-timezone days; de-dupe by date rather than narrowing.)
Count genuine leads. EXCLUDE tests: subjects/bodies containing "IGNORE", "probe", "diag", "verify", "test", or a website_url ending in ".example", or sender email cscrowe30@gmail.com / hi@connercrowe.com. For each genuine lead, open the message body and extract: name, email, store URL, catalog_size, heard_from, and the gclid and attribution fields if present.

STEP 2 - CONVERSIONS RECORDED (Google Ads, read)
  stay in the repository root
  PYTHONPATH="src" python with build_client(load_config(), login_customer_id='4727088547'), customer 5294557080.
Pull for the same window: campaign 24096546152 clicks/cost/conversions, and account conversions segmented by segments.conversion_action_name and segments.date.

STEP 3 - THE BACKSTOP UPLOAD (the one permitted write)
For each genuine lead whose email carries a NON-EMPTY gclid AND for which no "Form lead (all site forms)" or "Form lead (offline backstop)" conversion is recorded on the lead's date (or the day either side, timezone slack):
1. Upload an offline click conversion via ConversionUploadService.upload_click_conversions:
   - conversion_action: customers/5294557080/conversionActions/7721104001 ("Form lead (offline backstop)", UPLOAD_CLICKS, primary, $100 default)
   - gclid: from the email; conversion_date_time: the email's arrival time in account timezone formatted "yyyy-MM-dd HH:mm:ss-07:00" (America/Los_Angeles offset current at that date)
   - partial_failure=True; surface any partial_failure_error verbatim.
2. NEVER upload when a same-day online conversion already exists (that is the double-count guard - check first, always).
3. NEVER upload for a lead without a gclid (organic/direct leads have no click to attribute).
4. Log each upload to the repository root (your working directory)/_reports/cc_oci_uploads.log (date | lead email | gclid prefix 12 chars | result) and append a line to audit.log in the same folder.
Note: gclids expire for upload after 90 days, and same-day uploads can be rejected if the click is too recent - if the API answers CLICK_NOT_FOUND or TOO_RECENT_CONVERSION, retry on the next daily run (keep a pending marker in the log) rather than dropping it.

STEP 4 - REPORT
Open with one line: MATCHED, GAP CLOSED (uploaded N), GAP (unresolvable - explain), or NO ACTIVITY.
- A lead email with a gclid and no conversion that this task then uploads is the system working; say so in one line, not as an alarm.
- A lead email with NO gclid and no conversion means an organic/direct lead OR the capture fields failed; check whether the email shows the gclid field at all (present-but-empty = organic; absent entirely = the form fields regressed, which IS an alarm).
- Zero emails and zero clicks: NO ACTIVITY in two lines, stop.
- Any genuine lead at all: say so loudly at the top; also report its heard_from answer - that field settles attribution questions (especially AI/ChatGPT claims).
State plainly if Gmail or the ads MCP is unavailable rather than reporting a false zero. A tool failure and a genuine zero must never look the same.

TONE
Conner is an experienced paid-search operator. Lead with the numbers, no preamble, no filler. Three lines is a fine report on a quiet day.

## Output rule for the cloud
You cannot append to any account-management log or local report file from here. Put the dated log entry, in the log's established format, at the end of your final message so it can be pasted in by hand. The final message is the deliverable.
