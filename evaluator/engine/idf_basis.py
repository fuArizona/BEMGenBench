"""idf_basis.py - does a field of an IDF have a DOCUMENTARY BASIS? (the rules of the skill idf_doc_compare)

Every non-blank field of an object (the name field excepted) gets one of three answers:
  doc    the field has a documentary basis: it takes part in the comparison
  nodoc  it has none: it does not take part
  undet  undetermined: the IDF does not say and nobody has decided yet (excluded from the score until it is decided)

Order of the rules (the user's rules of 2026-11-17):
  1. the comment of the field (or, when the field has no note, the comment on the class line of its object) says that the value comes from the original documents   -> doc
  2. the comment says that it is an assumption, an EnergyPlus requirement / addition / default, "not in the documents", a value kept from the prototype  -> nodoc
  3. no note at all, or a note that decides neither way (for example `Derived from: X = 5 ft x 0.3048 = 1.524 m`):
       a. the value is the EnergyPlus default of the field (the schema = the IDD)                                          -> nodoc  (EnergyPlus default)
       b. a DECISIONS file (--decisions) has a rule for the class and field: it was made by looking the group up in the original documents or the IDD   -> doc / nodoc
       c. otherwise                                                                                                           -> undet  (rule 4: without the original documents the comments are the only evidence)
A note that matches both lists (`Source: ASHRAE Handbook ...; not in the xlsx or the PDF`) is nodoc: the negation wins.

Decisions file (JSON): {"ignore_classes": ["HVACTemplate:*"], "rules": [{"class": "Zone", "field": "multiplier", "basis": "doc", "file": "both", "reason": "xlsx raw_data column G"}, ...]}
  class   a class name (not case-sensitive) or `*`;   field   the key of the field (as printed in the report; fnmatch pattern, `*` = any): `vertices[*]/vertex_x_coordinate`
  file    `reference`, `candidate` or `both` (default both);   basis   doc | nodoc;   reason   free text (kept in the report).
  The first rule that matches wins. A rule never overrides rule 1 or 2 (the comment) or 3a.
"""
import fnmatch
import json
import re

import idf_values as V

# a note that says: the value does NOT come from the documents (checked first)
NODOC = [
    r"\bnot\s+(?:given\s+|stated\s+|found\s+|specified\s+|available\s+)?(?:in|by|from)\s+(?:the\s+|any\s+)?(?:input\s+|original\s+)?(?:xlsx|pdf|documents?|nrel|scorecards?|description|inputs?)\b",
    r"\bnot\s+in\s+(?:the\s+)?(?:xlsx|pdf)\b",
    r"\bnot\s+(?:documented|documentary)\b",
    r"\bassum(?:ed|ption|es|e)\b",
    r"\bguess(?:ed)?\b", r"\bestimat(?:ed|e)\b", r"\bplaceholder\b", r"\barbitrar", r"\bunknown\b",
    r"^\s*default\b", r"\benergyplus\s+(?:default|needs|requires|required|adds|added|sets)\b", r"\bdefault\s+of\s+energyplus\b", r"\bdefault\s+(?:value\s+)?of\s+the\s+(?:idd|field|schema)\b",
    r"\brequired\s+by\s+(?:energyplus|the\s+template|the\s+idd|the\s+schema)\b", r"\bneeded\s+by\s+(?:energyplus|the\s+template)\b", r"^\s*required\b",
    r"\bchoice\s+that\s+the\s+template\s+needs\b",
    r"^\s*kept\b", r"\bkept\s*:", r"\bleft\s+blank\b", r"\bprototype\s+value\b", r"\bnot\s+from\s+the\s+documents?\b",
    r"\badded\s+by\s+(?:energyplus|expandobjects)\b", r"\bexpandobjects\b",
    r"^\s*not\s+in\b", r"\bnot\s+in\s+[\w\-. ]+\.(?:txt|png|jpe?g|csv|docx?|xlsx?|pdf|md|xml|json|toml)\b",      # "Not in input1.txt: ..."
]
# a note that says: the value comes from a document
DOC = [
    r"\bxlsx\b", r"\bpdf\b", r"\bnrel\b", r"\bpnnl\b", r"\bscorecards?\b", r"\braw_data\b", r"\bschedule\s+summary\b", r"\bbuilding\s+summary\b",
    r"\b(?:input|original|source)\s+documents?\b", r"\bthe\s+documents?\b", r"\bdocuments?\s*[:(]", r"\btable\s+[a-z]?-?\d+\b", r"\bdocx\b", r"\bgbxml\b", r"\bepc\b", r"\bhpxml\b",
    r"\b[\w\-]+\.(?:txt|png|jpe?g|csv|docx?|xlsx?|pdf|md|xml|json|toml)\b",      # a note that names an input file (input1.txt, info.txt, floorplan_area.png)
    r"^\s*source\s*:",
]
_NODOC = [re.compile(p, re.I) for p in NODOC]
_DOC = [re.compile(p, re.I) for p in DOC]


def note_of(comment):
    """The NOTE of a field comment: `- Name  Source: xlsx ...` -> `Source: xlsx ...` (the field label, then two or more blanks, then the note); a comment that is only the label -> ''.
    A comment without the `-` after the `!` (a free comment) is all note."""
    c = (comment or "").strip()
    if not c:
        return ""
    if c.startswith("-"):
        c = c[1:].strip()
        parts = re.split(r"\s{2,}", c, maxsplit=1)
        return parts[1].strip() if len(parts) > 1 else ""
    return c


def classify_note(note):
    """(basis or None, reason) from one note."""
    if not note:
        return None, ""
    for p in _NODOC:
        if p.search(note):
            return "nodoc", "comment: %s" % note[:90]
    for p in _DOC:
        if p.search(note):
            return "doc", "comment: %s" % note[:90]
    return None, "note without a verdict: %s" % note[:90]


def load_decisions(path):
    if not path:
        return []
    d = json.load(open(path, encoding="utf8"))
    rules = d["rules"] if isinstance(d, dict) else d
    out = []
    for r in rules:
        if r.get("basis") not in ("doc", "nodoc"):
            raise ValueError("decision rule %r: basis must be doc or nodoc" % (r,))
        out.append(dict(cls=(r.get("class") or "*").lower(), field=r.get("field") or "*", basis=r["basis"], file=r.get("file", "both"), reason=r.get("reason", "")))
    return out


def load_ignored(path):
    """The `ignore_classes` list of a decisions file (class name patterns left out of the comparison in both files), or []."""
    if not path:
        return []
    d = json.load(open(path, encoding="utf8"))
    return list(d.get("ignore_classes", [])) if isinstance(d, dict) else []


def generic_key(key):
    """vertices[12]/vertex_x_coordinate -> vertices[*]/vertex_x_coordinate (the field of a group, for the decision lists)."""
    return re.sub(r"\[\d+\]", "[*]", key)


def _decide(rules, cls, key, who):
    for r in rules:
        if r["file"] not in ("both", who):
            continue
        if r["cls"] not in ("*", cls.lower()):
            continue
        if fnmatch.fnmatchcase(key, r["field"]) or fnmatch.fnmatchcase(generic_key(key), r["field"]):
            return r
    return None


def annotate(flat, who, rules=(), tol=0.01):
    """Sets o["basis"] = {field key: (doc|nodoc|undet, source, reason)} on every object of the Flat. Returns the counters."""
    stat = dict(doc=0, nodoc=0, undet=0, by_source={})
    for o in flat.objects:
        basis = {}
        oc_basis, oc_reason = classify_note(note_of(o.get("obj_comment", "")))
        for k, v in o["fields"].items():
            if (k == "name" and o["info"] and o["info"]["named"]) or V.is_blank(v):
                continue
            note = note_of(o["comments"].get(k, ""))
            b, why = classify_note(note)
            src = "comment"
            if b is None and not note and oc_basis:
                b, why, src = oc_basis, oc_reason.replace("comment:", "comment of the class line:"), "class-line comment"
            if b is None:
                prop = V.field_prop(o["info"], k) if o["info"] else None
                if prop is not None and V.default_of(prop) is not None and V.equals_default(v, prop, tol):
                    b, why, src = "nodoc", "the value is the EnergyPlus default of the field", "default"
            if b is None:
                r = _decide(rules, o["cls"], k, who)
                if r is not None:
                    b, why, src = r["basis"], "decision: %s" % (r["reason"] or "rule of the decisions file"), "decision"
            if b is None:
                b, why, src = "undet", why or "no comment", "undetermined"
            basis[k] = (b, src, why)
            stat[b] += 1
            stat["by_source"][src] = stat["by_source"].get(src, 0) + 1
        o["basis"] = basis
    return stat


def undetermined_groups(flat, limit_examples=4):
    """[{cls, field, count, distinct_values, examples}] of the fields that are still undetermined, largest first."""
    g = {}
    for o in flat.objects:
        for k, (b, src, why) in o.get("basis", {}).items():
            if b != "undet":
                continue
            row = g.setdefault((o["cls"], generic_key(k)), dict(cls=o["cls"], field=generic_key(k), count=0, examples=[], values=set()))
            row["count"] += 1
            row["values"].add(o["fields"][k])
            if len(row["examples"]) < limit_examples:
                row["examples"].append(dict(object=o.get("name") or o.get("identity") or "", value=o["fields"][k], note=why if why.startswith("note") else ""))
    out = []
    for row in g.values():
        row["distinct_values"] = len(row.pop("values"))
        out.append(row)
    return sorted(out, key=lambda r: (-r["count"], r["cls"], r["field"]))
