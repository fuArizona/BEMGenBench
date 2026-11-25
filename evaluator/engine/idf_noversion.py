"""idf_noversion.py - the comparison branch for a candidate IDF that has NO Version object (no EnergyPlus is called).

A file without Version cannot be a model that runs; it is a list of the values that a document gives (for example the documented_only.idf made by
tools/make_documented_only_idf.py). evaluate.py goes into this branch as soon as the candidate has no Version object. The numbers are
CANDIDATE-based (a precision, not the usual document-based KVOR):

  Field KVOR   denominator: the COUNTED fields of the CANDIDATE (those that have a document-supported counterpart in the REFERENCE)
               numerator:   the counted candidate fields with the same value (same class, object, field and value)
  Object KVOR  denominator: the COUNTED objects of the CANDIDATE (an object with at least one counted field)
               numerator:   the counted candidate objects whose counted fields are all the same
  Runs in EnergyPlus: always No (it is not called)

DOCUMENTARY BASIS (the same rule as the main comparison, idf_basis.py): the REFERENCE decides which fields count, from its own comments. A candidate field is NEUTRAL, in
neither the numerator nor the denominator, whatever its value, when
  - its counterpart in the reference has the basis `nodoc` (assumption, EnergyPlus requirement or default, "not in the documents") or `undet` (no verdict), or
  - it has NO counterpart in the reference (another field of the class, an object the reference does not have): the reference gives no document basis for it (user decision 2026-11-25).
What a file adds beyond the documents is neither rewarded nor penalised. So only the fields that the reference gives as document values are counted, and a counted field
is wrong only when its value differs. A candidate object is neutral when all its fields are neutral; it is then in neither Object count. A neutral field never spoils the
sameness of an object. The lists missing_fields / missing_objects are information (what the candidate has beyond the reference); they do not change a number.
Consequence: the numbers do not depend on whether the reference is reference.idf or a copy from which the nodoc fields were removed (documented_only.idf).

A field has a counterpart when the reference has the same class, the same object (by name / identity) and the same field, WITH THE SAME VALUE (text without case, or numbers within 1 %):
the key must exist and the value must be equal; a different value counts as different.
An object is the same when every counted field of the candidate object is the same (an object that has a counted field has a counterpart in the reference).
The comments of the candidate are ignored; the comments of the REFERENCE give the basis. Nothing is simulated and no file is changed.
"""
import idf_basis
import idf_flatten
import idf_values as V


def _same_value(a, b, tol=0.01):
    if a.strip().lower() == b.strip().lower():
        return True
    try:
        x, y = float(a), float(b)
    except ValueError:
        return False
    return abs(x - y) <= tol * max(abs(x), abs(y), 1e-12)


def compare(reference_text, candidate_text, schema, rules=()):
    """dict(fields=(n_counted, n_same), objects=(...), excluded_fields {nodoc, undet, no_counterpart}, excluded_objects, missing_fields, different_fields,
    missing_objects, different_objects, per_class, notes)."""
    fr = idf_flatten.flatten(reference_text, schema)
    fc = idf_flatten.flatten(candidate_text, schema)
    idf_basis.annotate(fr, "reference", rules)
    ref_obj = {o["key_prefix"]: o for o in fr.objects}
    n_f = n_fok = n_o = n_ook = 0
    excl_f = dict(nodoc=0, undet=0, no_counterpart=0)
    excl_o = 0
    miss_f, diff_f, miss_o, diff_o, per = [], [], [], [], {}
    for o in fc.objects:
        pre = o["key_prefix"]
        ro = ref_obj.get(pre)
        counted = same_fields = 0
        obj_ok = True
        for f, v in o["fields"].items():
            if (f == "name" and o["info"] and o["info"]["named"]) or V.is_blank(v):
                continue
            key = pre + "/" + f
            if key not in fr.leaves:                 # no counterpart in the reference: no document basis, neutral (information only)
                excl_f["no_counterpart"] += 1
                miss_f.append(key)
                continue
            b = ((ro or {}).get("basis", {}).get(f) or ("undet",))[0]
            if b != "doc":                           # the reference does not give it as a document value: neutral
                excl_f[b] += 1
                continue
            counted += 1
            if _same_value(v, fr.leaves[key][0]):
                same_fields += 1
            else:
                diff_f.append(dict(key=key, reference=fr.leaves[key][0], candidate=v))
                obj_ok = False
        if counted == 0:                             # an object with no counted field is neutral
            excl_o += 1
            if ro is None:
                miss_o.append(pre)
            continue
        row = per.setdefault(o["cls"], dict(objects=0, objects_ok=0, fields=0, fields_ok=0))
        row["objects"] += 1
        row["fields"] += counted
        row["fields_ok"] += same_fields
        n_o += 1
        n_f += counted
        n_fok += same_fields
        if obj_ok:
            n_ook += 1
            row["objects_ok"] += 1
        else:
            diff_o.append(pre)
    return dict(fields=(n_f, n_fok), objects=(n_o, n_ook), excluded_fields=excl_f, excluded_objects=excl_o,
                missing_fields=miss_f, different_fields=diff_f, missing_objects=miss_o, different_objects=diff_o, per_class=per, notes=fc.notes[:10])
