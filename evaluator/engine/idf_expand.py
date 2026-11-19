"""idf_expand.py - EnergyPlus's own ExpandObjects on an IDF text (design doc, section 8): the HVACTemplate objects become the full HVAC objects, so that a file with templates can be compared with one
that has the real objects.

  expand(text, root)  -> dict(ran, expanded (text or None), messages [str], stdout, exit, reason)
  parse_messages(err_text)  the Output:PreprocessorMessage objects of expandedidf.err as [(severity, text)]

How ExpandObjects works (read 2026-10-15 in Documentation/AuxiliaryPrograms.pdf chapter 10, in RunEPlus.bat and by running it): no command-line arguments; it works in the CURRENT FOLDER: reads `in.idf`,
writes `expanded.idf` (a copy of the file with the HVACTemplate objects commented out and the new objects added; none is written when there is nothing to expand) and `expandedidf.err` (messages
for EnergyPlus). RunEPlus.bat copies `Energy+.idd` next to `in.idf` first; this does the same. The work is done in a temporary folder that is deleted afterwards; the installation is only run, never
modified, and the input text is not changed.
"""
import os
import re
import shutil
import subprocess
import tempfile


def exe_of(root):
    for n in ("ExpandObjects.exe", "ExpandObjects"):
        p = os.path.join(root, n)
        if os.path.isfile(p):
            return p
    return None


def parse_messages(err_text):
    """[(severity, text)] of the Output:PreprocessorMessage objects of expandedidf.err (preprocessor name, severity, message lines)."""
    out = []
    clean = "\n".join(l.split("!")[0] for l in err_text.splitlines())
    for blk in clean.split(";"):
        parts = [p.strip() for p in blk.strip().split(",")]
        if parts and parts[0].lower() == "output:preprocessormessage" and len(parts) >= 3:
            out.append((parts[2], " ".join(x for x in parts[3:] if x)))
    return out


def expand(text, root, timeout=180):
    res = dict(ran=False, expanded=None, messages=[], stdout="", exit=None, reason="")
    exe = exe_of(root)
    if exe is None:
        res["reason"] = "ExpandObjects was not found in %s" % root
        return res
    tmp = tempfile.mkdtemp(prefix="idfc_expand_")
    try:
        with open(os.path.join(tmp, "in.idf"), "w", encoding="utf8", newline="\n") as f:
            f.write(text)
        for n in ("Energy+.idd",):
            src = os.path.join(root, n)
            if os.path.isfile(src):
                shutil.copy(src, os.path.join(tmp, n))
        try:
            r = subprocess.run([exe], cwd=tmp, capture_output=True, text=True, timeout=timeout, errors="replace")
        except subprocess.TimeoutExpired:
            res["reason"] = "ExpandObjects did not end in %d s" % timeout
            return res
        res.update(ran=True, exit=r.returncode, stdout=(r.stdout or "").strip())
        ep = os.path.join(tmp, "expandedidf.err")
        if os.path.isfile(ep):
            res["messages"] = parse_messages(open(ep, encoding="utf8", errors="replace").read())
            if not res["messages"]:
                res["messages"] = [("Information", open(ep, encoding="utf8", errors="replace").read().strip()[:300])]
        xp = os.path.join(tmp, "expanded.idf")
        if os.path.isfile(xp):
            res["expanded"] = open(xp, encoding="utf8", errors="replace").read()
        if r.returncode != 0:
            res["reason"] = "ExpandObjects ended with exit code %s" % r.returncode
        elif any(s.lower().startswith("fatal") for s, _ in res["messages"]):
            res["reason"] = "ExpandObjects reported a Fatal message: %s" % "; ".join(t for s, t in res["messages"] if s.lower().startswith("fatal"))[:300]
        return res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
