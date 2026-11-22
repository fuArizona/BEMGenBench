#!/usr/bin/env python3
"""Tests of class_keys.py (PILOT: the documents give only a category). python evaluator/tests/test_class_keys.py"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import idf_doc_compare  # noqa: E402

FAILS = []


def check(name, cond, info=""):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)
        print("     ", info)


HEAD = "Version,\n 23.1;\n\nBuilding,\n B;\n\nGlobalGeometryRules,\n UpperLeftCorner, Counterclockwise, Relative;\n\n"
DOC = "Source: xlsx raw_data row 1"


def surfaces(con):
    t = "Zone,\n Z1,\n 0, 0, 0, 0, 1, 1, 3;\n\n"
    t += "BuildingSurface:Detailed,\n Wall1,\n Wall,\n %s,\n Z1,\n ,\n Outdoors,\n ,\n SunExposed,\n WindExposed,\n 0.5,\n 4,\n 0,0,3,\n 0,0,0,\n 4,0,0,\n 4,0,3;\n\n" % con
    return t


def door(mat, k, rho, cname):
    return ("Material,\n %s,  !- Name  %s\n MediumSmooth,\n 0.045,  !- Thickness  %s\n %s,  !- Conductivity  %s\n %s,\n 1630;\n\n" % (mat, DOC, DOC, k, DOC, rho) +
            "Construction,\n %s,  !- Name  %s\n %s;  !- Outside Layer  %s\n\n" % (cname, DOC, mat, DOC) + surfaces(cname))


ITEMS = dict(items=[dict(id="door_wood", object=dict(**{"class": "Construction"}, name="Ext Door"), quote="input1.txt: wood door", category="wood door",
                         definition="a door whose material is wood; not a metal door")])


def run(cand, verdicts=None, items=ITEMS):
    d = tempfile.mkdtemp()
    fa, fb, ck = (os.path.join(d, n) for n in ("a.idf", "b.idf", "ck.json"))
    open(fa, "w").write(HEAD + door("Door core", 0.15, 608, "Ext Door"))
    open(fb, "w").write(HEAD + cand)
    json.dump(items, open(ck, "w"))
    args = ["--reference", fa, "--candidate", fb, "--out", d, "--name", "t", "--class-keys", ck]
    if verdicts is not None:
        vf = os.path.join(d, "v.json")
        json.dump(verdicts, open(vf, "w"))
        args += ["--judgements", vf]
    idf_doc_compare.main(args)
    rep = json.load(open(os.path.join(d, "t.idf_doc_compare_report.json")))
    rq = json.load(open(os.path.join(d, "t.judgement_requests.json")))["requests"] if os.path.isfile(os.path.join(d, "t.judgement_requests.json")) else []
    return rep, rq


cand = door("mat-17", 0.14, 550, "Cst 7")          # the candidate's partner of Ext Door is Cst 7 (the same surface polygon)
rep, rq = run(cand)
ck = [q for q in rq if q["task"] == "belongs_to_class"]
check("a request `belongs_to_class` with the document quote, the category and the candidate's construction with its layer", len(ck) == 1 and "mat-17" in ck[0]["candidate"]["text"] and ck[0]["document"]["category"] == "wood door", rq)
check("the reference object is not in the request", ck and "Door core" not in json.dumps(ck[0]) and "Ext Door" not in json.dumps(ck[0]), ck)
check("without a verdict file the status is not_judged and no key is added", rep["class_keys"]["status"] == "not_judged" and rep["class_keys"]["not_judged"] == 1, rep["class_keys"])
qid = ck[0]["id"]
rep2, _ = run(cand, dict(judge={}, verdicts=[dict(id=qid, verdict="belongs", rationale="k 0.14, rho 550: wood")]))
c2 = rep2["class_keys"]
check("a verdict `belongs`: judged, one item belongs", c2["status"] == "judged" and c2["belongs"] == 1 and c2["items"] == 1, c2)
check("the key score is not changed by the verdict", rep2["score"] == rep["score"], (rep2["score"], rep["score"]))
check("the verdict is not rejected by the judge of the constructions", (rep2["equivalences"].get("llm") or {}).get("rejected") == [], rep2["equivalences"].get("llm"))
rep3, _ = run(cand, dict(judge={}, verdicts=[dict(id=qid, verdict="does_not_belong")]))
check("a verdict `does_not_belong`: counted, not in the category", rep3["class_keys"]["does_not_belong"] == 1 and rep3["class_keys"]["belongs"] == 0, rep3["class_keys"])
rep4, _ = run(cand, dict(judge={}, verdicts=[]))
check("a verdict file without a verdict for the item: uncertain (not in the category)", rep4["class_keys"]["uncertain"] == 1 and rep4["class_keys"]["belongs"] == 0, rep4["class_keys"])
rep5, _ = run(cand, dict(judge={}, verdicts=[dict(id=qid, verdict="maybe")]))
check("a verdict that is not allowed counts as uncertain", rep5["class_keys"]["uncertain"] == 1, rep5["class_keys"])
other = dict(items=[dict(id="x", object=dict(**{"class": "Construction"}, name="No such construction"), quote="q", category="c", definition="d")])
rep6, rq6 = run(cand, None, other)
check("an object of the reference that has no partner: no request, status no_counterpart", rep6["class_keys"]["no_counterpart"] == 1 and not [q for q in rq6 if q["task"] == "belongs_to_class"], rep6["class_keys"])

print("\n%d failure(s)" % len(FAILS) if FAILS else "\nall tests passed")
sys.exit(1 if FAILS else 0)
