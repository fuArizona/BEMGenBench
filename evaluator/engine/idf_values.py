"""idf_values.py - how one field value is compared in the aligned mode (design doc, section 6.2).

  base_field(key)                 the schema field of a flat key ("vertices[2]/vertex_y_coordinate" -> "vertex_y_coordinate", "data[3]" -> "field")
  field_prop(info, key)           the schema property of that field ({} when unknown)
  kind_of(info, key)              "ref" (a field that holds the name of another object: object_list in the schema), "node" (a node or node list name), "val" (anything else)
  default_of(prop)                the default of the schema for the field, or None
  values_equal(a, b, prop, tol)   the value rules: text trimmed, inner blanks collapsed, case-insensitive; numbers equal within a relative tolerance (and an absolute one: 1e-6, 1e-3 for a field in m);
                                  two writings of the same date are equal ("3/12", "March 12", "12 Mar"; also after "Through:"), and two `For:` day lists of a Schedule:Compact are equal when they
                                  hold the same day types Sunday ... Saturday ("For: AllDays" = the seven days written out; design days, holidays and custom days are the choice of a file)
  is_blank(x)

Everything here is deterministic and has no state; the rules are listed in the report.
"""
import re

import idf_sched

NODE_HINTS = ("node_name", "node_or_nodelist", "nodelist_name")
_NUM = re.compile(r"^\s*[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?\s*$")


def is_blank(x):
    return x is None or str(x).strip() == ""


def base_field(info, key):
    m = re.match(r"^(\w+)\[\d+\]/(\w+)$", key)
    if m:
        return m.group(2)
    m = re.match(r"^(\w+)\[\d+\]$", key)
    if m:
        return (info["ext_fields"][0] if info and info.get("ext_fields") else m.group(1))
    return key


def field_prop(info, key):
    if not info:
        return {}
    return info["props"].get(base_field(info, key)) or {}


def _alts(prop):
    return prop.get("anyOf") or [prop]


def kind_of(info, key):
    if not info:
        return "val"
    prop = field_prop(info, key)
    if any("object_list" in a for a in _alts(prop)):
        return "ref"
    b = base_field(info, key)
    if any(h in b for h in NODE_HINTS) or b.endswith("_node"):
        return "node"
    return "val"


def default_of(prop):
    for a in [prop] + _alts(prop):
        if "default" in a:
            return a["default"]
    return None


def unit_of(prop):
    for a in [prop] + _alts(prop):
        if a.get("units"):
            return a["units"]
    return None


def norm_text(x):
    return " ".join(str(x).split()).lower()


def as_number(x):
    s = str(x)
    if _NUM.match(s):
        return float(s)
    return None


_MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
_DOC_DAYS = idf_sched.DAYS[:7]
_DATE_NUM = re.compile(r"^(\d{1,2})\s*/\s*(\d{1,2})$")
_DATE_MD = re.compile(r"^([a-z]{3,9})\.?\s+(\d{1,2})$")
_DATE_DM = re.compile(r"^(\d{1,2})\s+([a-z]{3,9})\.?$")
_LEAD = re.compile(r"^(through|for)\s*:\s*(.*)$")


def _date(t):
    """(month, day) of a date written as m/d, Month d or d Month; None for anything else."""
    m = _DATE_NUM.match(t)
    if m:
        mo, d = int(m.group(1)), int(m.group(2))
    else:
        m = _DATE_MD.match(t)
        if m:
            mo, d = _MONTHS.get(m.group(1)[:3]), int(m.group(2))
        else:
            m = _DATE_DM.match(t)
            if not m:
                return None
            mo, d = _MONTHS.get(m.group(2)[:3]), int(m.group(1))
    if mo is None or not (1 <= mo <= 12 and 1 <= d <= 31):
        return None
    return (mo, d)


def _canon(x):
    """The meaning of a value written in more than one way, or None when the text is not one of the forms handled (then the plain text rule applies)."""
    t = norm_text(x)
    m = _LEAD.match(t)
    if m and m.group(1) == "through":
        dt = _date(m.group(2).strip())
        return ("through", dt) if dt else None
    if m and m.group(1) == "for":
        words = m.group(2).split()
        days = set()
        for w in words:
            if w == "allotherdays":
                return None                  # depends on the clauses before it
            if w in idf_sched.KEYWORDS:
                days.update(idf_sched.KEYWORDS[w])
            elif w in idf_sched.DAYS:
                days.add(w)
            else:
                return None
        return ("for", frozenset(d for d in days if d in _DOC_DAYS)) if days else None
    dt = _date(t)
    return ("date", dt) if dt else None


# Values of a field that are the SAME because the documents of the benchmark name them as one class (user decision 2026-11-21): the terrain "Urban / City" of the iUnit xlsx (C7) is City or Urban of EnergyPlus.
# (class in lower case, field name) -> sets of values (lower case) that are equal to each other
ENUM_EQUIV = {("building", "terrain"): [{"city", "urban"}]}


def enum_equal(cls, field, a, b):
    for s in ENUM_EQUIV.get((str(cls).lower(), str(field).lower()), []):
        if norm_text(a) in s and norm_text(b) in s:
            return True
    return False


def values_equal(a, b, prop=None, tol=0.01):
    """a, b: the texts (not blank). Text: case-insensitive, inner blanks collapsed. Numbers: |a-b| <= max(abs_tol, tol * max(|a|, |b|)). Dates and `For:` day lists: by meaning (_canon)."""
    if norm_text(a) == norm_text(b):
        return True
    ca, cb = _canon(a), _canon(b)
    if ca is not None and ca == cb:
        return True
    x, y = as_number(a), as_number(b)
    if x is None or y is None:
        return False
    abs_tol = 1e-3 if (prop and unit_of(prop) == "m") else 1e-6
    return abs(x - y) <= max(abs_tol, tol * max(abs(x), abs(y)))


def equals_default(value, prop, tol=0.01):
    """The candidate left the field blank: it equals the reference value when that value is the default of the schema."""
    d = default_of(prop or {})
    if d is None:
        return False
    return values_equal(value, str(d), prop, tol)
