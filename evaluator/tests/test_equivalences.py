#!/usr/bin/env python3
"""Tests of idf_equiv.py: the same quantity written another way (constructions, windows, outdoor air and ventilation).

python evaluator/tests/test_equivalences.py [weather.epw]      The window tests that need EnergyPlus run only with a program and a weather file (any EPW; the default is the first of data/weather or BEMGEN_TEST_EPW)."""
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


DOC = "Source: xlsx raw_data row 1"
HEAD = "Version,\n 23.1;\n\nBuilding,\n B;\n\nGlobalGeometryRules,\n UpperLeftCorner, Counterclockwise, Relative;\n\n"


def zone_and_surface(con, zone="Z1", ceiling=3.0):
    t = "Zone,\n %s,\n 0, 0, 0, 0, 1, 1, %s;\n\n" % (zone, ceiling)
    t += ("BuildingSurface:Detailed,\n Floor1,\n Floor,\n %s,\n %s,\n ,\n Ground,\n ,\n NoSun,\n NoWind,\n 0,\n 4,\n 0,0,0,\n 0,5,0,\n 4,5,0,\n 4,0,0;\n\n" % (con, zone))
    t += ("BuildingSurface:Detailed,\n Wall1,\n Wall,\n %s,\n %s,\n ,\n Outdoors,\n ,\n SunExposed,\n WindExposed,\n 0.5,\n 4,\n 0,0,3,\n 0,0,0,\n 4,0,0,\n 4,0,3;\n\n" % (con, zone))
    return t


def doc_obj(cls, name, fields):
    """fields: [(value, label)]: every field carries the documentary comment."""
    lines = [cls + ",", " %s,  !- Name  %s" % (name, DOC)]
    for i, (v, lab) in enumerate(fields):
        lines.append(" %s%s  !- %s  %s" % (v, ";" if i == len(fields) - 1 else ",", lab, DOC))
    return "\n".join(lines) + "\n\n"


def two_layer(k, t):
    return (doc_obj("Material", "Brick", [("Rough", "Roughness"), (t, "Thickness"), (k, "Conductivity"), ("1800", "Density"), ("900", "Specific Heat")]) +
            doc_obj("Material:NoMass", "Ins", [("Rough", "Roughness"), ("2.0", "Thermal Resistance")]) +
            doc_obj("Construction", "Wall", [("Brick", "Outside Layer"), ("Ins", "Layer 2")]))


def one_layer(r):
    return (doc_obj("Material:NoMass", "WallR", [("Rough", "Roughness"), (r, "Thermal Resistance")]) + doc_obj("Construction", "Wall", [("WallR", "Outside Layer")]))


def run(a, b, extra=()):
    d = tempfile.mkdtemp()
    fa, fb = os.path.join(d, "a.idf"), os.path.join(d, "b.idf")
    open(fa, "w").write(a)
    open(fb, "w").write(b)
    idf_doc_compare.main(["--reference", fa, "--candidate", fb, "--out", d, "--name", "t"] + list(extra))
    return json.load(open(os.path.join(d, "t.idf_doc_compare_report.json")))


# equivalent = the resistance, the heat capacity and the order of the layers (user decision 2026-11-21)
# a wall without mass (two NoMass layers, R 1.0 + 1.125 = 2.125) against one NoMass layer of 2.125: the same
def two_nomass():
    return doc_obj("Material:NoMass", "A", [("Rough", "Roughness"), ("1.0", "Thermal Resistance")]) + doc_obj("Material:NoMass", "B", [("Rough", "Roughness"), ("1.125", "Thermal Resistance")]) + doc_obj("Construction", "Wall", [("A", "Outside Layer"), ("B", "Layer 2")])


refm = HEAD + two_nomass() + zone_and_surface("Wall")
same_r = HEAD + one_layer("2.125") + zone_and_surface("Wall")
j = run(refm, same_r)
e = j["equivalences"]
check("a two-layer wall and a one-layer wall without mass and with the same resistance: equivalent", e["constructions"]["pairs"] == 1 and e["constructions"]["equivalent"] == 1, e["constructions"])
check("the keys of the layers are given back; the supplementary rate is higher than the score", e["recovered_keys"] > 0 and e["rate_with_equivalents"] > j["score"]["rate"], (e["recovered_keys"], e["rate_with_equivalents"], j["score"]))
check("the key score itself has the losses (not changed)", j["score"]["same"] < j["score"]["keys"], j["score"])
e = run(refm, HEAD + one_layer("2.4") + zone_and_surface("Wall"))["equivalences"]
check("a resistance 13 % off: not equivalent, nothing given back", e["constructions"]["equivalent"] == 0 and e["recovered_keys"] == 0, e)
e = run(refm, HEAD + one_layer("2.14") + zone_and_surface("Wall"))["equivalences"]
check("a resistance 0.7 % off (inside the 1 % tolerance): equivalent", e["constructions"]["equivalent"] == 1, e["constructions"])
# the brick wall (heat capacity) against a one-layer wall without mass: the same resistance, but the mass is lost: not equivalent
ref = HEAD + two_layer("0.8", "0.1") + zone_and_surface("Wall")
e = run(ref, same_r)["equivalences"]
r0 = e["constructions"]["rows"][0]
check("the same resistance but the mass is lost (NoMass): not equivalent, nothing given back", r0["same_r"] and not r0["mass_same"] and not r0["same"] and e["recovered_keys"] == 0, r0)
# the same layers in the other order: the same resistance and mass, the heat capacity at the other end
rev = (doc_obj("Material:NoMass", "Ins", [("Rough", "Roughness"), ("2.0", "Thermal Resistance")]) + doc_obj("Material", "Brick", [("Rough", "Roughness"), ("0.1", "Thickness"), ("0.8", "Conductivity"), ("1800", "Density"), ("900", "Specific Heat")]) +
       doc_obj("Construction", "Wall", [("Ins", "Outside Layer"), ("Brick", "Layer 2")]))
e = run(ref, HEAD + rev + zone_and_surface("Wall"))["equivalences"]
r0 = e["constructions"]["rows"][0]
check("the layers in the other order: the same resistance and mass, another position of the heat capacity: not equivalent", r0["same_r"] and r0["mass_same"] and not r0["order_same"] and not r0["same"] and e["recovered_keys"] == 0, r0)
# a construction that the documents give only as a U-value (traceability/u_only_constructions.json): the thermal resistance alone decides
def run_u(ref_t, cand_t, names):
    d = tempfile.mkdtemp()
    fa, fb, fu = (os.path.join(d, n) for n in ("a.idf", "b.idf", "u.json"))
    open(fa, "w").write(ref_t)
    open(fb, "w").write(cand_t)
    json.dump(dict(constructions=[dict(name=n) for n in names]), open(fu, "w"))
    idf_doc_compare.main(["--reference", fa, "--candidate", fb, "--out", d, "--name", "t", "--u-only", fu])
    return json.load(open(os.path.join(d, "t.idf_doc_compare_report.json")))["equivalences"]


ref_u = HEAD + one_layer("2.125") + zone_and_surface("Wall")            # one layer without mass, as the reference writes a U-value
cand_layers = HEAD + two_layer("0.8", "0.1") + zone_and_surface("Wall")  # layers with mass, the same resistance 0.125 + 2.0
e = run_u(ref_u, cand_layers, [])["constructions"]
check("without the list: a wall with mass against the one-layer wall of the same resistance is not equivalent", e["equivalent"] == 0 and not e["rows"][0]["mass_same"], e)
e = run_u(ref_u, cand_layers, ["Wall"])["constructions"]
check("a construction of the list (the documents give only the U-value): equivalent by the resistance alone", e["equivalent"] == 1 and e["u_only_pairs"] == 1 and e["rows"][0]["u_only"] and not e["rows"][0]["mass_same"], e)
e = run_u(ref_u, HEAD + two_layer("0.4", "0.1") + zone_and_surface("Wall"), ["Wall"])["constructions"]
check("a construction of the list with another resistance (2.25 against 2.125) is not equivalent", e["equivalent"] == 0, e)

# a different construction name in the candidate, the same layers
e = run(ref, ref.replace(" Wall,  !- Name", " WallX,  !- Name").replace("Wall,\n Z1", "WallX,\n Z1").replace(" Wall,\n Z1", " WallX,\n Z1"))["equivalences"]
check("the same layers under another construction name (partner by the paired surfaces): equivalent", e["constructions"]["pairs"] >= 1 and e["constructions"]["equivalent"] == e["constructions"]["pairs"], e["constructions"])

# the keys given back: density and specific heat only when the heat capacity is also the same (the table RULES of idf_equiv.py)
import idf_equiv  # noqa: E402


def brick_keys(e):
    return sum(x["keys"] for x in e["recovered"] if x["key"].lower().startswith("material/brick"))


def two_layer_mat(name, k, t, rho):
    return (doc_obj("Material", name, [("Rough", "Roughness"), (t, "Thickness"), (k, "Conductivity"), (rho, "Density"), ("900", "Specific Heat")]) +
            doc_obj("Material:NoMass", "Ins", [("Rough", "Roughness"), ("2.0", "Thermal Resistance")]) + doc_obj("Construction", "Wall", [(name, "Outside Layer"), ("Ins", "Layer 2")]))


mass_ok = HEAD + two_layer_mat("Brick2", "0.4", "0.05", "3600") + zone_and_surface("Wall")           # R 0.125 as the reference, heat capacity 3600 x 900 x 0.05 = 1800 x 900 x 0.1
e = run(ref, mass_ok)["equivalences"]
check("the same resistance and the same heat capacity: the three lost keys of the brick (the specific heat is the same in both files) are given back", e["constructions"]["equivalent"] == 1 and e["constructions"]["rows"][0]["mass_same"] and brick_keys(e) == 3, e["recovered"])
mass_off = HEAD + two_layer_mat("Brick2", "0.4", "0.05", "5000") + zone_and_surface("Wall")          # the same resistance, the heat capacity 39 % higher
e = run(ref, mass_off)["equivalences"]
check("the same resistance, the heat capacity 39 % off: not equivalent, nothing given back", e["constructions"]["equivalent"] == 0 and not e["constructions"]["rows"][0]["mass_same"] and brick_keys(e) == 0, (e["constructions"]["rows"], e["recovered"]))
doc = open(os.path.join(ROOT, "docs", "equivalence_rules.md"), encoding="utf8").read()
check("docs/equivalence_rules.md is the output of rules_markdown() (do not edit it by hand)", doc == idf_equiv.rules_markdown())

# the outdoor air and ventilation of a zone: a flow for the whole zone against a flow per floor area (the floor is 4 x 5 = 20 m2)
vent = lambda m, v: ("ZoneVentilation:DesignFlowRate,\n V1,\n Z1,\n ,\n %s,\n %s;\n\n" % (m, v))
ref_a = HEAD + two_layer("0.8", "0.1") + zone_and_surface("Wall") + "ZoneVentilation:DesignFlowRate,\n V1,\n Z1,\n ,\n Flow/Zone,\n 0.04;\n\n"
cand_a = HEAD + two_layer("0.8", "0.1") + zone_and_surface("Wall") + "ZoneVentilation:DesignFlowRate,\n V1,\n Z1,\n ,\n Flow/Area,\n ,\n 0.002;\n\n"
e = run(ref_a, cand_a)["equivalences"]["air"]
check("0.04 m3/s for the zone and 0.002 m3/s per m2 of a 20 m2 floor: the same", e["comparable"] == 1 and e["same"] == 1, e)
cand_b = cand_a.replace("0.002", "0.0025")
e = run(ref_a, cand_b)["equivalences"]["air"]
check("0.05 m3/s against 0.04 m3/s: not the same", e["comparable"] == 1 and e["same"] == 0, e)
e = run(ref, cand_a)["equivalences"]["air"]
check("a zone that only one file states: listed, not compared", e["zones"] == 1 and e["comparable"] == 0 and e["same"] == 0, e)

# windows: the U-factor and the SHGC; simple glazing against simple glazing by their numbers; layered glazing by EnergyPlus
epw = (sys.argv[1] if len(sys.argv) > 1 else None) or os.environ.get("BEMGEN_TEST_EPW") or next(iter(sorted(glob.glob(os.path.join(ROOT, "data", "weather", "*.epw")))), None)
root = idf_schema.energyplus_root(None)


def win(u, shgc, name="Glz"):
    return (doc_obj("WindowMaterial:SimpleGlazingSystem", name, [(u, "U-Factor"), (shgc, "SHGC")]) + doc_obj("Construction", "Win", [(name, "Outside Layer")]) +
            "FenestrationSurface:Detailed,\n W1,\n Window,\n Win,\n Wall1,\n ,\n 0.1,\n ,\n 1,\n 4,\n 1,0,2,\n 1,0,1,\n 2,0,1,\n 2,0,2;\n\n")


base = HEAD + zone_and_surface("Wall") + two_layer("0.8", "0.1")
extra = ["--weather", epw] if epw and root else []
e = run(base + win("2.5", "0.4"), base + win("2.5", "0.4", "OtherGlazing"), extra)["equivalences"]["constructions"]
wrow = [r for r in e["rows"] if r["kind"] == "window"]
check("simple glazing under another name, the same U and SHGC: equivalent", wrow and wrow[0]["same"], e)
e = run(base + win("2.5", "0.4"), base + win("2.5", "0.45", "OtherGlazing"), extra)["equivalences"]["constructions"]
wrow = [r for r in e["rows"] if r["kind"] == "window"]
check("an SHGC 12 % off: not equivalent", wrow and not wrow[0]["same"], e)
if epw and root:
    layered = (doc_obj("WindowMaterial:Glazing", "Clear3", [("SpectralAverage", "Optical Data"), ("", "Window Glass Spectral Data Set"), ("0.003", "Thickness"), ("0.837", "Solar Transmittance"), ("0.075", "Front Reflectance"), ("0.075", "Back Reflectance"), ("0.898", "Visible Transmittance"), ("0.081", "Front Visible Reflectance"), ("0.081", "Back Visible Reflectance"), ("0", "IR Transmittance"), ("0.84", "Front IR Emissivity"), ("0.84", "Back IR Emissivity"), ("0.9", "Conductivity")]) +
               doc_obj("WindowMaterial:Gas", "Air13", [("Air", "Gas Type"), ("0.013", "Thickness")]) + doc_obj("Construction", "Win", [("Clear3", "Outside Layer"), ("Air13", "Layer 2"), ("Clear3", "Layer 3")]) +
               "FenestrationSurface:Detailed,\n W1,\n Window,\n Win,\n Wall1,\n ,\n 0.1,\n ,\n 1,\n 4,\n 1,0,2,\n 1,0,1,\n 2,0,1,\n 2,0,2;\n\n")
    e = run(base + layered, base + layered.replace("Clear3", "PaneA").replace("Air13", "GapA"), extra)["equivalences"]["constructions"]
    wrow = [r for r in e["rows"] if r["kind"] == "window"]
    check("double glazing with renamed layers: the U-factor and SHGC from EnergyPlus are the same", wrow and wrow[0]["same"] and wrow[0]["source"] == "EnergyPlus", e)
    e = run(base + win("2.7", "0.76"), base + layered, extra)["equivalences"]["constructions"]
    wrow = [r for r in e["rows"] if r["kind"] == "window"]
    check("simple glazing against layered glazing: both read by EnergyPlus, compared by U and SHGC", wrow and wrow[0].get("source") == "EnergyPlus" and "u_candidate" in wrow[0], e)
else:
    print("skipped: the EnergyPlus tests of layered glazing (no program or no weather file)")

print("\n%d failure(s)" % len(FAILS) if FAILS else "\nall tests passed")
sys.exit(1 if FAILS else 0)
