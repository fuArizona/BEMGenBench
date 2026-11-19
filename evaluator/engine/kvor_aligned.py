"""kvor_aligned.py - the main score of idf_compare: the Key-Value Overlap Rate after the objects were paired (idf_pair), with the value rules of idf_values.

  KVOR(aligned) = (reference keys that the candidate has correct) / (keys of the reference)        (the denominator is the same as in the paper mode)

For every non-blank field of a reference object (the name field excepted):
  - the object has no partner: the field is missed (one loss line per object, with its number of keys);
  - the vertices of a surface or fenestration object count as correct when the two polygons are the same (idf_pair.same_polygon: any start vertex, either winding; a reversed winding is listed as an
    informational finding, because EnergyPlus needs the outward direction);
  - the `data` fields of a schedule count as correct when the two schedules have the same hourly values (idf_sched);
  - a field that holds the name of another object is correct when the candidate names the PARTNER of the object the reference names (a name that is not paired: equal text);
  - a node (or node list) name is correct when it is the node that the reference node corresponds to in the paired objects (one to one, decided by votes over all fields); a node name that is the
    name of a paired object (a NodeList) goes by the previous rule;
  - any other field: equal by idf_values.values_equal (text: not case-sensitive, blanks collapsed; numbers: 1 % relative, 1e-6 absolute, 1e-3 for a field in metres);
  - the candidate left the field blank: correct when the reference value is the default of the schema.
Extra candidate keys (no reference key: fields of unpaired candidate objects, fields that are blank in the reference) are counted, not penalised; the precision and the extra keys are supplementary numbers.
"""
import re

import idf_pair
import idf_sched
import idf_values as V

_VERT = re.compile(r"^(vertices\[\d+\]/.+|vertex_\d+_[xyz]_coordinate)$")


def kvor_aligned(ref, cand, P):
    tol = P.tol
    per, losses, per_obj, node_pending, votes = {}, [], {}, [], {}
    findings = dict(reversed_winding=[], ambiguous=list(P.notes), node_conflicts=[], shared=P.shared_objects(), weak_single=list(P.weak),
                    split_merged=idf_pair.split_merged([o for o in P.ref if o["cls"].lower() in P.geom_classes], [o for o in P.cand if o["cls"].lower() in P.geom_classes], P.tol))
    correct = ref_keys = matched_cand = 0
    for r in P.ref:
        ls = idf_pair.leaves(r)
        row = per.setdefault(r["cls"], [0, 0])
        row[0] += len(ls)
        ref_keys += len(ls)
        if not ls:
            continue
        cu = P.pr.get(r["uid"])
        if cu is None:
            cu = P.shared.get(r["uid"])      # a shared candidate object that equals this reference object completely
        is_split = False
        if cu is None:
            cu = P.split.get(r["uid"])       # the counterpart of a surface that is cut differently (the non-vertex fields only: the polygons differ)
            is_split = cu is not None
        if cu is None:
            losses.append(dict(kind="missing_object", cls=r["cls"], key=(r["key_prefix"]), keys=len(ls), reference=r.get("name"), candidate=None))
            per_obj[r["uid"]] = 0
            continue
        c = P.cand[cu]
        pr = idf_pair.polygon(r)
        poly_ok = False
        if pr is not None:
            pc = idf_pair.polygon(c)
            poly_ok = pc is not None and idf_pair.same_polygon(pr, pc, idf_pair.poly_tol(pr, tol))
            if poly_ok and idf_pair.reversed_winding(pr, pc):
                findings["reversed_winding"].append("%s %s" % (r["cls"], r.get("name")))
        sem = False
        sp, sc = P.profile("r", r), P.profile("c", c)
        if sp is not None and sc is not None:
            sem = idf_sched.profiles_equal(sp, sc, tol)
        n_ok = 0
        for k, v in ls:
            cv = c["fields"].get(k)
            prop = V.field_prop(r["info"], k)
            kind = V.kind_of(r["info"], k)
            ok = None
            if is_split and (_VERT.match(k) or k == "number_of_vertices"):      # the polygons differ: the vertices (and their number) of a cut surface are not credited, even where a coordinate happens to be equal
                ok = False
            elif poly_ok and _VERT.match(k):
                ok = True
            elif sem and idf_sched.is_data_key(k):      # the same hourly values written as another schedule class (Constant / Compact / File with a readable CSV)
                ok = True
            elif V.is_blank(cv):
                ok = V.equals_default(v, prop, tol)
            elif kind == "node" and P.mapped(v) is None:
                votes.setdefault(v.strip().lower(), {})
                votes[v.strip().lower()][cv.strip().lower()] = votes[v.strip().lower()].get(cv.strip().lower(), 0) + 1
                node_pending.append((r, k, v, cv))
                continue
            else:
                ok = P.eq(k, v, cv, r)
            _book(ok, r, k, v, cv, row, losses)
            if ok:
                correct += 1
                n_ok += 1
                if not V.is_blank(cv):
                    matched_cand += 1
        per_obj[r["uid"]] = n_ok
    # ---- the nodes: one to one by votes
    trip = sorted(((n, rn, cn) for rn, d in votes.items() for cn, n in d.items()), key=lambda t: (-t[0], t[1], t[2]))
    winner, used = {}, set()
    for n, rn, cn in trip:
        if rn not in winner and cn not in used:
            winner[rn] = cn
            used.add(cn)
    for r, k, v, cv in node_pending:
        ok = winner.get(v.strip().lower()) == cv.strip().lower()
        row = per[r["cls"]]
        _book(ok, r, k, v, cv, row, losses)
        if ok:
            correct += 1
            per_obj[r["uid"]] = per_obj.get(r["uid"], 0) + 1
            matched_cand += 1
        else:
            findings["node_conflicts"].append("%s %s: reference node %r, candidate node %r (corresponds to %r)" % (r["cls"], r.get("name"), v, cv, winner.get(v.strip().lower())))
    # ---- the candidate side
    cand_keys = extra = 0
    for c in P.cand:
        ls = idf_pair.leaves(c)
        cand_keys += len(ls)
        ru = P.pc.get(c["uid"])
        if ru is None:
            extra += len(ls)
        else:
            rkeys = {k for k, _ in idf_pair.leaves(P.ref[ru])}
            extra += sum(1 for k, _ in ls if k not in rkeys)
    miss = sorted((x for x in losses if x["kind"] == "missing_object"), key=lambda x: (-x["keys"], x["cls"], str(x["reference"])))
    other = [x for x in losses if x["kind"] != "missing_object"]
    rate_exact = (correct / ref_keys) if ref_keys else 0.0
    ur, uc = P.unpaired()
    methods = {}
    for m in P.method.values():
        methods[m] = methods.get(m, 0) + 1
    if P.shared:
        methods["shared"] = len(P.shared)
    if P.split:
        methods["split"] = len(P.split)
    return dict(ref_keys=ref_keys, correct=correct, rate=round(rate_exact, 3), rate_exact=rate_exact, cand_keys=cand_keys, extra_keys=extra, precision=(matched_cand / cand_keys) if cand_keys else 0.0,
                per_class=per, losses=miss + other, findings=findings, pair_methods=methods, n_pairs=len(P.pr),
                unpaired_reference=[dict(cls=o["cls"], name=o.get("name") or o.get("identity"), keys=len(idf_pair.leaves(o))) for o in ur],
                unpaired_candidate=[dict(cls=o["cls"], name=o.get("name") or o.get("identity"), keys=len(idf_pair.leaves(o))) for o in uc], per_object=per_obj)


def _book(ok, r, k, v, cv, row, losses):
    if ok:
        row[1] += 1
    else:
        losses.append(dict(kind="changed" if not V.is_blank(cv) else "missing_field", cls=r["cls"], key=r["key_prefix"] + "/" + k, reference=v, candidate=None if V.is_blank(cv) else cv, keys=1))
