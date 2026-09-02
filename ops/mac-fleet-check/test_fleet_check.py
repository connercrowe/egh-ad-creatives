"""Run: /usr/bin/python3 -m unittest test_fleet_check.py  (stdlib only, no pytest needed)."""
import os
import plistlib
import tempfile
import time
import unittest
from pathlib import Path

import fleet_check as fc

NOW = time.time()


def write_plist(d, label, **keys):
    pl = {"Label": label, "ProgramArguments": ["/bin/true"]}
    pl.update(keys)
    p = Path(d) / (label + ".plist")
    with p.open("wb") as fh:
        plistlib.dump(pl, fh)
    return p


def touch(path, hours_ago):
    Path(path).write_text("x")
    t = NOW - hours_ago * 3600
    os.utime(path, (t, t))


class IntervalTests(unittest.TestCase):
    def test_daily(self):
        self.assertEqual(fc.expected_interval_hours({"StartCalendarInterval": {"Hour": 9, "Minute": 0}}), 24)

    def test_weekdays_mon_to_fri_gap_is_weekend(self):
        sci = [{"Weekday": d, "Hour": 20, "Minute": 0} for d in (1, 2, 3, 4, 5)]
        self.assertEqual(fc.expected_interval_hours({"StartCalendarInterval": sci}), 72)

    def test_three_times_a_day(self):
        sci = [{"Hour": h, "Minute": 0} for h in (7, 13, 19)]
        self.assertEqual(fc.expected_interval_hours({"StartCalendarInterval": sci}), 12)

    def test_weekly_monday(self):
        self.assertEqual(fc.expected_interval_hours({"StartCalendarInterval": {"Weekday": 1, "Hour": 7}}), 168)

    def test_monthly_first(self):
        self.assertEqual(fc.expected_interval_hours({"StartCalendarInterval": {"Day": 1, "Hour": 6}}), 744)

    def test_start_interval_seconds(self):
        self.assertEqual(fc.expected_interval_hours({"StartInterval": 3600}), 1)

    def test_minute_only_is_hourly(self):
        self.assertEqual(fc.expected_interval_hours({"StartCalendarInterval": {"Minute": 15}}), 1)

    def test_keepalive_is_service(self):
        self.assertEqual(fc.job_kind({"KeepAlive": True}), "service")
        self.assertEqual(fc.job_kind({"RunAtLoad": True}), "on-demand")


class LaunchctlParseTests(unittest.TestCase):
    def test_parse(self):
        text = "PID\tStatus\tLabel\n-\t0\tcom.conner.a\n123\t0\tai.openclaw.gateway\n-\t1\tcom.conner.b\n"
        jobs = fc.parse_launchctl(text)
        self.assertEqual(jobs["com.conner.a"], (None, 0))
        self.assertEqual(jobs["ai.openclaw.gateway"], (123, 0))
        self.assertEqual(jobs["com.conner.b"], (None, 1))


class AssessTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.logs = tempfile.mkdtemp()

    def _log(self, name):
        return str(Path(self.logs) / name)

    def run_assess(self, loaded, cfg=None):
        cfg = cfg or dict(fc.DEFAULT_CONFIG)
        entries = fc.read_plists(self.d)
        return {r["label"]: r for r in fc.assess(entries, loaded, cfg, NOW)}

    def test_ok_daily_job(self):
        lp = self._log("a.log"); touch(lp, 20)
        write_plist(self.d, "com.conner.a", StartCalendarInterval={"Hour": 9}, StandardOutPath=lp)
        rows = self.run_assess({"com.conner.a": (None, 0)})
        self.assertEqual(rows["com.conner.a"]["status"], "OK")

    def test_not_loaded_is_the_ezpanl_class(self):
        lp = self._log("r.log"); touch(lp, 5)
        write_plist(self.d, "com.connercrowe.ezpanl-report", StartCalendarInterval={"Weekday": 1, "Hour": 7}, StandardOutPath=lp)
        rows = self.run_assess({})
        self.assertEqual(rows["com.connercrowe.ezpanl-report"]["status"], "NOT_LOADED")

    def test_expected_unloaded_is_not_an_issue(self):
        write_plist(self.d, "com.connercrowe.ezpanl-report", StartCalendarInterval={"Weekday": 1, "Hour": 7})
        cfg = dict(fc.DEFAULT_CONFIG); cfg["expected_unloaded"] = ["com.connercrowe.ezpanl-report"]
        rows = self.run_assess({}, cfg)
        self.assertEqual(rows["com.connercrowe.ezpanl-report"]["status"], "UNLOADED_BY_DESIGN")
        self.assertEqual(fc.summarize(list(rows.values())), [])

    def test_stale_weekday_job_on_monday_morning_is_fine(self):
        lp = self._log("cs.log"); touch(lp, 62)  # Fri 20:00 -> Mon 10:00
        sci = [{"Weekday": d, "Hour": 20} for d in (1, 2, 3, 4, 5)]
        write_plist(self.d, "com.conner.callscorer", StartCalendarInterval=sci, StandardOutPath=lp)
        rows = self.run_assess({"com.conner.callscorer": (None, 0)})
        self.assertEqual(rows["com.conner.callscorer"]["status"], "OK")

    def test_stale_daily_job(self):
        lp = self._log("s.log"); touch(lp, 60)
        write_plist(self.d, "com.conner.s", StartCalendarInterval={"Hour": 9}, StandardOutPath=lp)
        rows = self.run_assess({"com.conner.s": (None, 0)})
        self.assertEqual(rows["com.conner.s"]["status"], "STALE")

    def test_failed_exit(self):
        lp = self._log("f.log"); touch(lp, 1)
        write_plist(self.d, "com.conner.f", StartCalendarInterval={"Hour": 9}, StandardOutPath=lp)
        rows = self.run_assess({"com.conner.f": (None, 3)})
        self.assertEqual(rows["com.conner.f"]["status"], "FAILED")

    def test_no_log_path(self):
        write_plist(self.d, "com.conner.n", StartCalendarInterval={"Hour": 9})
        rows = self.run_assess({"com.conner.n": (None, 0)})
        self.assertEqual(rows["com.conner.n"]["status"], "NO_LOG")

    def test_skip_log_override(self):
        write_plist(self.d, "com.conner.roger-healthcheck", StartInterval=300)
        cfg = dict(fc.DEFAULT_CONFIG); cfg["overrides"] = {"com.conner.roger-healthcheck": {"skip_log": True}}
        rows = self.run_assess({"com.conner.roger-healthcheck": (None, 0)}, cfg)
        self.assertEqual(rows["com.conner.roger-healthcheck"]["status"], "OK")

    def test_service_not_running(self):
        write_plist(self.d, "ai.openclaw.gateway", KeepAlive=True)
        rows = self.run_assess({"ai.openclaw.gateway": (None, 78)})
        self.assertEqual(rows["ai.openclaw.gateway"]["status"], "NOT_RUNNING")

    def test_service_running(self):
        write_plist(self.d, "ai.openclaw.gateway", KeepAlive=True)
        rows = self.run_assess({"ai.openclaw.gateway": (4242, 0)})
        self.assertEqual(rows["ai.openclaw.gateway"]["status"], "OK")

    def test_foreign_plists_ignored_and_self_skipped(self):
        write_plist(self.d, "com.apple.something", StartCalendarInterval={"Hour": 1})
        write_plist(self.d, fc.SELF_LABEL, StartCalendarInterval={"Hour": 10})
        rows = self.run_assess({})
        self.assertEqual(rows, {})

    def test_broken_plist(self):
        Path(self.d, "com.conner.bad.plist").write_bytes(b"not a plist")
        rows = self.run_assess({})
        self.assertEqual(rows["com.conner.bad"]["status"], "BROKEN_PLIST")


class ScheduleAwareTests(unittest.TestCase):
    """Weeknight 20:00 job (Mon-Fri) checked at 10:30 the next morning."""
    SCI = [{"Weekday": d, "Hour": 20, "Minute": 0} for d in (1, 2, 3, 4, 5)]

    @staticmethod
    def _at(weekday_py, hour, minute=30):
        # a fixed reference week: Mon 2026-09-07
        import datetime as dt
        base = dt.datetime(2026, 9, 7, 0, 0)
        return (base + dt.timedelta(days=weekday_py, hours=hour, minutes=minute)).timestamp()

    def test_last_fire_tuesday_morning_is_monday_night(self):
        now = self._at(1, 10)  # Tue 10:30
        lf = fc.last_scheduled_fire({"StartCalendarInterval": self.SCI}, now)
        self.assertEqual(fc.datetime.fromtimestamp(lf).strftime("%a %H:%M"), "Mon 20:00")

    def test_last_fire_monday_morning_is_friday_night(self):
        now = self._at(0, 10)  # Mon 10:30
        lf = fc.last_scheduled_fire({"StartCalendarInterval": self.SCI}, now)
        self.assertEqual(fc.datetime.fromtimestamp(lf).strftime("%a %H:%M"), "Fri 20:00")

    def test_hourly_minute_only(self):
        now = self._at(2, 14, 50)
        lf = fc.last_scheduled_fire({"StartCalendarInterval": {"Minute": 15}}, now)
        self.assertEqual(fc.datetime.fromtimestamp(lf).strftime("%a %H:%M"), "Wed 14:15")

    def test_monthly_and_interval_fall_back(self):
        self.assertIsNone(fc.last_scheduled_fire({"StartCalendarInterval": {"Day": 1, "Hour": 6}}, self._at(1, 10)))
        self.assertIsNone(fc.last_scheduled_fire({"StartInterval": 300}, self._at(1, 10)))

    def _assess_with_log_age(self, now, log_written_at):
        d = tempfile.mkdtemp(); lp = str(Path(d) / "cs.log")
        Path(lp).write_text("x"); os.utime(lp, (log_written_at, log_written_at))
        write_plist(d, "com.conner.callscorer", StartCalendarInterval=self.SCI, StandardOutPath=lp)
        rows = fc.assess(fc.read_plists(d), {"com.conner.callscorer": (None, 0)}, dict(fc.DEFAULT_CONFIG), now)
        return rows[0]

    def test_missed_monday_run_flagged_tuesday_morning(self):
        row = self._assess_with_log_age(now=self._at(1, 10), log_written_at=self._at(-3, 21))  # last write Fri 21:00
        self.assertEqual(row["status"], "STALE")
        self.assertIn("Mon 20:00", row["detail"])

    def test_monday_run_ok_tuesday_morning(self):
        row = self._assess_with_log_age(now=self._at(1, 10), log_written_at=self._at(0, 21))  # Mon 21:00
        self.assertEqual(row["status"], "OK")

    def test_weekend_gap_not_flagged_monday_morning(self):
        row = self._assess_with_log_age(now=self._at(0, 10), log_written_at=self._at(-3, 21))  # Fri 21:00
        self.assertEqual(row["status"], "OK")

    def test_within_grace_not_flagged(self):
        row = self._assess_with_log_age(now=self._at(1, 21, 0), log_written_at=self._at(0, 21))  # Tue 21:00, run due 20:00
        self.assertEqual(row["status"], "OK")


class CriticalTests(unittest.TestCase):
    def test_subject_and_telegram(self):
        rows = [{"label": "com.conner.callscorer", "status": "STALE", "detail": "no log write since Mon 20:00"},
                {"label": "com.conner.x", "status": "OK", "detail": ""}]
        cfg = {"critical_labels": ["com.conner.callscorer"], "telegram_notify": "/bin/echo"}
        self.assertEqual(fc.subject(rows, cfg), "[fleet-check] CRITICAL: STALE callscorer")
        self.assertTrue(fc.telegram_alert(cfg, rows))
        self.assertFalse(fc.telegram_alert({"critical_labels": []}, rows))


class RenderTests(unittest.TestCase):
    def test_subject_ok(self):
        rows = [{"label": "com.conner.a", "status": "OK"}]
        self.assertEqual(fc.subject(rows), "[fleet-check] OK, 1 jobs")

    def test_subject_issues(self):
        rows = [
            {"label": "com.connercrowe.ezpanl-report", "status": "NOT_LOADED"},
            {"label": "com.conner.sb-blog", "status": "STALE"},
        ]
        self.assertEqual(fc.subject(rows), "[fleet-check] 2 ISSUES: NOT_LOADED ezpanl-report, STALE sb-blog")


if __name__ == "__main__":
    unittest.main()
