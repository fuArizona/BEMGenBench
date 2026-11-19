"""idf_flatten.py (idf_doc_compare copy: the comments of every field are kept, see parse_idf_comments) - an IDF text -> objects with named fields -> flat key / value pairs (design doc, section 5).

  parse_idf(text)                 [(class as written, [field texts])]   comments (`!` to the end of the line) dropped, fields trimmed, blank fields kept (as ""), the order of the file kept
  flatten(text, schema)           Flat(objects, leaves, version, notes)

A LEAF is a field with a non-blank value (a blank field is not a key, the rule of the BEMEval XML flatten: empty elements are skipped), except the NAME field of the object (it is the identity).
Fields are named by the SCHEMA (snake-case keys of Energy+.schema.epJSON), not by position, so a different field order or trailing blank fields do not matter. The text of a value is kept as written
(trimmed): the `paper` comparison is exact.

The key of a leaf (lower case; the field names are the schema's):
  - a class that can occur once (`maxProperties` 1 in the schema: Version, Building, SimulationControl, Timestep, RunPeriod ...)      <class>/<field>
  - any other class                                                                                                                  <class>/<identity>/<field>
  - an extensible group: the item index inside the object, from 0                                                                   <class>/<identity>/vertices[2]/vertex_y_coordinate
    (a group with one field: `<class>/<identity>/data[3]`)
The IDENTITY of an object: the value of its name field when the class has one; a class without a name field that can occur several times (Output:Variable, Output:Meter ...) takes the value of its
first field, then (while two objects of the class still have the same identity) of the first two fields, and so on; what is still equal gets `#2`, `#3` in the order of the file. So the identity does
not depend on the order of the objects unless the objects are completely equal.
A class that the schema does not know (another EnergyPlus version, a typo) keeps its fields as `field_1`, `field_2` ... and is listed in `notes`.
"""
import re


def parse_idf(text):
    """The objects of an IDF text. A `!` starts a comment to the end of the line (an IDF field never holds one)."""
    clean = "\n".join(l.split("!")[0] for l in text.splitlines())
    out = []
    for blk in clean.split(";"):
        blk = blk.strip()
        if not blk:
            continue
        parts = [p.strip() for p in blk.split(",")]
        out.append((parts[0], parts[1:]))
    return out


def parse_idf_comments(text):
    """Like parse_idf, but the comments are kept: [(class, [field texts], [comment of each field], comment of the class line)].
    The comment of a field is the text after the `!` of the line on which its separator (`,` or `;`) stands; a leading `-` (the `!- Field label  note` form of EnergyPlus) is part of it, see idf_basis.note_of.
    The objects and the field texts are exactly those of parse_idf."""
    objs, cur_fields, cur_comments, buf, cls_comment = [], [], [], "", ""
    for line in text.splitlines():
        if "!" in line:
            code, com = line.split("!", 1)
        else:
            code, com = line, ""
        com = com.strip()
        for ch in code:
            if ch in ",;":
                cur_fields.append(buf.strip())
                cur_comments.append(com)
                buf = ""
                if ch == ";":
                    if any(f for f in cur_fields):
                        objs.append((cur_fields[0], cur_fields[1:], cur_comments[1:], cur_comments[0]))
                    cur_fields, cur_comments = [], []
            else:
                buf += ch
        # text without a separator on a line (rare) continues in the buffer
        buf += " " if buf and code.strip() else ""
    return objs


class Flat:
    def __init__(self):
        self.objects = []        # dicts: cls (schema name or as written), known, name, identity, key_prefix, fields {key_suffix: text}, order
        self.leaves = {}         # full key -> (value text, class name as in the schema or as written)
        self.version = None      # the text of the Version object, e.g. "23.1"
        self.notes = []          # things worth saying (unknown classes, values beyond the fields of a class)


def _fields_of(info, values, notes, cls):
    """{field key: text} for the values of one object (the order of the schema; an extensible group with an item index)."""
    fixed = info["fields"]
    out = {}
    for i, v in enumerate(values):
        if i < len(fixed):
            out[fixed[i]] = v
        elif info["ext"]:
            n = max(1, len(info["ext_fields"]))
            k, j = divmod(i - len(fixed), n)
            sub = info["ext_fields"][j] if info["ext_fields"] else "field"
            out["%s[%d]" % (info["ext"], k) if n == 1 else "%s[%d]/%s" % (info["ext"], k, sub)] = v
        else:
            notes.append("%s: more fields than the schema lists (field %d)" % (cls, i + 1))
            out["extra_%d" % (i + 1)] = v
    return out


def flatten(text, schema):
    flat = Flat()
    raw = parse_idf_comments(text)
    objs = []
    for cls, values, comments, cls_comment in raw:
        if schema.known(cls):
            info = schema.info(cls)
            fields = _fields_of(info, values, flat.notes, info["cls"])
            cmts = _fields_of(info, comments, [], info["cls"])
            objs.append(dict(cls=info["cls"], known=True, info=info, fields=fields, values=values, comments=cmts, obj_comment=cls_comment))
        else:
            flat.notes.append("class %r is not in the schema: its fields are compared as field_1, field_2 ..." % cls)
            objs.append(dict(cls=cls, known=False, info=None, fields={"field_%d" % (i + 1): v for i, v in enumerate(values)}, values=values,
                             comments={"field_%d" % (i + 1): v for i, v in enumerate(comments)}, obj_comment=cls_comment))
    # ---- identities
    by_cls = {}
    for o in objs:
        by_cls.setdefault(o["cls"].lower(), []).append(o)
    for cls, group in by_cls.items():
        info = group[0]["info"]
        unique = bool(info and info["unique"])
        named = bool(info and info["named"])
        for o in group:
            o["name"] = (o["fields"].get("name") or None) if named else None
        if unique and len(group) == 1:
            for o in group:
                o["identity"] = None
            continue
        if named:
            ids = [(o["name"] or "").lower() for o in group]
        else:
            ids = _identities([o["values"] for o in group])
        seen = {}
        for o, i in zip(group, ids):
            seen[i] = seen.get(i, 0) + 1
            o["identity"] = i if seen[i] == 1 else "%s#%d" % (i, seen[i])
    # ---- leaves
    for o in objs:
        pre = o["cls"].lower() + ("/" + o["identity"] if o["identity"] is not None else "")
        o["key_prefix"] = pre
        for f, v in o["fields"].items():
            if f == "name" and o["info"] and o["info"]["named"]:
                continue
            if v == "":
                continue
            flat.leaves[pre + "/" + f] = (v, o["cls"])
    flat.objects = objs
    for o in objs:
        if o["cls"].lower() == "version" and o["values"]:
            flat.version = o["values"][0]
    return flat


def _identities(value_lists):
    """The identity of the objects of an unnamed class: the first field, then the first two, ... until the identities are different (or all fields are used)."""
    n = max((len(v) for v in value_lists), default=0)
    for k in range(1, n + 1):
        ids = ["|".join(x.lower() for x in v[:k]) for v in value_lists]
        if len(set(ids)) == len(ids):
            return ids
    return ["|".join(x.lower() for x in v) for v in value_lists]


def version_of(text):
    """The `major.minor` of the Version object of an IDF text, or None."""
    for cls, values in parse_idf(text):
        if cls.lower() == "version" and values:
            m = re.match(r"\s*(\d+)\.(\d+)", values[0])
            return "%s.%s" % m.groups() if m else values[0]
    return None
