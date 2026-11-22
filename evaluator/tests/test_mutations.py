#!/usr/bin/env python3
"""test_mutations.py - mutation tests of the evaluator.

A candidate is made from the REFERENCE IDF of a case by a known change, and `evaluate.py` scores it:
  - an INVARIANT change (a different writing of the same model: names, order, number format, case, comments, a copy of a schedule under another name ...) must leave the key score, the Object KVOR and the schedule
    score exactly as the unchanged reference has them (100 %);
  - a DEGRADING change (a value changed, an object or a schedule deleted ...) must lower them, by about the keys that the change touches.
A mutation that does not apply to a case (the case has no such object) is skipped and listed.

Usage (from anywhere):  python evaluator/tests/test_mutations.py [case_id ...]      default cases: doe_small_office doe_warehouse res_lupton_house
Needs the EnergyPlus install that evaluate.py needs (schema); about 1 second per mutation and case. A FAIL is a finding about the evaluator: a writing it does not treat as the same, or a loss it does not see."""
import json
import os
import random
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EVAL = os.path.join(ROOT, "evaluator", "evaluate.py")
FAILS, SKIPPED = [], []


# ------------------------------------------------------------------ text helpers
def ref_text(case):
    return open(os.path.join(ROOT, "cases", case, "reference", "reference.idf"), encoding="utf8", errors="replace").read()


def parse(text):
    """The objects of an IDF text as line ranges: [dict(start, end, cls, fields)]; a `!` starts a comment to the end of the line."""
    lines = text.split("\n")
    out, cur = [], None
    for i, l in enumerate(lines):
        code = l.split("!")[0]
        if not code.strip():
            continue
        if cur is None:
            cur = dict(start=i, code="")
        cur["code"] += code
        if ";" in code:
            cur["end"] = i
            parts = [x.strip() for x in cur["code"].replace(";", ",").split(",")]
            while parts and parts[-1] == "":
                parts.pop()
            cur["cls"], cur["fields"] = parts[0], parts[1:]
            out.append(cur)
            cur = None
    return lines, out


def evaluate(case, text):
    d = tempfile.mkdtemp()
    cand = os.path.join(d, "cand.idf")
    open(cand, "w", encoding="utf8", newline="\n").write(text)
    r = subprocess.run([sys.executable, EVAL, "--case", case, "--candidate", cand, "--out", os.path.join(d, "out"), "--top", "5000", "--no-run"], capture_output=True, text=True)
    p = os.path.join(d, "out", case + ".json")
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf8"))


def rename_word(text, old, new):
    return re.sub(r"(?<![\w:.\-])" + re.escape(old) + r"(?![\w:.\-])", new, text)


def rebuild(text, number_format=None, order=None):
    """The objects written again from their fields, comments dropped; number_format(token) -> token for a field that is a number; order(list) -> list of objects."""
    lines, objs = parse(text)
    if order:
        objs = order(objs)
    out = []
    for o in objs:
        f = [number_format(x) if (number_format and o["cls"].lower() != "version" and re.fullmatch(r"[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?", x)) else x for x in [o["cls"]] + o["fields"]]
        out.append(", ".join(f[:1] + f[1:]) + ";\n")
    return "\n".join(out)


def first_object(text, cls):
    lines, objs = parse(text)
    for o in objs:
        if o["cls"].lower() == cls.lower():
            return lines, o
    return lines, None


def delete_first(text, cls):
    lines, o = first_object(text, cls)
    if o is None:
        return None
    return "\n".join(lines[:o["start"]] + lines[o["end"] + 1:])


def scale_doc_number(text, cls, factor):
    """The first number of the first object of the class whose comment says `Source` (a documentary value), multiplied by factor."""
    lines, objs = parse(text)
    for o in objs:
        if o["cls"].lower() != cls.lower():
            continue
        for i in range(o["start"], o["end"] + 1):
            m = re.match(r"^(\s*)([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)(\s*[,;])(.*!.*Source.*)$", lines[i])
            if m and float(m.group(2)) != 0:
                lines[i] = "%s%r%s%s" % (m.group(1), float(m.group(2)) * factor, m.group(3), m.group(4))
                return "\n".join(lines)
    return None


def change_schedule_value(text):
    """The first hourly value of the first Schedule:Compact set to 0.99 (0.01 when it is 0.99 already). A value is written either on its own line or after its `Until:` on one line."""
    lines, objs = parse(text)
    for o in objs:
        if o["cls"].lower() != "schedule:compact":
            continue
        for i in range(o["start"], o["end"] + 1):
            m = re.match(r"^(\s*Until:\s*[\d:]+\s*,\s*)([-+]?\d+\.?\d*)(\s*[,;].*)$", lines[i], re.I) or re.match(r"^()([-+]?\d+\.?\d*)(\s*[,;].*)$", lines[i])
            if m:
                v = 0.01 if abs(float(m.group(2)) - 0.99) < 1e-9 else 0.99
                lines[i] = "%s%r%s" % (m.group(1), v, m.group(3))
                return "\n".join(lines)
    return None


def first_name(text, cls):
    lines, o = first_object(text, cls)
    return o["fields"][0] if o and o["fields"] else None


# ------------------------------------------------------------------ the mutations
def m_rename_schedule(t):
    n = first_name(t, "Schedule:Compact")
    return rename_word(t, n, "RENAMED_SCHEDULE_X") if n else None


def m_rename_zone(t):
    n = first_name(t, "Zone")
    return rename_word(t, n, "RENAMED_ZONE_X") if n else None


def m_rename_material(t):
    n = first_name(t, "Material")
    return rename_word(t, n, "RENAMED_MATERIAL_X") if n else None


def m_rename_construction(t):
    n = first_name(t, "Construction")
    return rename_word(t, n, "RENAMED_CONSTRUCTION_X") if n else None


def m_copy_schedule(t):
    """The loads that name the first schedule use an identical copy of it under another name."""
    lines, objs = parse(t)
    sched = next((o for o in objs if o["cls"].lower() == "schedule:compact"), None)
    if sched is None:
        return None
    name = sched["fields"][0]
    users = [o for o in objs if o["cls"].lower() in ("lights", "electricequipment", "people") and name in o["fields"]]
    if not users:
        return None
    out = list(lines)
    for o in users:
        for i in range(o["start"], o["end"] + 1):
            out[i] = rename_word(out[i], name, name + "_COPY")
    copy = [rename_word(l, name, name + "_COPY") for l in lines[sched["start"]:sched["end"] + 1]]
    return "\n".join(out[:sched["end"] + 1] + [""] + copy + [""] + out[sched["end"] + 1:])


def m_rename_surface(t):
    n = first_name(t, "BuildingSurface:Detailed")
    return rename_word(t, n, "RENAMED_SURFACE_X") if n else None


def m_days_written_out(t):
    """`For: Weekdays` written as the five days (the same day types)."""
    out = re.sub(r"(For:\s*)Weekdays\b", r"\1Monday Tuesday Wednesday Thursday Friday", t)
    return None if out == t else out


INVARIANT = [
    ("a surface renamed everywhere", m_rename_surface),
    ("`For: Weekdays` written as Monday ... Friday", m_days_written_out),
    ("a schedule renamed everywhere", m_rename_schedule),
    ("a zone renamed everywhere", m_rename_zone),
    ("a material renamed everywhere", m_rename_material),
    ("a construction renamed everywhere", m_rename_construction),
    ("a copy of a schedule under another name used by the loads", m_copy_schedule),
    ("all comments removed, one object per line", lambda t: rebuild(t)),
    ("the objects in reverse order", lambda t: rebuild(t, order=lambda l: list(reversed(l)))),
    ("the objects in random order", lambda t: rebuild(t, order=lambda l: random.Random(1).sample(l, len(l)))),
    ("numbers written with trailing zeros (0.5 as 0.5000)", lambda t: rebuild(t, number_format=lambda x: x + "0000" if "." in x and "e" not in x.lower() else x)),
    ("whole numbers written as 1.0", lambda t: rebuild(t, number_format=lambda x: x + ".0" if re.fullmatch(r"[-+]?\d+", x) and len(x) < 4 else x)),
    ("a documentary number 0.5 % off (inside the 1 % tolerance)", lambda t: scale_doc_number(t, "Lights", 1.005) or scale_doc_number(t, "ElectricEquipment", 1.005) or scale_doc_number(t, "Material", 1.005)),
    ("all text in upper case", lambda t: rebuild(t).upper()),
    ("all text in lower case", lambda t: rebuild(t).lower()),
    ("the comments replaced by other text", lambda t: "\n".join((l.split("!")[0] + "!- nothing to see here") if "!" in l else l for l in t.split("\n"))),
]

DEGRADING = [
    ("a Lights / ElectricEquipment / Material object deleted", lambda t: delete_first(t, "Lights") or delete_first(t, "ElectricEquipment") or delete_first(t, "Material"), "keys"),
    ("a documentary number 5 % off", lambda t: scale_doc_number(t, "Lights", 1.05) or scale_doc_number(t, "ElectricEquipment", 1.05) or scale_doc_number(t, "Material", 1.05), "keys"),
    ("a documentary number 50 % off", lambda t: scale_doc_number(t, "Lights", 1.5) or scale_doc_number(t, "ElectricEquipment", 1.5) or scale_doc_number(t, "Material", 1.5), "keys"),
    ("one hourly value of a schedule changed", change_schedule_value, "schedule"),
    ("the first schedule deleted", lambda t: delete_first(t, "Schedule:Compact"), "schedule"),
    ("a Material deleted (the constructions that use it are no longer the same)", lambda t: delete_first(t, "Material"), "objects"),
]


def sig(j):
    return (j["score"]["same"], j["score"]["keys"], (j.get("object_score") or {}).get("same"), (j.get("schedule_score") or {}).get("same"))


def check(name, cond, info=""):
    print(("ok   " if cond else "FAIL ") + name + (("   " + str(info)) if (info and not cond) else ""))
    if not cond:
        FAILS.append(name)


def run_case(case):
    t0 = ref_text(case)
    base = evaluate(case, t0)
    if base is None:
        check("%s: the unchanged reference could be scored" % case, False)
        return
    b = sig(base)
    check("%s: the unchanged reference scores 100 %%" % case, base["score"]["same"] == base["score"]["keys"], base["score"])
    for name, fn in INVARIANT:
        t = fn(t0)
        if t is None:
            SKIPPED.append("%s: %s" % (case, name))
            continue
        j = evaluate(case, t)
        got = sig(j) if j else None
        info = ""
        if j and got != b:
            info = "reference %s, candidate %s; first differences: %s" % (b, got, [(x["kind"], x["key"][:50], x["reference"], x["candidate"]) for x in j["differences"]["listed"][:3]])
        check("%s: invariant: %s" % (case, name), got == b, info or got)
    for name, fn, what in DEGRADING:
        t = fn(t0)
        if t is None:
            SKIPPED.append("%s: %s" % (case, name))
            continue
        j = evaluate(case, t)
        if j is None:
            check("%s: degrading: %s: could be scored" % (case, name), False)
            continue
        got = sig(j)
        lost = b[0] - got[0] + (b[1] - got[1])          # keys that are no longer the same (a deleted object also takes its keys out of the candidate side, not out of the universe)
        if what == "keys":
            ok = got[0] < b[0]
        elif what == "schedule":
            n_sched = (base.get("schedule_score") or {}).get("schedules") or 0
            ok = got[0] < b[0] and (got[3] < b[3] if n_sched else True)       # a case whose documents give no schedule has nothing to count as a schedule: the key score must drop
        else:
            ok = got[2] is not None and got[2] < b[2]
        check("%s: degrading: %s" % (case, name), ok, "reference %s, candidate %s" % (b, got))


def main():
    cases = sys.argv[1:] or ["doe_small_office", "doe_warehouse", "res_lupton_house"]
    for c in cases:
        run_case(c)
    if SKIPPED:
        print("\nskipped (the case has no such object): %d" % len(SKIPPED))
        for s in SKIPPED:
            print("  " + s)
    print("\n%d failure(s)" % len(FAILS) if FAILS else "\nall mutation tests passed")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
