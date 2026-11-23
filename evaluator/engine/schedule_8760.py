"""schedule_8760.py - the schedules of the two files as hourly series of a whole year, made by EnergyPlus (annotation, not in the score).

  Hourly(root, weather, timeout).compare(P, pairs)   P = the pairing (idf_pair); pairs = [(reference schedule name, candidate schedule name)]
      -> dict(status "done" | "not_run" | "failed", reason, hours, expanded, rows=[dict(reference, candidate, same, share, first_difference)])

When it is used: schedule_kvor.py compares the schedules by their meaning first (`idf_sched.profile`: 24 hours of each day type in each `Through:` period). Only the pairs of schedules that this comparison finds
DIFFERENT are sent here; a pair that is the same is not expanded. EnergyPlus then writes the hourly value of every schedule of each file for the same period of the same year with the same weather file
(`Output:Variable, *, Schedule Value, Hourly`), and the two series of a pair are compared hour by hour (the number tolerance of the engine, 1 %). This sees what the profile does not: a day type that does not
occur in a period, the weekday of the real calendar (the year of the run), the holidays and the daylight saving rule that the file writes.

How the run is made. For each file one EnergyPlus run of a small IDF (about 2 seconds): Version, SimulationControl without any sizing, Building, Timestep (4), one RunPeriod, and from the file
  - every Schedule:* and ScheduleTypeLimits object (a Schedule:File with a relative file name gets the absolute name, from the folder of its IDF),
  - every RunPeriodControl:SpecialDays and RunPeriodControl:DaylightSavingTime object.
The RunPeriod (begin and end date, begin / end year, weekday of the start day) is the one of the REFERENCE for both files, so that both are run over the same dates of the same year; the three rules of the file itself
(use of the weather file holidays, use of the weather file daylight saving period, weekend holiday rule) are the file's own. The weather file is the one of the case (EnergyPlus reads the holidays and the daylight
saving period of the weather file when the RunPeriod says so). The files are only read; the runs are made in temporary folders that are deleted afterwards.

Since 2026-11-21 (user decision) this comparison is the FINAL one for a pair that the comparison by day type finds different: the same series = the same schedule (all its keys are the same, `schedule_rescue.py`); different series = the result by day type stands. The series has the hours that EnergyPlus gives for the run period of the reference and the weather file (8,760 in a year of 365 days, 8,784 in a leap year when the weather file has the leap day); the two series of a pair are compared hour by hour whatever the length. Without an EnergyPlus program or a weather file the comparison is not applied and `note` says so.
"""
import csv
import os
import re
import shutil
import subprocess
import tempfile

import idf_run
import idf_values as V

TOL = 0.01
ABS_TOL = 1e-6
CLASSES = ("schedule:", "scheduletypelimits", "runperiodcontrol:specialdays", "runperiodcontrol:daylightsavingtime")


def _g(o, k):
    v = o["fields"].get(k)
    return None if V.is_blank(v) else str(v).strip()


def _run_period(ref_objs, own_objs):
    """The text of the RunPeriod: the dates of the reference, the rules of the file itself (None when the reference has no RunPeriod)."""
    r = next((o for o in ref_objs if o["cls"].lower() == "runperiod"), None)
    if r is None:
        return None
    me = next((o for o in own_objs if o["cls"].lower() == "runperiod"), r)
    f = lambda o, k, d="": _g(o, k) or d
    vals = ["rp", f(r, "begin_month", "1"), f(r, "begin_day_of_month", "1"), f(r, "begin_year"), f(r, "end_month", "12"), f(r, "end_day_of_month", "31"), f(r, "end_year"), f(r, "day_of_week_for_start_day"),
            f(me, "use_weather_file_holidays_and_special_days"), f(me, "use_weather_file_daylight_saving_period"), f(me, "apply_weekend_holiday_rule"), "Yes", "Yes", "No"]
    return "RunPeriod,\n  " + ",\n  ".join(vals) + ";"


def build_idf(ref_objs, own_objs, base_dir):
    rp = _run_period(ref_objs, own_objs)
    if rp is None:
        return None
    out = ["Version, 23.1;", "SimulationControl, No, No, No, No, Yes;", "Building, B, 0, Suburbs, 0.04, 0.4, FullExterior, 25, 6;", "GlobalGeometryRules, UpperLeftCorner, Counterclockwise, Relative;", "Timestep, 4;", rp]
    for o in own_objs:
        c = o["cls"].lower()
        if not c.startswith(CLASSES):
            continue
        vals = list(o["values"])
        if c == "schedule:file" and len(vals) > 2 and vals[2] and not os.path.isabs(vals[2]) and base_dir:
            vals[2] = os.path.abspath(os.path.join(base_dir, vals[2]))
        out.append(o["cls"] + ",\n  " + ",\n  ".join(vals) + ";")
    out.append("Output:Variable, *, Schedule Value, Hourly;")
    return "\n".join(out) + "\n"


def read_series(csv_path):
    """{lower case schedule name: [hourly values]} of the eplusout.csv of a run."""
    with open(csv_path, newline="", encoding="utf8", errors="replace") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        cols = {}
        for i, h in enumerate(head):
            m = re.match(r"^(.*):Schedule Value \[\]\(Hourly\)\s*$", h.strip())
            if m:
                cols[i] = m.group(1).lower()
        series = {n: [] for n in cols.values()}
        for row in rd:
            for i, n in cols.items():
                try:
                    series[n].append(float(row[i]))
                except (IndexError, ValueError):
                    series[n].append(float("nan"))
    return series


class Hourly:
    def __init__(self, root, weather, timeout=300, base_dirs=None):
        self.root, self.weather, self.timeout = root, weather, timeout
        self.base_dirs = base_dirs or {}

    def _run(self, text):
        exe = idf_run.exe_of(self.root) if self.root else None
        if exe is None:
            return None, "the energyplus program was not found (give --energyplus <installation folder>)"
        tmp = tempfile.mkdtemp(prefix="bemgen_s8760_")
        try:
            idf = os.path.join(tmp, "s.idf")
            open(idf, "w", encoding="utf8").write(text)
            try:
                r = subprocess.run([exe, "-w", os.path.abspath(self.weather), "-r", "-d", tmp, idf], cwd=tmp, capture_output=True, text=True, timeout=self.timeout, errors="replace")
            except subprocess.TimeoutExpired:
                return None, "EnergyPlus did not end in %d s" % self.timeout
            ep = os.path.join(tmp, "eplusout.err")
            err = open(ep, encoding="utf8", errors="replace").read() if os.path.isfile(ep) else ""
            sev, fat, _, done = idf_run.count_err(err)
            cp = os.path.join(tmp, "eplusout.csv")
            if not done or fat or not os.path.isfile(cp):
                first = [l.strip() for l in err.splitlines() if re.search(r"\*\*\s*(Severe|Fatal)\s*\*\*", l)][:2]
                return None, "the run of the schedules failed: " + ("; ".join(first) if first else "no result")
            return read_series(cp), ""
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def compare(self, P, pairs, cal_pairs=(), tolerance=0.01):
        res = self._compare(P, pairs, cal_pairs, tolerance)
        if res["status"] == "done":
            res["applied"] = True
            res["rescued"] = [r["reference"] for r in res["rows"] if r["same"] and r.get("trigger") != "calendar"]
            res["demoted"] = [r["reference"] for r in res["rows"] if not r["same"] and r.get("trigger") == "calendar"]
        else:
            res["applied"] = False
            why = res.get("reason") or ""
            if res["status"] == "not_run" and ("weather file" in why or "energyplus program" in why):
                res["note"] = "the 8,760-hour comparison was not applied because there is no EnergyPlus program or no weather file (%s); the result of the comparison by day type stands" % why
                res["note_zh"] = "因为没有EnergyPlus 或天气文件，8760 没有应用"
            else:
                res["note"] = "the 8,760-hour comparison was not applied (%s); the result of the comparison by day type stands" % (why or res["status"])
                res["note_zh"] = "8760 没有应用（原因：%s）" % (why or res["status"])
        return res

    def _compare(self, P, pairs, cal_pairs=(), tolerance=0.01):
        """pairs: the pairs that the comparison by day type finds different (the same series = the same schedule: no tolerance).
        cal_pairs: the pairs that the comparison by day type finds the SAME, expanded because the calendar of the two files differs (holidays, start weekday ...): the hours that differ are
        outside the `For:` day types, so the pair stays the same while the share of hours that differ is at most `tolerance` (default 1 %); above it the schedule is different (row `trigger: calendar`)."""
        res = dict(status="not_run", reason="", hours=None, rows=[], expanded=len(pairs), expanded_calendar=len(cal_pairs), tolerance=tolerance)
        if not pairs and not cal_pairs:
            res.update(status="done", reason="no schedule differs by the comparison of the meaning, and the calendar does not call for a check: nothing to expand")
            return res
        if not self.weather or not os.path.isfile(self.weather):
            res["reason"] = "the weather file %s was not found (run data/weather/download_weather.py or give --weather-dir)" % (os.path.basename(self.weather) if self.weather else "of the case")
            return res
        runs = {}
        for who, own in (("r", P.ref), ("c", P.cand)):
            text = build_idf(P.ref, own, self.base_dirs.get(who))
            if text is None:
                res["reason"] = "the reference has no RunPeriod: the schedules are not expanded"
                return res
            s, why = self._run(text)
            if s is None:
                res.update(status="failed", reason=("reference: " if who == "r" else "candidate: ") + why)
                return res
            runs[who] = s
        for trig, plist in (("day_type", pairs), ("calendar", cal_pairs)):
          for rn, cn in plist:
            a, b = runs["r"].get(rn.lower()), runs["c"].get(cn.lower())
            if a is None or b is None or len(a) != len(b) or not a:
                if trig == "calendar":
                    continue          # a pair that is the same by day type and has no series: the result by day type stands
                res["rows"].append(dict(reference=rn, candidate=cn, same=False, share=0.0, first_difference=None, trigger=trig, note="no series of one of the two schedules (or of another length)"))
                continue
            eq = [abs(u - w) <= max(ABS_TOL, TOL * max(abs(u), abs(w))) for u, w in zip(a, b)]
            first = next((i for i, e in enumerate(eq) if not e), None)
            share = sum(eq) / len(eq)
            diff_h = len(eq) - sum(eq)
            same = first is None if trig == "day_type" else (diff_h / len(eq) <= tolerance + 1e-12)
            res["rows"].append(dict(reference=rn, candidate=cn, same=same, share=share, diff_hours=diff_h, trigger=trig, first_difference=None if first is None else dict(hour_of_year=first + 1, reference=a[first], candidate=b[first])))
            res["hours"] = len(a)
        res.update(status="done")
        return res
