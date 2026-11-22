#!/usr/bin/env python3
"""Tests of the interface for a judge (engine/idf_judge.py): the requests the evaluator writes, and the verdict files it reads (made here by hand; no language model is called).

python evaluator/tests/test_judgements.py"""
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


DOC = "Source: xlsx raw_data row 1"
HEAD = "Version,\n 23.1;\n\nBuilding,\n B;\n\nGlobalGeometryRules,\n UpperLeftCorner, Counterclockwise, Relative;\n\n"


def doc_obj(cls, name, fields):
    lines = [cls + ",", " %s,  !- Name  %s" % (name, DOC)]
    for i, (v, lab) in enumerate(fields):
        lines.append(" %s%s  !- %s  %s" % (v, ";" if i == len(fields) - 1 else ",", lab, DOC))
    return "\n".join(lines) + "\n\n"


def surfaces(con):
    t = "Zone,\n Z1,\n 0, 0, 0, 0, 1, 1, 3;\n\n"
    t += "BuildingSurface:Detailed,\n Floor1,\n Floor,\n %s,\n Z1,\n ,\n Ground,\n ,\n NoSun,\n NoWind,\n 0,\n 4,\n 0,0,0,\n 0,5,0,\n 4,5,0,\n 4,0,0;\n\n" % con
    t += "BuildingSurface:Detailed,\n Wall1,\n Wall,\n %s,\n Z1,\n ,\n Outdoors,\n ,\n SunExposed,\n WindExposed,\n 0.5,\n 4,\n 0,0,3,\n 0,0,0,\n 4,0,0,\n 4,0,3;\n\n" % con
    return t


def wall(k="0.8", t="0.1", ins="2.0", mat="Brick", con="Wall"):
    return (doc_obj("Material", mat, [("Rough", "Roughness"), (t, "Thickness"), (k, "Conductivity"), ("1800", "Density"), ("900", "Specific Heat")]) +
            doc_obj("Material:NoMass", "Ins", [("Rough", "Roughness"), (ins, "Thermal Resistance")]) + doc_obj("Construction", con, [(mat, "Outside Layer"), ("Ins", "Layer 2")]))


def run(a, b, judgements=None):
    d = tempfile.mkdtemp()
    fa, fb = os.path.join(d, "a.idf"), os.path.join(d, "b.idf")
    open(fa, "w").write(a)
    open(fb, "w").write(b)
    args = ["--reference", fa, "--candidate", fb, "--out", d, "--name", "t"]
    if judgements is not None:
        jf = os.path.join(d, "j.json")
        json.dump(judgements, open(jf, "w"))
        args += ["--judgements", jf]
    idf_doc_compare.main(args)
    rep = json.load(open(os.path.join(d, "t.idf_doc_compare_report.json")))
    rq = os.path.join(d, "t.judgement_requests.json")
    return rep, (json.load(open(rq))["requests"] if os.path.isfile(rq) else [])


REF = HEAD + wall() + surfaces("Wall")
# 1. the partner of a construction is found by the surfaces (and by the pairing): then no request
rep, reqs = run(REF, HEAD + wall(k="0.4", t="0.05", con="Wall B", mat="Brick B") + surfaces("Wall B"))
check("the partner is found by the surfaces: no request 'no_counterpart'", not [q for q in reqs if q["task"] == "no_counterpart"], reqs)
# the reference has two constructions, the candidate two others that no surface names: Roof pairs with Omega (the pairing by similarity), Wall has no partner
ROOF = doc_obj("Material:NoMass", "RoofIns", [("Rough", "Roughness"), ("5.0", "Thermal Resistance")]) + doc_obj("Construction", "Roof", [("RoofIns", "Outside Layer")])
REF2 = HEAD + wall() + ROOF


def zeta(r):
    """The candidate: Zeta (one layer without mass, resistance r) and Omega."""
    return (HEAD + doc_obj("Material:NoMass", "ZetaR", [("Rough", "Roughness"), (r, "Thermal Resistance")]) + doc_obj("Construction", "Zeta", [("ZetaR", "Outside Layer")]) +
            doc_obj("Material:NoMass", "OmegaR", [("Rough", "Roughness"), ("7.0", "Thermal Resistance")]) + doc_obj("Construction", "Omega", [("OmegaR", "Outside Layer")]))


CAND2 = zeta("2.125")
rep, reqs = run(REF2, CAND2)
np_ = [q for q in reqs if q["task"] == "no_counterpart"]
check("a reference construction without a partner: a request 'no_counterpart' that lists the candidate constructions that have no partner", len(np_) == 1 and [c["construction"] for c in np_[0]["candidates"]] == ["Zeta"] and "ZetaR" in np_[0]["candidates"][0]["text"], reqs)
check("the text of the request has no comments", all("Source" not in q["reference"]["text"] and "Source" not in q["candidates"][0]["text"] for q in np_), np_)
if np_:
    q = np_[0]
    j = lambda **k: dict(judge=dict(model="test"), verdicts=[dict(id=q["id"], **k)])
    base = rep["equivalences"]
    rep, _ = run(REF2, CAND2, j(verdict="equivalent", candidate_construction="Zeta"))
    e = rep["equivalences"]
    rep, _ = run(REF2, CAND2, j(verdict="equivalent", candidate_construction="Zeta"))
    e = rep["equivalences"]
    check("'equivalent' for a construction with the same resistance but no mass (the brick wall has a heat capacity): refused", len(e["llm"]["rejected"]) == 1 and "heat capacit" in e["llm"]["rejected"][0]["reason"] and e["llm"]["equivalent"] == 0, e["llm"])
    check("the key score is not changed by the verdict", rep["score"]["same"] == run(REF2, CAND2)[0]["score"]["same"])
    rep, _ = run(REF2, CAND2, j(verdict="not_equivalent"))
    check("a 'not_equivalent' verdict gives nothing back", rep["equivalences"]["llm"]["recovered_by_judgement"] == 0 and not rep["equivalences"]["llm"]["rejected"], rep["equivalences"]["llm"])
    rep, _ = run(REF2, CAND2, j(verdict="equivalent", candidate_construction="Omega"))
    check("a construction that is not listed is rejected", len(rep["equivalences"]["llm"]["rejected"]) == 1, rep["equivalences"]["llm"])
    rep, _ = run(REF2, CAND2, j(verdict="maybe"))
    check("a verdict that is not allowed is rejected", len(rep["equivalences"]["llm"]["rejected"]) == 1, rep["equivalences"]["llm"])
    rep, _ = run(REF2, CAND2, dict(judge={}, verdicts=[dict(id="zzzz", verdict="equivalent")]))
    check("an id that is not a request is rejected", len(rep["equivalences"]["llm"]["rejected"]) == 1, rep["equivalences"]["llm"])
# the judge cannot overrule a computed number: the candidate construction has a resistance 32 % higher
FAR = zeta("2.8")
rep, reqs = run(REF2, FAR)
np_ = [q for q in reqs if q["task"] == "no_counterpart"]
rep, _ = run(REF2, FAR, dict(judge={}, verdicts=[dict(id=np_[0]["id"], verdict="equivalent", candidate_construction="Zeta")])) if np_ else (rep, None)
check("'equivalent' for a construction whose computed resistance differs by 32 %: refused", bool(np_) and len(rep["equivalences"]["llm"]["rejected"]) == 1 and rep["equivalences"]["llm"]["equivalent"] == 0, rep["equivalences"]["llm"] if np_ else "no request")
# 3. a pair 3 % off in resistance: a request 'classify_near' (a category only, never a score)
NEAR = HEAD + wall(ins="2.1", con="Wall") + surfaces("Wall")
rep, reqs = run(REF, NEAR)
cl = [q for q in reqs if q["task"] == "classify_near"]
check("a resistance 3 % off: a request 'classify_near' with the computed numbers", len(cl) == 1 and "r_reference" in cl[0]["computed"], reqs)
if cl:
    rep, _ = run(REF, NEAR, dict(judge={}, verdicts=[dict(id=cl[0]["id"], verdict="equivalent", category="rounding")]))
    check("the verdict on a 'classify_near' request is only recorded", rep["equivalences"]["llm"]["classified"][0]["category"] == "rounding" and rep["equivalences"]["llm"]["recovered_by_judgement"] == 0, rep["equivalences"]["llm"])
# 4. a layer without a value: the evaluator cannot compute the resistance: 'cannot_compute'
NOVAL = HEAD + doc_obj("Material", "Brick", [("Rough", "Roughness"), ("0.1", "Thickness"), ("", "Conductivity")]) + doc_obj("Material:NoMass", "Ins", [("Rough", "Roughness"), ("2.0", "Thermal Resistance")]) + doc_obj("Construction", "Wall", [("Brick", "Outside Layer"), ("Ins", "Layer 2")]) + surfaces("Wall")
rep, reqs = run(REF, NOVAL)
cc_ = [q for q in reqs if q["task"] == "cannot_compute"]
check("a layer without a conductivity: a request 'cannot_compute'", len(cc_) == 1, reqs)
if cc_:
    rep, _ = run(REF, NOVAL, dict(judge={}, verdicts=[dict(id=cc_[0]["id"], verdict="equivalent")]))
    check("an 'equivalent' verdict on it is accepted (nothing computed to contradict it) and gives back keys that the evaluator alone does not", rep["equivalences"]["llm"]["equivalent"] == 1 and not rep["equivalences"]["llm"]["rejected"] and rep["equivalences"]["llm"]["recovered_by_judgement"] > 0 and rep["equivalences"]["llm"]["rate_with_llm"] > rep["equivalences"]["rate_with_equivalents"], rep["equivalences"]["llm"])
rep, _ = run(REF, REF, dict(judge={}, verdicts=[]))
check("without a request nothing is asked and the llm result says so", rep["equivalences"]["llm"]["requests"] == 0 and rep["equivalences"]["llm"]["recovered_by_judgement"] == 0, rep["equivalences"]["llm"])

print("\n%d failure(s)" % len(FAILS) if FAILS else "\nall tests passed")
sys.exit(1 if FAILS else 0)
