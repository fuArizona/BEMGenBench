#!/usr/bin/env python3
"""Tests of the evaluator engine (synthetic IDFs, no EnergyPlus run needed for the comparison). python evaluator/tests/test_engine.py (from the root of the repository)"""
import glob
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import idf_basis  # noqa: E402
import idf_doc_compare  # noqa: E402

FAILS = []


def check(name, cond, info=""):
    print(("ok   " if cond else "FAIL ") + name + (("  " + str(info)) if (info and not cond) else ""))
    if not cond:
        FAILS.append(name)


# ---------------------------------------------------------------- the comment rules
nd = lambda c: idf_basis.classify_note(idf_basis.note_of(c))[0]
check("note_of: label only -> no note", idf_basis.note_of("- Name") == "")
check("note_of: label + note", idf_basis.note_of("- U-Factor {W/m2-K}  Source: NREL PDF Table 24") == "Source: NREL PDF Table 24")
check("rule 1: Source xlsx -> doc", nd("- Multiplier  Source: xlsx raw_data!G269 Multipliers = 1.") == "doc")
check("rule 1: Source PDF table -> doc", nd("- U  Source: NREL PDF Table 24, p.38") == "doc")
check("rule 2: Not in the documents -> nodoc", nd("- COP  Not in the documents: EnergyPlus requires a COP.") == "nodoc")
check("rule 2: assumed -> nodoc", nd("- R  the resistance 0.2 m2-K/W is assumed") == "nodoc")
check("rule 2: Default -> nodoc", nd("- X  Default: the value equals the EnergyPlus default of this optional field.") == "nodoc")
check("rule 2: Kept prototype value -> nodoc", nd("- X  Kept: prototype value, not in the xlsx or the PDF.") == "nodoc")
check("the negation wins over the document name", nd("- X  Source: ASHRAE Handbook 2005; not in the xlsx or the PDF.") == "nodoc")
check("Derived from a ft x 0.3048 conversion -> no verdict", nd("- X  Derived from: X = 9 ft x 0.3048 = 2.7432 m.") is None)
check("no note -> no verdict", nd("- X") is None)
check("a note that names an input file is a document source (Derived from input1.txt)", nd("- X  Derived from input1.txt: at home after 17:00 (1.0)") == "doc")
check("Source: with an input file -> doc", nd("- X  Source: info.txt, one air volume (floorplan_area.png)") == "doc")
check("Kept: not in input1.txt -> nodoc", nd("- X  Kept: not in input1.txt; Gallup NM EPW header") == "nodoc")
check("Not in input1.txt -> nodoc", nd("- X  Not in input1.txt: left blank = EnergyPlus default (0.04)") == "nodoc")

# ---------------------------------------------------------------- a synthetic pair
HEAD = "Version,\n 23.1;\n\nBuilding,\n B;\n\nGlobalGeometryRules,\n UpperLeftCorner, Counterclockwise, Relative;\n\nZone,\n Z1,\n 0,0,0,0,1,1;\n\n"


def sched(rows):
    head = "Schedule:Compact," + chr(10) + " S1," + chr(10) + " ," + chr(10) + " Through: 12/31," + chr(10) + " For: Weekdays SummerDesignDay WinterDesignDay," + chr(10)
    lines = []
    for i, (u, v, note) in enumerate(rows):
        end = ";" if i == len(rows) - 1 else ","
        lines.append(" %s,%s%s   !- Field %d  %s" % (u, v, end, i, note) + chr(10))
    return head + "".join(lines) + chr(10)


def build(win_u, win_note, extra_note, light, sched_rows, light_kind="Watts/Area"):
    t = HEAD
    t += "WindowMaterial:SimpleGlazingSystem,\n Glz,\n %s,   !- U-Factor  %s\n 0.4;   !- SHGC  %s\n\n" % (win_u, win_note, extra_note)
    t += "Lights,\n L1,\n Z1,\n S1,\n %s,\n %s,   !- value  %s\n\n" % (light_kind, light[0], light[1]) if False else ""
    return t + sched(sched_rows)


def run(a_text, b_text, extra=()):
    d = tempfile.mkdtemp()
    fa, fb = os.path.join(d, "a.idf"), os.path.join(d, "b.idf")
    open(fa, "w").write(a_text)
    open(fb, "w").write(b_text)
    rc = idf_doc_compare.main(["--reference", fa, "--candidate", fb, "--out", d, "--name", "t"] + list(extra))
    j = json.load(open(sorted(glob.glob(os.path.join(d, "t.idf_doc_compare_report.json")))[0]))
    return rc, j, d


DOC = "Source: xlsx raw_data row 1"
rowsA = [("Until: 7:00", "0.1", DOC), ("Until: 24:00", "0.9", DOC)]
base = build("3.2366", DOC, "Not in the documents: EnergyPlus needs it.", None, rowsA)

# 1. identical files: 100 %
rc, j, _ = run(base, base)
check("identical files: exit 0 and 100 %", rc == 0 and j["score"]["rate"] == 1.0 and j["score"]["keys"] >= 3, j["score"])

# 2. a documented number within 1 %: same; 5 % off: different
rc, j, _ = run(base, build("3.254", DOC, "Not in the documents: EnergyPlus needs it.", None, rowsA))
check("documented number 0.5 % off: same", j["score"]["rate"] == 1.0, j["score"])
rc, j, _ = run(base, build("3.40", DOC, "Not in the documents: EnergyPlus needs it.", None, rowsA))
check("documented number 5 % off: one key different", j["score"]["same"] == j["score"]["keys"] - 1, j["score"])

# 3. a value that is NOT documented may differ without cost
a = build("3.2366", DOC, "Not in the documents: EnergyPlus needs it.", None, rowsA).replace(" 0.4;", " 0.4;")
b = build("3.2366", DOC, "Not in the documents: EnergyPlus needs it.", None, rowsA).replace(" 0.4;", " 0.7;")
rc, j, _ = run(a, b)
check("an undocumented (nodoc) value that differs is not compared", j["score"]["rate"] == 1.0, j["score"])

# 4. an undetermined field (no note) is left out; a decisions file can put it in
a2 = a.replace("0.4;   !- SHGC  Not in the documents: EnergyPlus needs it.", "0.4;   !- SHGC")
b2 = b.replace("0.7;   !- SHGC  Not in the documents: EnergyPlus needs it.", "0.7;   !- SHGC")
rc, j, d = run(a2, b2)
check("an undetermined field is left out of the score", j["score"]["rate"] == 1.0 and j["reference"]["basis"]["undet"] >= 1, (j["score"], j["reference"]["basis"]))
dec = os.path.join(d, "dec.json")
json.dump({"rules": [{"class": "WindowMaterial:SimpleGlazingSystem", "field": "solar_heat_gain_coefficient", "basis": "doc", "reason": "PDF Table 25"}]}, open(dec, "w"))
rc, j, _ = run(a2, b2, ["--decisions", dec])
check("a decision (doc) puts it in: 0.4 against 0.7 is now a difference", j["score"]["same"] == j["score"]["keys"] - 1 and j["decisions"]["rules"] == 1, j["score"])

# 5. a schedule: the documented clause is compared by its hourly values; a design-day clause of one file is a choice
rowsB = [("Until: 7:00", "0.1", DOC), ("Until: 24:00", "0.9", DOC)]
tB = "Version,\n 23.1;\n\nBuilding,\n B;\n\nGlobalGeometryRules,\n UpperLeftCorner, Counterclockwise, Relative;\n\nZone,\n Z1,\n 0,0,0,0,1,1;\n\n"
tA = tB
tA += ("Schedule:Compact,\n S1,\n ,\n Through: 12/31,\n For: Weekdays,\n Until: 7:00,0.1,   !- F  %s\n Until: 24:00,0.9,   !- F  %s\n For: SummerDesignDay WinterDesignDay,\n Until: 24:00,1;   !- F  Kept: design day of the prototype\n\n" % (DOC, DOC))
tB += ("Schedule:Compact,\n S1,\n ,\n Through: 12/31,\n For: Weekdays SummerDesignDay WinterDesignDay,\n Until: 7:00,0.1,   !- F  %s\n Until: 24:00,0.9;   !- F  %s\n\n" % (DOC, DOC))
rc, j, _ = run(tA, tB)
check("schedule: same documented weekday values written in another clause layout: 100 %", j["score"]["rate"] == 1.0 and j["score"]["keys"] == 4, j["score"])
tC = tB.replace("Until: 7:00,0.1", "Until: 7:00,0.5")
rc, j, _ = run(tA, tC)
check("schedule: a documented hourly value that differs: the clause is lost", j["score"]["same"] < j["score"]["keys"], j["score"])

# 6. the same load with another calculation method (a count against a density): the intensity decides
zone = "Zone,\n Z1,\n 0,0,0,0,1,1;\n\nBuildingSurface:Detailed,\n Fl,\n Floor,\n C1,\n Z1,\n ,\n Adiabatic,\n ,\n NoSun,\n NoWind,\n AutoCalculate,\n 4,\n 0,10,0,\n 0,0,0,\n 10,0,0,\n 10,10,0;\n\n"
peopleA = "People,\n P1,\n Z1,\n S1,\n People,\n 5,   !- n  Source: xlsx raw_data M\n ,\n ;\n\n"
peopleB = "People,\n P1,\n Z1,\n S1,\n Area/Person,\n ,\n ,\n 20;   !- m2 per person  Source: xlsx raw_data M\n\n"
mk = lambda p: HEAD.replace("Zone,\n Z1,\n 0,0,0,0,1,1;\n\n", zone) + p + "Schedule:Compact,\n S1,\n ,\n Through: 12/31,\n For: AllDays,\n Until: 24:00,1;\n\n"
rc, j, _ = run(mk(peopleA), mk(peopleB))
check("load: 5 people in 100 m2 = 20 m2 per person: same", j["score"]["rate"] == 1.0 and j["score"]["keys"] >= 1, j["score"])
rc, j, _ = run(mk(peopleA), mk(peopleB.replace("20;", "25;")))
check("load: 25 m2 per person is a difference", j["score"]["same"] < j["score"]["keys"], j["score"])

# 7. a documented object that one file lacks is a loss (union), and ignore-class can set a class aside
extra = "Material,\n M1,\n Rough,\n 0.0254,   !- thickness  Source: xlsx Building Summary C9\n 0.7, 1800, 900;\n\n"
rc, j, _ = run(base + extra, base)
check("a documented object missing in the other file is a loss", j["score"]["same"] == j["score"]["keys"] - 1, j["score"])
rc, j, _ = run(base + extra, base, ["--ignore-class", "Material"])
check("--ignore-class sets the class aside (and says how many keys)", j["score"]["rate"] == 1.0 and j["ignored_classes"]["documentary_keys_removed"].get("Material") == 1, j["ignored_classes"])
rc, j, _ = run(base + extra, base, ["--universe", "intersection"])
check("universe intersection: a documented value that one file lacks is not counted", j["score"]["rate"] == 1.0, j["score"])

# 8. the HVAC is compared by TYPE: HVACTemplate against real objects of the same kind of system
tmpl_vav = "HVACTemplate:System:VAV,\n Sys1,\n ,\n ,\n ,\n ,\n ,\n ,\n ,\n ,\n NoEconomizer;   !- Economizer  Source: xlsx HVAC System Type 7\n\n"
real_vav = "AirTerminal:SingleDuct:VAV:Reheat,\n Term1;\n\nAirLoopHVAC,\n Loop1;\n\n"
real_hp = "AirLoopHVAC:UnitaryHeatPump:AirToAir,\n HP1;\n\n"
check("HVAC by type: HVACTemplate VAV against real VAV terminals: same", run(HEAD + tmpl_vav, HEAD + real_vav)[1]["score"]["rate"] == 1.0)
rc, j, _ = run(HEAD + tmpl_vav, HEAD + real_hp)
check("HVAC by type: VAV against an air-to-air heat pump: the type is a difference", j["score"]["same"] < j["score"]["keys"] and any(x["kind"] == "hvac_type" for x in j["losses"]), j["score"])
rc, j, _ = run(HEAD + tmpl_vav, HEAD + real_vav, ["--hvac-by-type", "off"])
check("--hvac-by-type off compares the fields (the template field has no counterpart)", j["score"]["rate"] < 1.0, j["score"])

# 9. one load split in two objects with the same schedule, and a zone multiplier written as a ZoneGroup
sch_ok = "Schedule:Compact,\n S1,\n ,\n Through: 12/31,\n For: AllDays,\n Until: 24:00,1;\n\n"
sch_ok2 = "Schedule:Compact,\n S2,\n ,\n Through: 12/31,\n For: Weekdays SummerDesignDay,\n Until: 24:00,1,\n For: AllOtherDays,\n Until: 24:00,1;\n\n"
lights_one = "Lights,\n L1,\n Z1,\n S1,\n Watts/Area,\n ,\n 17.4375;   !- w  Source: xlsx raw_data L33\n\n"
lights_two = ("Lights,\n L1a,\n Z1,\n S1,\n Watts/Area,\n ,\n 16.46877;   !- w  Source: xlsx raw_data L33\n\n" + "Lights,\n L1b,\n Z1,\n S2,\n Watts/Area,\n ,\n 0.96875;   !- w  Source: xlsx raw_data L33\n\n")
mk2 = lambda body: HEAD.replace("Zone,\n Z1,\n 0,0,0,0,1,1;\n\n", zone) + body
rc, j, _ = run(mk2(sch_ok + sch_ok2 + lights_one), mk2(sch_ok + sch_ok2 + lights_two))
check("a load split in two objects with the same hourly schedule = the one load (17.4375 = 16.46877 + 0.96875)", j["score"]["rate"] == 1.0 and j["score"]["keys"] >= 1, j["score"])
rc, j, _ = run(mk2(sch_ok + sch_ok2 + lights_one), mk2(sch_ok + sch_ok2 + lights_two.replace("0.96875", "2.5")))
check("the split loads add up to another total: a difference", j["score"]["same"] < j["score"]["keys"], j["score"])
zA = HEAD.replace("Zone,\n Z1,\n 0,0,0,0,1,1;\n\n", "Zone,\n Z1,\n 0,\n 0,0,0,\n ,\n 2;   !- multiplier  Source: xlsx raw_data G\n\n")
zB = HEAD + "ZoneList,\n ML,\n Z1;\n\nZoneGroup,\n MG,\n ML,\n 2;   !- m  Source: xlsx raw_data G\n\n"
rc, j, _ = run(zA, zB)
check("zone multiplier 2 on the zone = a ZoneGroup multiplier 2 (effective multiplier)", j["score"]["rate"] == 1.0 and j["score"]["keys"] >= 1, j["score"])

# 10. EnergyPlus reads the first letters of the schedule keywords: `For AllOtherDays` and `Until 24:00` without a colon are the same as with it
import idf_sched  # noqa: E402
cl = idf_sched.compact_clauses(["S", "", "Through: 12/31", "For: Weekdays", "Until: 7:00", "0.33", "Until: 24:00", "1", "For AllOtherDays", "Until 24:00", "0.5"])
check("Schedule:Compact keywords without a colon are read (For AllOtherDays, Until 24:00)", cl is not None and len(cl) == 2 and "saturday" in cl[1]["days"] and cl[1]["hours"][0] == 0.5, cl)
sA = HEAD + "Schedule:Compact,\n S1,\n ,\n Through: 12/31,\n For: Weekdays,\n Until: 24:00,1,   !- a  Source: xlsx Schedule Summary row 1\n For AllOtherDays,\n Until: 24:00,0.5;   !- b  Source: xlsx Schedule Summary row 2\n\n"
sB = sA.replace("For AllOtherDays", "For: AllOtherDays")
rc, j, _ = run(sA, sB)
check("a file that writes `For AllOtherDays` against one that writes `For: AllOtherDays`: the same schedule, 100 %", j["score"]["rate"] == 1.0 and j["score"]["keys"] >= 4, j["score"])

# 11. the same infiltration written with another calculation method
def room(infil):
    d = 10.0
    surf = "BuildingSurface:Detailed,\n Fl,\n Floor,\n C1,\n Z1,\n ,\n Ground,\n ,\n NoSun,\n NoWind,\n AutoCalculate,\n 4,\n 0,10,0,\n 0,0,0,\n 10,0,0,\n 10,10,0;\n\n"
    walls = [((0, 0, 10, 0)), ((10, 0, 10, 10)), ((10, 10, 0, 10)), ((0, 10, 0, 0))]
    for i, (x1, y1, x2, y2) in enumerate(walls):
        surf += "BuildingSurface:Detailed,\n W%d,\n Wall,\n C1,\n Z1,\n ,\n Outdoors,\n ,\n SunExposed,\n WindExposed,\n AutoCalculate,\n 4,\n %g,%g,3,\n %g,%g,0,\n %g,%g,0,\n %g,%g,3;\n\n" % (i, x1, y1, x1, y1, x2, y2, x2, y2)
    zone = "Zone,\n Z1,\n 0,\n 0,0,0,\n ,\n 1,\n 3,\n 300;\n\n"
    sched = "Schedule:Compact,\n S1,\n ,\n Through: 12/31,\n For: AllDays,\n Until: 24:00,1;\n\n"
    return "Version,\n 23.1;\n\nBuilding,\n B;\n\nGlobalGeometryRules,\n UpperLeftCorner, Counterclockwise, Relative;\n\n" + zone + surf + sched + infil


def infil(method, per, field_pos):
    vals = ["", "", "", ""]
    vals[field_pos] = "%s;   !- value  Source: xlsx raw_data R" % per
    return "ZoneInfiltration:DesignFlowRate,\n I1,\n Z1,\n S1,\n %s,\n %s,\n %s,\n %s,\n %s\n\n" % ((method,) + tuple(v if v else "" for v in vals[:3]) + (vals[3] if vals[3] else ";",))


ref_i = room(infil("Flow/ExteriorWallArea", "0.001", 2))      # 120 m2 of exterior wall: 0.12 m3/s; 100 m2 floor; 300 m3
for name, cand_i, expect in (
    ("Flow/Zone 0.12 m3/s", "ZoneInfiltration:DesignFlowRate,\n I1,\n Z1,\n S1,\n Flow/Zone,\n 0.12;\n\n", True),
    ("Flow/Area 0.0012 m3/s-m2 of floor", "ZoneInfiltration:DesignFlowRate,\n I1,\n Z1,\n S1,\n Flow/Area,\n ,\n 0.0012;\n\n", True),
    ("1.44 air changes per hour in 300 m3", "ZoneInfiltration:DesignFlowRate,\n I1,\n Z1,\n S1,\n AirChanges/Hour,\n ,\n ,\n ,\n 1.44;\n\n", True),
    ("Flow/Zone 0.2 m3/s is another value", "ZoneInfiltration:DesignFlowRate,\n I1,\n Z1,\n S1,\n Flow/Zone,\n 0.2;\n\n", False),
):
    rc, j, _ = run(ref_i, room(cand_i))
    check("infiltration: " + name + (" = the reference (0.001 per m2 of exterior wall)" if expect else ": a difference"), (j["score"]["same"] == j["score"]["keys"]) == expect and j["score"]["keys"] >= 1, j["score"])

# 12. a zone that the candidate names in short (Z1_APT for Z1 Apartment): its loads are compared with the loads of the reference zone
LIGHTS = "Lights,\n L1,\n Z1,\n S1,\n Watts/Area,\n ,\n %s;   !- value  Source: xlsx raw_data R\n\n"
ref_z = room(LIGHTS % "10").replace("\n Z1,\n", "\n Z1 Apartment,\n")
for name, w, expect in (("10 W/m2 in the renamed zone", "10", True), ("20 W/m2 in the renamed zone", "20", False)):
    cand_z = room(LIGHTS % w).replace("\n Z1,\n", "\n Z1_APT,\n")
    rc, j, _ = run(ref_z, cand_z)
    check("renamed zone: " + name + (" = the reference" if expect else ": a difference"), (j["score"]["same"] == j["score"]["keys"]) == expect, str(j["score"]))

print("\n%d failure(s)" % len(FAILS) if FAILS else "\nall tests passed")
sys.exit(1 if FAILS else 0)
