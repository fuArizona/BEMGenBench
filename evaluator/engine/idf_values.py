"""idf_values.py - how one field value is compared in the aligned mode (design doc, section 6.2).

  base_field(key)                 the schema field of a flat key ("vertices[2]/vertex_y_coordinate" -> "vertex_y_coordinate", "data[3]" -> "field")
  field_prop(info, key)           the schema property of that field ({} when unknown)
  kind_of(info, key)              "ref" (a field that holds the name of another object: object_list in the schema), "node" (a node or node list name), "val" (anything else)
  default_of(prop)                the default of the schema for the field, or None
  values_equal(a, b, prop, tol)   the value rules: text trimmed, inner blanks collapsed, case-insensitive; numbers equal within a relative tolerance (and an absolute one: 1e-6, 1e-3 for a field in m)
  is_blank(x)

Everything here is deterministic and has no state; the rules are listed in the report.
"""
import re

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


def values_equal(a, b, prop=None, tol=0.01):
    """a, b: the texts (not blank). Text: case-insensitive, inner blanks collapsed. Numbers: |a-b| <= max(abs_tol, tol * max(|a|, |b|))."""
    if norm_text(a) == norm_text(b):
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
