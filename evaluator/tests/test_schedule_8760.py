#!/usr/bin/env python3
"""Tests of the 8,760-hour comparison of the schedules (schedule_8760.py): a schedule that the comparison of the meaning finds different is expanded by EnergyPlus and compared hour by hour.

python evaluator/tests/test_schedule_8760.py [weather.epw]      (any EPW file: the schedules do not depend on the weather; default: the first EPW of data/weather, else the environment variable BEMGEN_TEST_EPW)
Needs an EnergyPlus install (about 2 seconds per run of a file); skipped without one or without a weather file."""
import glob
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import idf_doc_compare  # noqa: E402
import idf_schema  # noqa: E402

FAILS = []


def check(name, cond, info=""):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)
        print("     ", info)


epw = (sys.argv[1] if len(sys.argv) > 1 else None) or os.environ.get("BEMGEN_TEST_EPW") or next(iter(sorted(glob.glob(os.path.join(ROOT, "data", "weather", "*.epw")))), None)
root = idf_schema.energyplus_root(None)
if not root or not epw or not os.path.isfile(epw):
    print("skipped: no EnergyPlus install or no weather file (give one on the command line or in BEMGEN_TEST_EPW)")
    sys.exit(0)

DOC = "Source: xlsx raw_data row 1"


def idf(year, sched_text):
    return ("Version,\n 23.1;\n\nBuilding,\n B;\n\nGlobalGeometryRules,\n UpperLeftCorner, Counterclockwise, Relative;\n\nZone,\n Z1,\n 0,0,0,0,1,1;\n\n"
            "RunPeriod,\n rp,\n 1,\n 1,\n %d,\n 12,\n 31,\n %d,\n ,\n Yes,\n Yes,\n No,\n Yes,\n Yes;\n\n" % (year, year) + sched_text)


def sched(through_blocks, doc=True):
    """through_blocks: [(through, [(for text, [(until, value)])])]"""
    out = "Schedule:Compact,\n S1,\n ,\n"
    items = []
    for th, fors in through_blocks:
        items.append(" Through: %s" % th)
        for ftxt, rows in fors:
            items.append(" For: %s" % ftxt)
            for u, v in rows:
                items.append(" Until: %s" % u)
                items.append(" %s" % v)
    for i, t in enumerate(items):
        out += "%s%s" % (t, ";" if i == len(items) - 1 else ",")
        if doc:
            out += "   !- field  " + DOC
        out += "\n"
    return out + "\n"


def run(ref, cand):
    d = tempfile.mkdtemp()
    fa, fb = os.path.join(d, "a.idf"), os.path.join(d, "b.idf")
    open(fa, "w").write(ref)
    open(fb, "w").write(cand)
    rc = idf_doc_compare.main(["--reference", fa, "--candidate", fb, "--out", d, "--name", "t", "--schedules-8760", "--weather", epw])
    return rc, json.load(open(os.path.join(d, "t.idf_doc_compare_report.json")))["schedule_kvor"]


const = lambda v: [("12/31", [("AllDays", [("24:00", v)])])]
# a candidate that is the same by the meaning: nothing is expanded
rc, s = run(idf(2025, sched(const("0.5"))), idf(2025, sched(const("0.5"))))
h = s["hourly_8760"]
check("same schedule: nothing is expanded, 1 / 1", h["status"] == "done" and h["expanded"] == 0 and h["schedules_same_8760"] == 1 and h["rate"] == 1.0, h)
# a real difference (hours 8 to 12 of every day): expanded, not the same, 19 / 24 of the hours equal
a = [("12/31", [("AllDays", [("7:00", "0.1"), ("24:00", "0.9")])])]
b = [("12/31", [("AllDays", [("12:00", "0.1"), ("24:00", "0.9")])])]
rc, s = run(idf(2025, sched(a)), idf(2025, sched(b)))
h = s["hourly_8760"]
check("a different schedule: expanded, 8,760 hours, not the same, 19 / 24 of the hours", h["status"] == "done" and h["expanded"] == 1 and h["hours"] == 8760 and h["same_after"] == 0 and abs(h["rate_hours"] - 19 / 24) < 1e-3, h)
check("the first difference is reported (hour 8 of the year)", h["rows"][0]["first_difference"]["hour_of_year"] == 8, h["rows"])
# different by the meaning, the same hour by hour: the candidate gives Sunday and the other days other values in a period of ONE day (1 January 2025 is a Wednesday)
ref = const("0.5")
cand = [("1/1", [("Wednesday", [("24:00", "0.5")]), ("AllOtherDays", [("24:00", "9")])]), ("12/31", [("AllDays", [("24:00", "0.5")])])]
rc, s = run(idf(2025, sched(ref)), idf(2025, sched(cand)))
h = s["hourly_8760"]
check("same hour by hour (2025: 1 January is a Wednesday) though the meaning differs: rescued", s["same"] == 0 and h["same_after"] == 1 and h["rate"] == 1.0 and h["rate_hours"] == 1.0, (s["same"], h))
# the same two files in a year that starts on a Monday: now different
rc, s = run(idf(2024, sched(ref)), idf(2024, sched(cand)))
h = s["hourly_8760"]
check("the same files in 2024 (1 January is a Monday): different, from hour 1", h["same_after"] == 0 and h["rows"][0]["first_difference"]["hour_of_year"] == 1, h)
# the run is not requested: no field
d = tempfile.mkdtemp()
open(os.path.join(d, "a.idf"), "w").write(idf(2025, sched(a)))
open(os.path.join(d, "b.idf"), "w").write(idf(2025, sched(b)))
idf_doc_compare.main(["--reference", os.path.join(d, "a.idf"), "--candidate", os.path.join(d, "b.idf"), "--out", d, "--name", "t"])
check("without --schedules-8760 there is no run and the field is empty", json.load(open(os.path.join(d, "t.idf_doc_compare_report.json")))["schedule_kvor"]["hourly_8760"] is None)
# a missing weather file is reported, not an error
rc = idf_doc_compare.main(["--reference", os.path.join(d, "a.idf"), "--candidate", os.path.join(d, "b.idf"), "--out", d, "--name", "t2", "--schedules-8760", "--weather", os.path.join(d, "none.epw")])
h = json.load(open(os.path.join(d, "t2.idf_doc_compare_report.json")))["schedule_kvor"]["hourly_8760"]
check("a missing weather file: status not_run with the reason", rc == 0 and h["status"] == "not_run" and "weather" in h["reason"], h)

# the 8,760-hour comparison is the FINAL one: the same series = the same schedule (schedule_rescue.py), all the keys of it
import schedule_rescue  # noqa: E402
d_ = tempfile.mkdtemp()
ref_t, cand_t = idf(2025, sched(ref)), idf(2025, sched(cand))
fa, fb = os.path.join(d_, "a.idf"), os.path.join(d_, "b.idf")
open(fa, "w").write(ref_t)
open(fb, "w").write(cand_t)
idf_doc_compare.main(["--reference", fa, "--candidate", fb, "--out", d_, "--name", "t", "--schedules-8760", "--weather", epw])
rep1 = json.load(open(os.path.join(d_, "t.idf_doc_compare_report.json")))
rows = rep1["schedule_kvor"]["hourly_8760"]["rows"]
new_t, n_ = schedule_rescue.rescue(cand_t, ref_t, rows)
open(fb, "w").write(new_t)
d2 = tempfile.mkdtemp()
idf_doc_compare.main(["--reference", fa, "--candidate", fb, "--out", d2, "--name", "t"])
rep2 = json.load(open(os.path.join(d2, "t.idf_doc_compare_report.json")))
check("the pair that the day-type comparison finds different but the 8,760 hours the same is replaced by the reference's schedule under the candidate's name", n_ == 1 and rep1["schedule_kvor"]["same"] == 0 and rep1["schedule_kvor"]["hourly_8760"]["rescued"] == ["S1"], (n_, rep1["schedule_kvor"]))
check("on the second run all the keys of that schedule are the same (key score and schedule KVOR)", rep2["schedule_kvor"]["same"] == 1 and rep2["score"]["same"] == rep2["score"]["keys"], (rep1["score"], rep2["score"], rep2["schedule_kvor"]))
check("a pair with different series is not replaced (the result by day type stands)", schedule_rescue.rescue(cand_t, ref_t, [dict(reference="S1", candidate="S1", same=False)])[1] == 0)
# without a weather file the comparison is not applied, and the result says so
d3 = tempfile.mkdtemp()
fb2 = os.path.join(d3, "b.idf")
open(fb2, "w").write(cand_t)
idf_doc_compare.main(["--reference", fa, "--candidate", fb2, "--out", d3, "--name", "t", "--schedules-8760", "--weather", os.path.join(d3, "none.epw")])
h_ = json.load(open(os.path.join(d3, "t.idf_doc_compare_report.json"), encoding="utf8"))["schedule_kvor"]["hourly_8760"]
check("without a weather file: not applied, with the note in English and in Chinese", h_["applied"] is False and "no EnergyPlus program or no weather file" in h_["note"] and h_["note_zh"] == "因为没有EnergyPlus 或天气文件，8760 没有应用", h_)

# end to end with evaluate.py: a case whose weather file is the EPW given (Buffalo): the candidate is the reference with one schedule written with a period of one day first
import re  # noqa: E402
import subprocess  # noqa: E402
CASE = os.path.join(ROOT, "cases", "doe_small_office")
if os.path.isdir(CASE) and "Buffalo" in os.path.basename(epw):
    rt = open(os.path.join(CASE, "reference", "reference.idf"), encoding="utf8").read()
    m = re.search(r"  Schedule:Compact,\n    ltg_sch_office,.*?;[^\n]*\n", rt, re.S)
    old = m.group(0)
    head, body = old.split("Through: 12/31", 1)
    sun = re.search(r"For: (?:Sunday|AllOtherDays)[^\n]*\n((?:\s+Until:[^\n]*\n)+)", old)
    sunday = "".join("    Until: %s,%s,\n" % uv for uv in re.findall(r"Until: ([\d:]+),([\d.]+)", sun.group(1)))
    cand_e = rt.replace(old, head + "Through: 1/1,\n    For: Sunday,\n" + sunday + "    For: AllOtherDays,\n    Until: 24:00,0.99,\n    Through: 12/31" + body)
    de = tempfile.mkdtemp()
    cf = os.path.join(de, "cand.idf")
    open(cf, "w", encoding="utf8").write(cand_e)

    def ev(*extra):
        out = os.path.join(de, "o%d" % len(os.listdir(de)))
        subprocess.run([sys.executable, "-B", os.path.join(ROOT, "evaluator", "evaluate.py"), "--case", CASE, "--candidate", cf, "--out", out, "--no-run"] + list(extra), capture_output=True, text=True)
        return json.load(open(os.path.join(out, "doe_small_office.json"), encoding="utf8"))
    j1 = ev("--weather-dir", os.path.dirname(epw))
    j2 = ev("--weather-dir", os.path.dirname(epw), "--no-schedules-8760")
    j3 = ev("--weather-dir", os.path.join(de, "nowhere"))
    check("evaluate.py: the 8,760 hours are the final comparison: 265 / 265 (rescued: ltg_sch_office)", j1["score"]["same"] == j1["score"]["keys"] and j1["schedule_8760"]["rescued"] == ["ltg_sch_office"], (j1["score"], j1["schedule_8760"]))
    check("evaluate.py --no-schedules-8760: the result by day type (fewer keys)", j2["score"]["same"] < j2["score"]["keys"] and j2["schedule_8760"]["applied"] is False, (j2["score"], j2["schedule_8760"]))
    check("evaluate.py without a weather file: the result by day type, and the note in English and Chinese in the case file", j3["score"]["same"] == j2["score"]["same"] and j3["schedule_8760"]["applied"] is False and j3["schedule_8760"]["note_zh"] == "因为没有EnergyPlus 或天气文件，8760 没有应用", (j3["score"], j3["schedule_8760"]))
else:
    print("skipped: the end-to-end test of evaluate.py (needs the Buffalo EPW file and the case doe_small_office)")

print("\n%d failure(s)" % len(FAILS) if FAILS else "\nall tests passed")
sys.exit(1 if FAILS else 0)
