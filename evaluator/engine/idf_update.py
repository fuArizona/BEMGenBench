#!/usr/bin/env python3
"""idf_update.py - brings an IDF of an older EnergyPlus version up to a newer one with the transition programs of the local EnergyPlus installations (the programs of IDFVersionUpdater).

  tuple_of(text_version)                    "23.1" / "23.1.0" -> (23, 1)
  available_steps()                         {(from): dict(to, exe, idd_from, idd_to, csv)} of every local installation (PreProcess/IDFVersionUpdater)
  plan(v_from, v_to)                        the list of steps from one version to the other, or None when the local programs do not reach it
  choose_target(vr, vc)                     the version both files are brought to (see below)
  upgrade(text, v_from, v_to)               -> dict(text, steps, reason): the text of the IDF in version v_to

Which version: the HIGHER of the two versions of the files (23.1 and 26.2 -> 26.2; 23.1 and 22.2 -> 23.1). The lower file is upgraded step by step (23.1 -> 23.2 -> 24.1 -> ...); the higher file is never
changed and a file is never downgraded. When the local programs have no chain from the lower version to the higher one the comparison stops with a message.
Every step runs in a temporary folder (the program, its two IDD files and the report-variable table are COPIED there): the installation is only read, never written. The input text is not changed; the
upgraded text is returned (the caller writes it next to the report). A transition that exits with an error, or reports Severe errors, stops the upgrade (reason)."""
import glob
import os
import re
import shutil
import subprocess
import tempfile

import idf_schema


def tuple_of(v):
    m = re.match(r"\s*(\d+)\.(\d+)", str(v or ""))
    return (int(m.group(1)), int(m.group(2))) if m else None


def _tag(t):
    return "V%d-%d-0" % t


def _roots():
    out = []
    for r in [x for g in idf_schema.standard_install_globs() for x in sorted(glob.glob(g), reverse=True)] + [os.environ.get("ENERGYPLUS_DIR") or ""]:
        if r and os.path.isdir(os.path.join(r, "PreProcess", "IDFVersionUpdater")) and r not in out:
            out.append(r)
    return out


def available_steps():
    """{(from): dict(to, exe, idd_from, idd_to, csv)}: one step per version, taken from the newest installation that has the program and both IDD files"""
    steps = {}
    for r in _roots():
        d = os.path.join(r, "PreProcess", "IDFVersionUpdater")
        for exe in glob.glob(os.path.join(d, "Transition-V*-to-V*.exe")):
            m = re.match(r"Transition-V(\d+)-(\d+)-\d+-to-V(\d+)-(\d+)-\d+\.exe$", os.path.basename(exe))
            if not m:
                continue
            a, b = (int(m.group(1)), int(m.group(2))), (int(m.group(3)), int(m.group(4)))
            ia, ib = os.path.join(d, _tag(a) + "-Energy+.idd"), os.path.join(d, _tag(b) + "-Energy+.idd")
            if a in steps or not (os.path.isfile(ia) and os.path.isfile(ib)):
                continue
            csv = os.path.join(d, "Report Variables %d-%d-0 to %d-%d-0.csv" % (a + b))
            steps[a] = dict(to=b, exe=exe, idd_from=ia, idd_to=ib, csv=csv if os.path.isfile(csv) else None)
    return steps


def plan(v_from, v_to):
    st = available_steps()
    chain, cur = [], v_from
    while cur != v_to:
        s = st.get(cur)
        if s is None or s["to"] > v_to or len(chain) > 60:
            return None
        chain.append((cur, s))
        cur = s["to"]
    return chain


def choose_target(vr, vc):
    """(target version tuple, who is upgraded: 'reference' | 'candidate' | None) for two version tuples; None target when a version is missing"""
    if vr is None or vc is None:
        return None, None
    if vr == vc:
        return vr, None
    return (vr, "candidate") if vr > vc else (vc, "reference")


def upgrade(text, v_from, v_to):
    res = dict(text=None, steps=[], reason=None)
    ch = plan(v_from, v_to)
    if ch is None:
        known = sorted("%d.%d" % k for k in available_steps())
        res["reason"] = "no chain of transition programs from %d.%d to %d.%d among the local installations (starting versions available: %s)" % (v_from + v_to + (", ".join(known) or "none",))
        return res
    tmp = tempfile.mkdtemp(prefix="idfupd_")
    try:
        cur = text
        for a, s in ch:
            for f in os.listdir(tmp):
                os.remove(os.path.join(tmp, f))
            for src in (s["exe"], s["idd_from"], s["idd_to"], s["csv"]):
                if src:
                    shutil.copy(src, tmp)
            with open(os.path.join(tmp, "in.idf"), "wb") as f:
                f.write(cur.encode("utf-8"))
            p = subprocess.run([os.path.join(tmp, os.path.basename(s["exe"])), "in.idf"], cwd=tmp, capture_output=True, text=True, errors="replace", timeout=600)
            out = p.stdout + p.stderr
            m = re.search(r"Conversion Completed Successfully--\s*(\d+) Warning;\s*(\d+) Severe", out)
            step = dict(from_version="%d.%d" % a, to_version="%d.%d" % s["to"], exit_code=p.returncode, warnings=int(m.group(1)) if m else None, severe=int(m.group(2)) if m else None,
                        program=os.path.basename(s["exe"]), report_variable_table=bool(s["csv"]))
            step["warning_lines"] = sorted({l.split("** Warning **", 1)[1].strip() for l in out.splitlines() if "** Warning **" in l})[:4]
            step["severe_lines"] = sorted({l.split("** Severe  **", 1)[1].strip() for l in out.splitlines() if "** Severe  **" in l})[:4]      # reported, not a failure: a partial file (no Building ...) gets Severe messages and is still converted
            res["steps"].append(step)
            raw = open(os.path.join(tmp, "in.idf"), "rb").read()
            nxt = None
            for enc in ("utf-8-sig", "cp1252"):
                try:
                    nxt = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            vm = re.search(r"^\s*Version\s*,\s*(\d+\.\d+)", nxt or "", re.M | re.I)
            ok_version = bool(vm) and tuple_of(vm.group(1)) == s["to"]
            # some transition programs (23.2 -> 24.1) print no `Conversion Completed Successfully` line: success = exit 0, no Fatal, and the result has the new Version; Severe messages are listed in the report
            if p.returncode != 0 or "** Fatal **" in out or not ok_version:
                res["reason"] = "the transition %s -> %s failed (exit %s, Version of the result %s): %s" % (step["from_version"], step["to_version"], p.returncode, vm.group(1) if vm else None, out.strip()[-300:].replace("\n", " | "))
                return res
            cur = nxt
        res["text"] = cur
        return res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
