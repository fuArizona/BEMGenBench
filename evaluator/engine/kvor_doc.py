"""kvor_doc.py - the score of idf_doc_compare: the aligned comparison of idf_compare (the objects are paired first, idf_pair; the value rules of idf_values), restricted to the keys that have a DOCUMENTARY BASIS.

  score = (keys of the universe that are the same in both files) / (keys of the universe)

The UNIVERSE (--universe union, the default): every key that has a documentary basis (idf_basis: doc) in the reference, or in its partner object of the candidate, or (a candidate object without a partner) in the candidate.
  `intersection`: only the keys that are doc in BOTH files (a documented value that one file does not have is then not counted as a loss).
A key of the universe is the SAME when both files have it and the values are equal by the rules of idf_compare (numbers within the tolerance, 1 % by default; text not case-sensitive; a field that holds the name of another
object names the partner; polygons the same; schedules the same hourly values; a node the corresponding node), or when one side leaves the field blank and the other has the schema default.
Keys without a documentary basis (nodoc, undetermined) are not counted; the report lists how many, by reason. Nothing is penalised for them.
"""
import re

import idf_hvac
import idf_intensity
import idf_pair
import idf_sched
import idf_values as V

_VERT = re.compile(r"^(vertices\[\d+\]/.+|vertex_\d+_[xyz]_coordinate)$")


def _basis(o, k):
    return (o.get("basis", {}).get(k) or (None,))[0]


DOC_DAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]      # the day types that a document gives; design days, holidays and custom days are choices of the file


def _ignored(cls, patterns):
    import fnmatch
    return any(fnmatch.fnmatchcase(cls.lower(), p.lower()) for p in patterns)


def _clause_doc(o, cl):
    """A clause of a Schedule:Compact has a documentary basis when every Until and value field of it does."""
    return all(((o.get("basis", {}).get("data[%d]" % i) or ("",))[0] == "doc") for i in cl["idx"])


def _clause_units(r, c, P, universe, tol):
    """The documentary content of two paired Schedule:Compact objects, clause by clause (`For:` + its Until / value fields), instead of field by field (the clauses of the two files do not have the same order or
    the same set of day types: a design-day clause is the choice of the file). Only the day types Sunday ... Saturday are compared. A clause of the reference that is documentary counts its fields and is correct
    when the candidate has the same 24 hourly values on every one of its days; a documentary clause of the candidate that covers a day the reference does not document counts the same way, against the reference.
    Returns ([(n fields, correct, label, reference hours, candidate hours)], {data keys that this function handled}) or None when a schedule cannot be read."""
    cr, cc = idf_sched.compact_clauses(r["values"]), idf_sched.compact_clauses(c["values"])
    pr, pc = P.profile("r", r), P.profile("c", c)
    if cr is None or cc is None or pr is None or pc is None:
        return None
    units, handled = [], set()

    def covered(clauses, o, end, days):
        got = set()
        for cl in clauses:
            if cl["end"] == end and _clause_doc(o, cl):
                got.update(cl["days"])
        return all(d in got for d in days)

    def same(hours, other, end, days):
        for d in days:
            h2 = idf_sched.hours_at(other, end, d)
            if h2 is None or any(abs(u - w) > max(1e-6, tol * max(abs(u), abs(w))) for u, w in zip(hours, h2)):
                return False
        return True

    for cl in cr:
        days = [d for d in cl["days"] if d in DOC_DAYS]
        handled.update("data[%d]" % i for i in cl["idx"])
        if not days or not _clause_doc(r, cl):
            continue
        if universe == "intersection" and not covered(cc, c, cl["end"], days):
            continue
        units.append((len(cl["idx"]), same(cl["hours"], pc, cl["end"], days), "For: " + " ".join(cl["days"]), cl["hours"], None))
    for cl in cc:
        days = [d for d in cl["days"] if d in DOC_DAYS]
        handled.update("data[%d]" % i for i in cl["idx"])
        if universe != "union" or not days or not _clause_doc(c, cl):
            continue
        if covered(cr, r, cl["end"], days):
            continue        # the same days are documentary in the reference too: counted there
        units.append((len(cl["idx"]), same(cl["hours"], pr, cl["end"], days), "For: " + " ".join(cl["days"]) + " (documentary in the candidate only)", None, cl["hours"]))
    return units, handled


def _grouped_doc(objects, zone):
    """True when a ZoneGroup that holds the zone has a documentary multiplier."""
    lists = {}
    for o in objects:
        if o["cls"].lower() == "zonelist":
            lists[(o["name"] or "").strip().lower()] = [str(v).strip().lower() for k, v in o["fields"].items() if k.startswith("zones[") and not V.is_blank(v)]
    for o in objects:
        if o["cls"].lower() == "zonegroup" and zone in lists.get((o["fields"].get("zone_list_name") or "").strip().lower(), []) and _basis(o, "zone_list_multiplier") == "doc":
            return True
    return False


# the documents give ONE number per zone for a family of loads (the xlsx `Plug and Process` is the electric AND gas equipment of the zone together), however many objects a file writes for it
def _vadd(a, b):
    return tuple((None if (x is None or y is None) else x + y) for x, y in zip(a, b))


def _vsum(vs):
    out = None
    for v in vs:
        out = v if out is None else _vadd(out, v)
    return out


def _vzero(v):
    return all(x is None or abs(x) <= 1e-12 for x in v)


def _vsame(a, b, tol):
    """Two intensities are the same when one of their components agrees (a load has one component: the intensity per m2 of floor; an infiltration has four, see idf_intensity.infil_unit)."""
    return any(x is not None and y is not None and abs(x - y) <= max(1e-9, tol * max(abs(x), abs(y))) for x, y in zip(a, b))


def _vtext(v):
    if len(v) == 1:
        return "%.6g per m2" % v[0]
    parts = ["%.4g m3/s" % v[0]]
    if v[2] is not None:
        parts.append("%.4g per m2 of exterior wall" % v[2])
    if v[1] is not None:
        parts.append("%.4g per m2 of floor" % v[1])
    return ", ".join(parts)


FAMILY = {"electricequipment": "equipment", "gasequipment": "equipment", "otherequipment": "equipment"}


def _load_groups(objects, areas, side, P, geo):
    """{(class, zone): [(object, intensity per m2, schedule profile or None, schedule name, value documentary, schedule documentary)]} of the load objects whose intensity is known."""
    by_name = {}
    for o in objects:
        if o["cls"].lower().startswith("schedule:") and o.get("name"):
            by_name[o["name"].strip().lower()] = o
    g = {}
    for o in objects:
        infil = o["cls"].lower() == idf_intensity.INFIL_CLASS
        if o["cls"].lower() not in idf_intensity.CLASSES and not infil:
            continue
        u = idf_intensity.infil_unit(o, geo) if infil else idf_intensity.unit(o, areas)
        if u is None:
            continue
        if not infil:
            u = (u[0], u[1], (u[2],))
        zone = (o["fields"].get(idf_intensity.ZONE_KEY) or "").strip().lower()
        sk = idf_intensity.schedule_key(o["cls"])
        sname = (o["fields"].get(sk) or "").strip().lower()
        so = by_name.get(sname)
        prof = P.profile(side, so) if so is not None else None
        v_doc = any(_basis(o, k) == "doc" for k in u[0])
        s_doc = _basis(o, sk) == "doc"
        g.setdefault((FAMILY.get(o["cls"].lower(), o["cls"].lower()), zone), []).append((o, u[2], prof, sname, v_doc, s_doc))
    return g


def _merge(items):
    """Loads of one zone and class with the same schedule (the same hourly values, or the same name when the schedule cannot be read) are ONE load: the intensities add up."""
    out = []
    for o, inten, prof, sname, v_doc, s_doc in items:
        for g in out:
            if (prof is not None and g["prof"] is not None and idf_sched.profiles_equal(prof, g["prof"])) or (prof is None and g["prof"] is None and sname == g["name"]):
                g["inten"] = _vadd(g["inten"], inten)
                g["v_doc"] |= v_doc
                g["s_doc"] |= s_doc
                break
        else:
            out.append(dict(inten=inten, prof=prof, name=sname, v_doc=v_doc, s_doc=s_doc))
    return out


def _zone_rename(P):
    """{candidate zone name (lower): reference zone name (lower)} for the zones that are paired: the loads of two paired zones are compared whatever the zone is called."""
    cd = {o["uid"]: o for o in P.cand if o["cls"].lower() == "zone"}
    rd = {o["uid"]: o for o in P.ref if o["cls"].lower() == "zone"}
    m = {}
    for ru, cu in P.pr.items():
        r = rd.get(ru)
        if r is not None and cu in cd and r.get("name") and cd[cu].get("name"):
            m[cd[cu]["name"].strip().lower()] = r["name"].strip().lower()
    return m


def _paired_groups(gr, gc, rename=None):
    if rename:
        gc2 = {}
        for (cl, zone), lst in gc.items():
            gc2.setdefault((cl, rename.get(zone, zone)), []).extend(lst)
        gc = gc2
    out = {}
    for key in sorted(set(gr) | set(gc)):
        out[key] = (gr.get(key, []), gc.get(key, []))
    return out


def _load_units(cl, zone, ritems, citems, P, universe, tol, counted):
    """[(n keys, correct, label, reference text, candidate text)] of the loads of one zone and class: for every group of the same schedule, a value key (the intensity) and a schedule key."""
    # a load of 0 W/m2 is no load: the prototype writes it (Lighting Level 0 with the schedule AlwaysOff), a Short IDF leaves the object out; the two are the same, so a zero group is not counted on either side
    R, C = [g for g in _merge(ritems) if not _vzero(g["inten"])], [g for g in _merge(citems) if not _vzero(g["inten"])]
    units = []
    used = set()
    pairs = []
    for i, rg in enumerate(R):
        for j, cg in enumerate(C):
            if j in used:
                continue
            if (rg["prof"] is not None and cg["prof"] is not None and idf_sched.profiles_equal(rg["prof"], cg["prof"])) or (rg["prof"] is None and cg["prof"] is None and rg["name"] == cg["name"]):
                pairs.append((i, j, True))
                used.add(j)
                break
        else:
            pairs.append((i, None, False))
    rest_c = [j for j in range(len(C)) if j not in used]
    for n, (i, j, ok) in enumerate(pairs):          # a group without a same-schedule partner is paired with a left-over group of the other file (its schedule differs)
        if j is None and rest_c:
            pairs[n] = (i, rest_c.pop(0), False)
    done_c = {j for _, j, _ in pairs if j is not None}
    # the VALUE: the total intensity of the zone and family (the documents give one number for it); documented zero loads on both sides are not counted
    n_comp = len((ritems or citems)[0][1])
    zero = tuple(0.0 for _ in range(n_comp))
    tot_r, tot_c = _vsum([x[1] for x in ritems]) or zero, _vsum([x[1] for x in citems]) or zero
    v_r, v_c = any(x[4] for x in ritems), any(x[4] for x in citems)
    if not _vzero(tot_r) or not _vzero(tot_c):
        if counted("doc" if v_r else None, "doc" if v_c else None):
            ok_v = _vsame(tot_r, tot_c, tol)
            units.append((1, ok_v, "value (total of the zone)", "%s (%d object%s)" % (_vtext(tot_r), len(ritems), "" if len(ritems) == 1 else "s") if ritems else None,
                          "%s (%d object%s)" % (_vtext(tot_c), len(citems), "" if len(citems) == 1 else "s") if citems else None))
    # the SCHEDULES: one key per group of the same schedule
    for i, j, same_sched in pairs:
        rg, cg = R[i], (C[j] if j is not None else None)
        rv = "schedule %s" % rg["name"]
        cv = ("schedule %s" % cg["name"]) if cg else None
        if counted("doc" if rg["s_doc"] else None, "doc" if (cg and cg["s_doc"]) else None):
            units.append((1, same_sched and cg is not None, "schedule", rv, cv))
    if universe == "union":
        for j, cg in enumerate(C):
            if j not in done_c and cg["s_doc"]:
                units.append((1, False, "schedule", None, "schedule %s" % cg["name"]))
    return units


def kvor_doc(ref, cand, P, universe="union", ignore=(), hvac_by_type=True):
    tol = P.tol
    per, losses, per_obj, node_pending, votes = {}, [], {}, [], {}
    ex = dict(reference=dict(nodoc=0, undet=0), candidate=dict(nodoc=0, undet=0))
    cnt = dict(ref_doc=0, cand_doc=0, both_doc=0, only_ref=0, only_cand=0)
    findings = dict(reversed_winding=[], ambiguous=list(P.notes), node_conflicts=[], shared=P.shared_objects(), weak_single=list(P.weak),
                    split_merged=idf_pair.split_merged([o for o in P.ref if o["cls"].lower() in P.geom_classes], [o for o in P.cand if o["cls"].lower() in P.geom_classes], P.tol))
    correct = universe_n = 0
    hvac_removed = {}     # HVAC class -> documentary keys left out because the HVAC is compared by TYPE (idf_hvac)
    ignored = {}          # class -> documentary keys left out because the class is ignored (the two files write that part of the model with different classes)
    areas_r, areas_c = idf_intensity.zone_areas(P.ref), idf_intensity.zone_areas(P.cand)
    mult_r, mult_c = idf_intensity.effective_multipliers(P.ref), idf_intensity.effective_multipliers(P.cand)
    geo_r, geo_c = idf_intensity.zone_geometry(P.ref), idf_intensity.zone_geometry(P.cand)
    grp_r, grp_c, grouped_r, grouped_c = _load_groups(P.ref, areas_r, "r", P, geo_r), _load_groups(P.cand, areas_c, "c", P, geo_c), set(), set()
    for lst in grp_r.values():
        grouped_r.update(o["uid"] for o, *_ in lst)
    for lst in grp_c.values():
        grouped_c.update(o["uid"] for o, *_ in lst)
    structural = {}       # ZoneList / ZoneGroup: their content is compared as the effective zone multiplier
    partner_of_cand = set(P.pc) | set(P.shared.values()) | set(P.split.values())

    def counted(br, bc):
        if universe == "intersection":
            return br == "doc" and bc == "doc"
        return br == "doc" or bc == "doc"

    for r in P.ref:
        allr = idf_pair.leaves(r)
        if _ignored(r["cls"], ignore):
            ignored[r["cls"]] = ignored.get(r["cls"], 0) + sum(1 for k, _ in allr if _basis(r, k) == "doc")
            continue
        if hvac_by_type and idf_hvac.is_hvac_class(r["cls"]):
            hvac_removed[r["cls"]] = hvac_removed.get(r["cls"], 0) + sum(1 for k, _ in allr if _basis(r, k) == "doc")
            continue
        if r["cls"].lower() in ("zonelist", "zonegroup"):
            structural[r["cls"]] = structural.get(r["cls"], 0) + sum(1 for k, _ in allr if _basis(r, k) == "doc")
            continue
        if r["uid"] in grouped_r:
            continue            # a load of a zone: compared per zone and class below (a file may split one load into several objects)
        row = per.setdefault(r["cls"], [0, 0])
        cu = P.pr.get(r["uid"])
        if cu is None:
            cu = P.shared.get(r["uid"])
        is_split = False
        if cu is None:
            cu = P.split.get(r["uid"])
            is_split = cu is not None
        c = P.cand[cu] if cu is not None else None
        # ---- Schedule:Compact against Schedule:Compact: the documentary clauses are compared as a whole
        sched_keys = set()
        if c is not None and r["cls"].lower() == "schedule:compact" and c["cls"].lower() == "schedule:compact":
            res_u = _clause_units(r, c, P, universe, tol)
            if res_u is not None:
                units, sched_keys = res_u
                for n_f, ok_u, label, rh, ch in units:
                    row[0] += n_f
                    universe_n += n_f
                    cnt["ref_doc" if rh is not None else "cand_doc"] += n_f
                    if ok_u:
                        row[1] += n_f
                        correct += n_f
                    else:
                        losses.append(dict(kind="changed_schedule", cls=r["cls"], key="%s/%s/%s" % (r["cls"].lower(), r.get("name"), label), reference=("hourly values %s" % (rh,)) if rh else None,
                                           candidate=("hourly values %s" % (ch,)) if ch else None, keys=n_f))
                        cnt["only_ref" if rh is not None else "only_cand"] += n_f
        # ---- a Schedule:Compact of the reference that has no readable Schedule:Compact partner: its documentary clauses count the same way (the number of keys of the universe must not depend on the pairing)
        if r["cls"].lower() == "schedule:compact" and not sched_keys and universe == "union":
            clauses = idf_sched.compact_clauses(r["values"])
            if clauses is not None:
                n_missing = 0
                for cl in clauses:
                    sched_keys.update("data[%d]" % i for i in cl["idx"])
                    if [d for d in cl["days"] if d in DOC_DAYS] and _clause_doc(r, cl):
                        n_missing += len(cl["idx"])
                if n_missing:
                    row[0] += n_missing
                    universe_n += n_missing
                    cnt["only_ref"] += n_missing
                    losses.append(dict(kind="missing_object" if c is None else "changed_schedule", cls=r["cls"], key="%s/%s" % (r["cls"].lower(), r.get("name")), reference=r.get("name"), candidate=None, keys=n_missing))
        # ---- a load written with another calculation method (a count in one file, a density in the other): the intensity per m2 of zone floor is compared
        unit_r, unit_c = set(), set()
        if c is not None and r["cls"].lower() == c["cls"].lower() and r["cls"].lower() in idf_intensity.CLASSES:
            ur, uc = idf_intensity.unit(r, areas_r), idf_intensity.unit(c, areas_c)
            if ur and uc:
                unit_r, unit_c = set(ur[0] + ur[1]), set(uc[0] + uc[1])
                r_doc = any(_basis(r, k) == "doc" for k in ur[0])
                c_doc = any(_basis(c, k) == "doc" for k in uc[0])
                cnt["ref_doc"] += 1 if r_doc else 0
                cnt["cand_doc"] += 1 if c_doc else 0
                if counted("doc" if r_doc else None, "doc" if c_doc else None):
                    row[0] += 1
                    universe_n += 1
                    if abs(ur[2] - uc[2]) <= max(1e-9, tol * max(abs(ur[2]), abs(uc[2]))):
                        row[1] += 1
                        correct += 1
                    else:
                        losses.append(dict(kind="changed", cls=r["cls"], key="%s/%s (per m2 of zone floor)" % (r["key_prefix"], ur[0][0]), reference="%s = %s (%.6g per m2)" % (ur[0][0], r["fields"][ur[0][0]], ur[2]),
                                           candidate="%s = %s (%.6g per m2)" % (uc[0][0], c["fields"][uc[0][0]], uc[2]), keys=1))
                        cnt["only_ref"] += 1
        # ---- the zone multiplier: the effective value (zone multiplier x the ZoneGroup multiplier) is compared
        if c is not None and r["cls"].lower() == "zone" and c["cls"].lower() == "zone":
            zr, zc = (r["name"] or "").strip().lower(), (c["name"] or "").strip().lower()
            mr, mc = mult_r.get(zr, 1.0), mult_c.get(zc, 1.0)
            doc_r = _basis(r, "multiplier") == "doc" or (mr != 1.0 and _grouped_doc(P.ref, zr))
            doc_c = _basis(c, "multiplier") == "doc" or (mc != 1.0 and _grouped_doc(P.cand, zc))
            cnt["ref_doc"] += 1 if doc_r else 0
            cnt["cand_doc"] += 1 if doc_c else 0
            if counted("doc" if doc_r else None, "doc" if doc_c else None):
                row[0] += 1
                universe_n += 1
                if abs(mr - mc) <= max(1e-9, tol * max(abs(mr), abs(mc))):
                    row[1] += 1
                    correct += 1
                else:
                    losses.append(dict(kind="changed", cls=r["cls"], key="%s/multiplier (zone x ZoneGroup)" % r["key_prefix"], reference=str(mr), candidate=str(mc), keys=1))
                    cnt["only_ref"] += 1
            unit_r.add("multiplier")
            unit_c.add("multiplier")
        # ---- which keys are in the universe
        ls = []
        for k, v in allr:
            if k in unit_r:
                continue
            if k in sched_keys:
                if _basis(r, k) in ("nodoc", "undet") and (c is None or _basis(c, k) != "doc"):
                    ex["reference"][_basis(r, k)] += 1
                continue
            br = _basis(r, k)
            bc = _basis(c, k) if c is not None else None
            if br == "doc":
                cnt["ref_doc"] += 1
            if bc == "doc":
                cnt["cand_doc"] += 1
            if br == "doc" and bc == "doc":
                cnt["both_doc"] += 1
            if counted(br, bc):
                ls.append((k, v))
            elif br in ("nodoc", "undet"):
                ex["reference"][br] += 1
        # keys that only the candidate has (the reference field is blank)
        extra_c = []
        if c is not None:
            rk = {k for k, _ in allr}
            for k, cv in idf_pair.leaves(c):
                if k in rk or k in sched_keys or k in unit_c:
                    continue
                bc = _basis(c, k)
                if bc == "doc":
                    cnt["cand_doc"] += 1
                    if universe == "union":
                        extra_c.append((k, cv))
                        cnt["only_cand"] += 1
                elif bc in ("nodoc", "undet"):
                    ex["candidate"][bc] += 1
        row[0] += len(ls) + len(extra_c)
        universe_n += len(ls) + len(extra_c)
        for k, cv in extra_c:       # documented in the candidate, blank in the reference: the same only when the value is the schema default
            prop = V.field_prop(c["info"], k) if c["info"] else None
            if prop is not None and V.equals_default(cv, prop, tol):
                row[1] += 1
                correct += 1
            else:
                losses.append(dict(kind="only_in_candidate", cls=r["cls"], key=r["key_prefix"] + "/" + k, reference=None, candidate=cv, keys=1))
        if not ls:
            per_obj[r["uid"]] = 0
            continue
        if c is None:
            losses.append(dict(kind="missing_object", cls=r["cls"], key=(r["key_prefix"]), keys=len(ls), reference=r.get("name"), candidate=None))
            per_obj[r["uid"]] = 0
            cnt["only_ref"] += len(ls)
            continue
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
            if is_split and (_VERT.match(k) or k == "number_of_vertices"):
                ok = False
            elif poly_ok and _VERT.match(k):
                ok = True
            elif sem and idf_sched.is_data_key(k):
                ok = True
            elif V.is_blank(cv):
                ok = V.equals_default(v, prop, tol)
                if not ok:
                    cnt["only_ref"] += 1
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
        per_obj[r["uid"]] = n_ok
    # ---- the loads, per zone and class
    for (cl, zone), (ritems, citems) in _paired_groups(grp_r, grp_c, _zone_rename(P)).items():
        row = per.setdefault(ritems[0][0]["cls"] if ritems else citems[0][0]["cls"], [0, 0])
        for n_f, ok_u, label, rv, cv_ in _load_units(cl, zone, ritems, citems, P, universe, tol, counted):
            row[0] += n_f
            universe_n += n_f
            if ok_u:
                row[1] += n_f
                correct += n_f
            else:
                losses.append(dict(kind="changed", cls=ritems[0][0]["cls"] if ritems else citems[0][0]["cls"], key="%s/%s: %s" % (cl, zone, label), reference=rv, candidate=cv_, keys=n_f))
                cnt["only_ref" if rv is not None else "only_cand"] += n_f
    # ---- the nodes: one to one by votes
    trip = sorted(((n, rn, cn) for rn, d in votes.items() for cn, n in d.items()), key=lambda t: (-t[0], t[1], t[2]))
    winner, used = {}, set()
    for n, rn, cn in trip:
        if rn not in winner and cn not in used:
            winner[rn] = cn
            used.add(cn)
    for r, k, v, cv in node_pending:
        ok = winner.get(v.strip().lower()) == cv.strip().lower()
        _book(ok, r, k, v, cv, per[r["cls"]], losses)
        if ok:
            correct += 1
            per_obj[r["uid"]] = per_obj.get(r["uid"], 0) + 1
        else:
            findings["node_conflicts"].append("%s %s: reference node %r, candidate node %r (corresponds to %r)" % (r["cls"], r.get("name"), v, cv, winner.get(v.strip().lower())))
    # ---- candidate objects without a partner: their documented keys are in the universe (union) and are not matched
    for c in P.cand:
        if c["uid"] in partner_of_cand:
            continue
        ls = idf_pair.leaves(c)
        if _ignored(c["cls"], ignore):
            ignored[c["cls"]] = ignored.get(c["cls"], 0) + sum(1 for k, _ in ls if _basis(c, k) == "doc")
            continue
        if hvac_by_type and idf_hvac.is_hvac_class(c["cls"]):
            hvac_removed[c["cls"]] = hvac_removed.get(c["cls"], 0) + sum(1 for k, _ in ls if _basis(c, k) == "doc")
            continue
        if c["cls"].lower() in ("zonelist", "zonegroup") or c["uid"] in grouped_c:
            continue
        n_doc = 0
        for k, _ in ls:
            b = _basis(c, k)
            if b == "doc":
                n_doc += 1
            elif b in ("nodoc", "undet"):
                ex["candidate"][b] += 1
        cnt["cand_doc"] += n_doc
        if universe == "union" and n_doc:
            row = per.setdefault(c["cls"], [0, 0])
            row[0] += n_doc
            universe_n += n_doc
            cnt["only_cand"] += n_doc
            losses.append(dict(kind="extra_object", cls=c["cls"], key=c["key_prefix"], keys=n_doc, reference=None, candidate=c.get("name") or c.get("identity")))
    # ---- the HVAC by TYPE: one key per system type that is documentary in either file (union) or in both (intersection); the same when both files have that type
    hvac_rows = []
    if hvac_by_type:
        tr, tc = idf_hvac.tags(P.ref), idf_hvac.tags(P.cand)
        for tag in sorted(set(tr) | set(tc)):
            r_t, c_t = tr.get(tag), tc.get(tag)
            doc_r, doc_c = bool(r_t and r_t["doc"]), bool(c_t and c_t["doc"])
            if not counted("doc" if doc_r else None, "doc" if doc_c else None):
                hvac_rows.append(dict(tag=tag, counted=False, reference=r_t, candidate=c_t, same=None))
                continue
            same = bool(r_t and c_t)
            row = per.setdefault("HVAC (by type)", [0, 0])
            row[0] += 1
            universe_n += 1
            cnt["ref_doc"] += 1 if doc_r else 0
            cnt["cand_doc"] += 1 if doc_c else 0
            if same:
                row[1] += 1
                correct += 1
            else:
                cnt["only_ref" if r_t else "only_cand"] += 1
                losses.append(dict(kind="hvac_type", cls="HVAC (by type)", key="HVAC type: " + tag, reference=("present (%s)" % ", ".join(r_t["classes"][:3])) if r_t else None,
                                   candidate=("present (%s)" % ", ".join(c_t["classes"][:3])) if c_t else None, keys=1))
            hvac_rows.append(dict(tag=tag, counted=True, reference=r_t, candidate=c_t, same=same))
    miss = sorted((x for x in losses if x["kind"] in ("missing_object", "extra_object")), key=lambda x: (-x["keys"], x["cls"], str(x["reference"] or x["candidate"])))
    other = [x for x in losses if x["kind"] not in ("missing_object", "extra_object")]
    ur, uc = P.unpaired()
    methods = {}
    for m in P.method.values():
        methods[m] = methods.get(m, 0) + 1
    if P.shared:
        methods["shared"] = len(P.shared)
    if P.split:
        methods["split"] = len(P.split)
    return dict(universe=universe, keys=universe_n, correct=correct, rate=(correct / universe_n) if universe_n else 0.0, counts=cnt, excluded=ex, per_class=per, losses=miss + other,
                findings=findings, pair_methods=methods, n_pairs=len(P.pr), per_object=per_obj, ignored=ignored, structural_removed=structural, hvac_removed=hvac_removed, hvac_types=hvac_rows,
                unpaired_reference=[dict(cls=o["cls"], name=o.get("name") or o.get("identity"), keys=len(idf_pair.leaves(o))) for o in ur],
                unpaired_candidate=[dict(cls=o["cls"], name=o.get("name") or o.get("identity"), keys=len(idf_pair.leaves(o))) for o in uc])


def _book(ok, r, k, v, cv, row, losses):
    if ok:
        row[1] += 1
    else:
        losses.append(dict(kind="changed" if not V.is_blank(cv) else "missing_field", cls=r["cls"], key=r["key_prefix"] + "/" + k, reference=v, candidate=None if V.is_blank(cv) else cv, keys=1))
