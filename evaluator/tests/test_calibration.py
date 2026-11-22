#!/usr/bin/env python3
"""Tests of the calibration set (evaluator/calibration/build_set.py and score_judgements.py). python evaluator/tests/test_calibration.py"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CAL = os.path.join(os.path.dirname(HERE), "calibration")
FAILS = []


def check(name, cond, info=""):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)
        print("     ", info)


d = tempfile.mkdtemp()
r = subprocess.run([sys.executable, os.path.join(CAL, "build_set.py"), "--out", d], capture_output=True, text=True)
check("the set is built", r.returncode == 0, r.stderr[-300:])
reqs = json.load(open(os.path.join(d, "requests.json")))["requests"]
truth = json.load(open(os.path.join(d, "truth.json")))
labels = {t["label"] for t in truth.values()}
check("at least 150 pairs with the four labels, in dev and in test", len(reqs) >= 150 and labels == {"equivalent", "u_equivalent_only", "not_equivalent", "boundary"} and {t["split"] for t in truth.values()} == {"dev", "test"}, (len(reqs), labels))
text = open(os.path.join(d, "requests.json")).read()
check("the requests do not hold a label or a family", "u_equivalent_only" not in text and "r_off_" not in text and "reverse_order" not in text)
check("a base construction is in one split only", all(len({t["split"] for t in truth.values() if t["base"] == b}) == 1 for b in {t["base"] for t in truth.values()}))
d2 = tempfile.mkdtemp()
subprocess.run([sys.executable, os.path.join(CAL, "build_set.py"), "--out", d2], capture_output=True, text=True)
check("the same seed gives the same set", open(os.path.join(d2, "requests.json")).read() == text)
r = subprocess.run([sys.executable, os.path.join(CAL, "score_judgements.py"), d, "--baseline"], capture_output=True, text=True)
check("the scorer runs on the rule of the evaluator (no false equivalent among the not_equivalent pairs)", r.returncode == 0 and "false equivalent: 0 of" in r.stdout, r.stdout[-400:] + r.stderr[-200:])
print("\n%d failure(s)" % len(FAILS) if FAILS else "\nall tests passed")
sys.exit(1 if FAILS else 0)
