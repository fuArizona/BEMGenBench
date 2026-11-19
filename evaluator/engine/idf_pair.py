"""idf_pair.py - pairs the objects of the reference with the objects of the candidate (aligned mode; design doc, section 6.2). Deterministic; every pair records HOW it was made.

  pairing = pair(ref_flat, cand_flat, tol=0.01)       -> Pairing  (.pr: reference uid -> candidate uid, .pc: the reverse, .method, .name_map, .notes, .pairs() / .unpaired())

Objects are paired only inside their CLASS, in these stages (the order matters: a later stage uses the earlier pairs):
  1 unique      a class that the schema allows once (Version, Building, SimulationControl, RunPeriod ...)                                                             method `unique`
  2 geometry    surfaces and fenestration (any class with vertices): the same polygon (the same points within a tolerance, any start vertex, either winding); two
                objects that fit the same candidates (the two sides of an interior wall) are decided after the zones are paired                                          `geometry`
  3 zones       a zone pairs with the zone that holds the partners of its surfaces (the most votes)                                                                     `surfaces`
  4 name        the same name (not case-sensitive); an unnamed class: the same identity (idf_flatten)                                                                    `name`
  5 content     all non-reference fields equal by the value rules (a schedule: the same hourly values), the pair is unique on both sides                               `content`
  6 anchor      the fields that name other objects name the PARTNERS of the same objects (a Lights object of the paired zone, a Construction of the paired layers)      `anchor`
  7 single      the only object of the class left on each side                                                                                                         `single`
  8 similarity  the best share of equal fields, at least 0.5, one to one                                                                                              `similarity`
  (zone-name    after stage 3: zones still unpaired whose names have the same words, a short form such as apt / apartment counts as the same; one to one)                 `zone-name`)
Stages 4-6 are repeated until nothing new is paired (a pair found by one stage makes the next stage possible). What is left is UNPAIRED on its side.
The polygon tolerance is max(1 mm, tol x the diagonal of the reference polygon).
"""
import math

import idf_sched
import idf_values as V

SINGLE_MIN = 0.2    # the last object of a class on each side is paired only when at least this share of the reference fields is equal
FIXED_VERTEX = ("vertex_%d_x_coordinate", "vertex_%d_y_coordinate", "vertex_%d_z_coordinate")


def polygon(o):
    """The points of an object with vertices (BuildingSurface:Detailed ... or FenestrationSurface:Detailed ...), or None."""
    f = o["fields"]
    pts = []
    info = o["info"]
    if info and info["ext"] == "vertices":
        k = 0
        while True:
            row = [f.get("vertices[%d]/%s" % (k, n)) for n in ("vertex_x_coordinate", "vertex_y_coordinate", "vertex_z_coordinate")]
            if row[0] is None:
                break
            pts.append(row)
            k += 1
    else:
        for k in range(1, 5):
            row = [f.get(n % k) for n in FIXED_VERTEX]
            if row[0] is None:
                break
            pts.append(row)
    if len(pts) < 3:
        return None
    try:
        return [tuple(float(x) for x in p) for p in pts]
    except (TypeError, ValueError):
        return None


def poly_tol(p, tol):
    xs, ys, zs = zip(*p)
    diag = math.sqrt((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2 + (max(zs) - min(zs)) ** 2)
    return max(1e-3, tol * diag)


def _dist(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))


def simplify(p, t):
    """The polygon without repeated points and without points on the straight line between their neighbours (distance <= t / 10, at least 0.1 mm): the same shape, fewer points."""
    eps = max(1e-4, t / 10.0)
    pts = list(p)
    changed = True
    while changed and len(pts) > 3:
        changed = False
        for i in range(len(pts)):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
            ab = [b[k] - a[k] for k in range(3)]
            ac = [c[k] - a[k] for k in range(3)]
            lac = math.sqrt(sum(x * x for x in ac))
            if lac < 1e-12:
                d = math.sqrt(sum(x * x for x in ab))
            else:
                cr = (ab[1] * ac[2] - ab[2] * ac[1], ab[2] * ac[0] - ab[0] * ac[2], ab[0] * ac[1] - ab[1] * ac[0])
                d = math.sqrt(sum(x * x for x in cr)) / lac
                dot = sum(ab[k] * ac[k] for k in range(3)) / lac
                if dot < -eps or dot > lac + eps:   # b is beyond the segment a-c: a spike, not a collinear point
                    d = max(d, eps * 2)
            if d <= eps:
                del pts[i]
                changed = True
                break
    return pts


def same_polygon(p, q, t):
    """The same shape within t (any start vertex, either winding; points on a straight edge do not count)."""
    p, q = simplify(p, t), simplify(q, t)
    if len(p) != len(q):
        return False
    used = set()
    for a in p:
        hit = next((j for j, b in enumerate(q) if j not in used and _dist(a, b) <= t), None)
        if hit is None:
            return False
        used.add(hit)
    return True


def normal(p):
    nx = ny = nz = 0.0
    for i, (x1, y1, z1) in enumerate(p):
        x2, y2, z2 = p[(i + 1) % len(p)]
        nx += (y1 - y2) * (z1 + z2)
        ny += (z1 - z2) * (x1 + x2)
        nz += (x1 - x2) * (y1 + y2)
    return nx, ny, nz


def _plane(p):
    nx, ny, nz = normal(p)
    ln = math.sqrt(nx * nx + ny * ny + nz * nz)
    if ln < 1e-12:
        return None
    u = (nx / ln, ny / ln, nz / ln)
    d = sum(u[k] * p[0][k] for k in range(3))
    return u, d, ln / 2.0


def _split_cases(ref_objs, cand_objs, tol):
    """Surfaces that one file has as one polygon and the other as several coplanar pieces (same normal, pieces inside the box of the whole, the pieces' areas add up to the whole within 1 %).
    Informational: [{cls, whole_side ('reference'|'candidate'), whole, area, pieces: [names], pieces_area}]."""
    def info(objs):
        out = []
        for o in objs:
            p = polygon(o)
            if p is None:
                continue
            pl = _plane(p)
            if pl is None:
                continue
            xs, ys, zs = zip(*p)
            out.append(dict(o=o, p=p, u=pl[0], d=pl[1], area=pl[2], lo=(min(xs), min(ys), min(zs)), hi=(max(xs), max(ys), max(zs))))
        return out
    ri, ci = info(ref_objs), info(cand_objs)
    res = []
    for side, whole, pieces in (("reference", ri, ci), ("candidate", ci, ri)):
        for w in whole:
            t = poly_tol(w["p"], tol)
            cl = w["o"]["cls"].lower()
            got = [x for x in pieces if x["o"]["cls"].lower() == cl and sum(a * b for a, b in zip(w["u"], x["u"])) > 0.999 and abs(w["d"] - x["d"]) <= t
                   and all(x["lo"][k] >= w["lo"][k] - t and x["hi"][k] <= w["hi"][k] + t for k in range(3)) and x["area"] < w["area"] * 0.999]
            if len(got) >= 2 and abs(sum(x["area"] for x in got) - w["area"]) <= 0.01 * w["area"]:
                res.append(dict(cls=w["o"]["cls"], whole_side=side, whole=w["o"].get("name"), area=round(w["area"], 3), pieces=[x["o"].get("name") for x in got], pieces_area=round(sum(x["area"] for x in got), 3),
                                _whole_obj=w["o"], _piece_objs=[x["o"] for x in sorted(got, key=lambda x: -x["area"])]))
    return res


def split_merged(ref_objs, cand_objs, tol):
    """The informational finding (see _split_cases), without the objects."""
    return [{k: v for k, v in c.items() if not k.startswith("_")} for c in _split_cases(ref_objs, cand_objs, tol)]


def reversed_winding(p, q):
    a, b = normal(p), normal(q)
    return sum(x * y for x, y in zip(a, b)) < 0


def leaves(o):
    """[(key, text)] of the non-blank fields of an object except its name."""
    out = []
    named = o["info"] and o["info"]["named"]
    for k, v in o["fields"].items():
        if (k == "name" and named) or V.is_blank(v):
            continue
        out.append((k, v))
    return out


class Pairing:
    def __init__(self, ref, cand, tol=0.01):
        self.tol = tol
        self.doc_only = False        # idf_doc_compare sets it: the shared-object test looks at the fields with a documentary basis only
        self.ref, self.cand = ref.objects, cand.objects
        self.geom_classes = self._geometry_classes()
        for i, o in enumerate(self.ref):
            o["uid"] = i
        for i, o in enumerate(self.cand):
            o["uid"] = i
        self.pr, self.pc, self.method = {}, {}, {}
        self.name_map = {}
        self.notes = []
        self.weak = []
        self.split = {}       # reference uid -> candidate uid: a surface that one file has whole and the other in coplanar pieces (stage_split): the non-vertex fields are compared with the other side's counterpart
        self.shared = {}      # reference uid -> candidate uid: a SHARED candidate object that equals a reference object completely (stage_shared)
        self._sched = {}
        self.base = {"r": None, "c": None}      # the folder of the reference / candidate IDF: a Schedule:File names its CSV relative to it (idf_sched, 2026-10-28)

    # ------------------------------------------------------------------ helpers
    def link(self, r, c, method):
        self.pr[r["uid"]] = c["uid"]
        self.pc[c["uid"]] = r["uid"]
        self.method[r["uid"]] = method
        if r.get("name") and c.get("name"):
            self.name_map.setdefault(r["name"].lower(), set()).add(c["name"].lower())

    def free(self, side):
        objs, used = (self.ref, self.pr) if side == "r" else (self.cand, self.pc)
        by = {}
        for o in objs:
            if o["uid"] not in used:
                by.setdefault(o["cls"].lower(), []).append(o)
        return by

    def mapped(self, value):
        """The names that a reference value maps to (the partners of the object it names), or None when it names no paired object."""
        return self.name_map.get(str(value).strip().lower())

    def profile(self, side, o):
        k = (side, o["uid"])
        if k not in self._sched:
            self._sched[k] = idf_sched.profile(o, self.base.get(side))
        return self._sched[k]

    def eq(self, key, rv, cv, o):
        """One field of a reference object against the candidate value text, by the rules (a reference field: through the pairing)."""
        prop = V.field_prop(o["info"], key)
        if V.kind_of(o["info"], key) in ("ref", "node"):
            m = self.mapped(rv)
            if m is not None and str(cv).strip().lower() in m:
                return True
        return V.values_equal(rv, cv, prop, self.tol)

    def content_equal(self, r, c):
        n = 0
        pr, pc = self.profile("r", r), self.profile("c", c)
        for k, v in leaves(r):
            if V.kind_of(r["info"], k) in ("ref", "node"):
                continue
            if pr is not None and pc is not None and idf_sched.is_data_key(k):
                continue
            cv = c["fields"].get(k)
            if V.is_blank(cv):
                if not V.equals_default(v, V.field_prop(r["info"], k), self.tol):
                    return False
            elif not V.values_equal(v, cv, V.field_prop(r["info"], k), self.tol):
                return False
            n += 1
        if pr is not None and pc is not None:
            return idf_sched.profiles_equal(pr, pc, self.tol)
        return n > 0

    def score(self, r, c):
        """The share of the non-blank reference fields that the candidate object has equal (references through the pairing)."""
        ls = leaves(r)
        if not ls:
            return 0.0
        pr, pc = self.profile("r", r), self.profile("c", c)
        sem = pr is not None and pc is not None and idf_sched.profiles_equal(pr, pc, self.tol)
        good = 0
        for k, v in ls:
            cv = c["fields"].get(k)
            if sem and idf_sched.is_data_key(k):
                good += 1
            elif V.is_blank(cv):
                good += 1 if V.equals_default(v, V.field_prop(r["info"], k), self.tol) else 0
            elif self.eq(k, v, cv, r):
                good += 1
        return good / len(ls)

    # ------------------------------------------------------------------ stages
    def stage_unique(self):
        fr, fc = self.free("r"), self.free("c")
        for cls, rs in fr.items():
            cs = fc.get(cls)
            if cs and rs[0]["info"] and rs[0]["info"]["unique"] and len(rs) == 1 and len(cs) == 1:
                self.link(rs[0], cs[0], "unique")

    def _geometry_classes(self):
        out = set()
        for o in self.ref:
            if o["info"] and (o["info"]["ext"] == "vertices" or any(f.startswith("vertex_1_") for f in o["info"]["fields"])):
                out.add(o["cls"].lower())
        return out

    def stage_geometry(self):
        self.amb = {}
        fr, fc = self.free("r"), self.free("c")
        for cls in sorted(self._geometry_classes()):
            rs, cs = fr.get(cls, []), fc.get(cls, [])
            polys_r = {o["uid"]: polygon(o) for o in rs}
            polys_c = {o["uid"]: polygon(o) for o in cs}
            cand_of = {}
            for r in rs:
                p = polys_r[r["uid"]]
                if p is None:
                    continue
                t = poly_tol(p, self.tol)
                cand_of[r["uid"]] = [c for c in cs if polys_c[c["uid"]] is not None and same_polygon(p, polys_c[c["uid"]], t)]
            ref_of = {}
            for ru, lst in cand_of.items():
                for c in lst:
                    ref_of.setdefault(c["uid"], []).append(ru)
            for r in rs:
                lst = cand_of.get(r["uid"], [])
                if len(lst) == 1 and len(ref_of[lst[0]["uid"]]) == 1:
                    self.link(r, lst[0], "geometry")
                elif lst:
                    self.amb[r["uid"]] = [c for c in lst]

    def stage_zones(self):
        votes = {}
        for ru, cu in list(self.pr.items()):
            r, c = self.ref[ru], self.cand[cu]
            rz, cz = r["fields"].get("zone_name"), c["fields"].get("zone_name")
            if rz and cz:
                votes[(rz.lower(), cz.lower())] = votes.get((rz.lower(), cz.lower()), 0) + 1
        fr, fc = self.free("r"), self.free("c")
        zr = {o["name"].lower(): o for o in fr.get("zone", []) if o.get("name")}
        zc = {o["name"].lower(): o for o in fc.get("zone", []) if o.get("name")}
        for (a, b), n in sorted(votes.items(), key=lambda kv: (-kv[1], kv[0])):
            if a in zr and b in zc and zr[a]["uid"] not in self.pr and zc[b]["uid"] not in self.pc:
                self.link(zr[a], zc[b], "surfaces")
        # the surfaces that fit several candidates: decide by the zone of the partner, then by the order of the file
        changed = True
        while changed:
            changed = False
            for ru in sorted(self.amb):
                if ru in self.pr:
                    continue
                r = self.ref[ru]
                lst = [c for c in self.amb[ru] if c["uid"] not in self.pc]
                zm = self.mapped(r["fields"].get("zone_name", ""))
                pick = [c for c in lst if zm and str(c["fields"].get("zone_name", "")).lower() in zm]
                if len(pick) == 1:
                    self.link(r, pick[0], "geometry")
                    changed = True
        for ru in sorted(self.amb):
            if ru in self.pr:
                continue
            lst = [c for c in self.amb[ru] if c["uid"] not in self.pc]
            if lst:
                self.link(self.ref[ru], lst[0], "geometry-ambiguous")
                self.notes.append("%s %r fits %d candidates (the two sides of a wall?): paired in the order of the file" % (self.ref[ru]["cls"], self.ref[ru].get("name"), len(lst)))

    @staticmethod
    def _name_tokens(name):
        import re
        t = re.findall(r"[a-z0-9]+", str(name).lower())
        return [x for x in t if x not in ("zone", "zn", "the")]

    @staticmethod
    def _tok_same(a, b):
        if a == b:
            return True
        if a.isdigit() or b.isdigit():
            return False
        s, l = (a, b) if len(a) <= len(b) else (b, a)
        if len(s) < 2 or s[0] != l[0]:
            return False
        it = iter(l)
        return all(ch in it for ch in s)             # a short form: the letters of the short word in order inside the long one (apt / apartment, rm / room)

    def stage_zone_names(self):
        """Zones that are still unpaired (the two layouts differ, so the surfaces gave no pair) and whose NAMES say the same: the same words in the same order, a word
        written in short (apt / apartment) counts as the same. Only a one-to-one match is taken. method `zone-name`."""
        fr, fc = self.free("r"), self.free("c")
        zr, zc = fr.get("zone", []), fc.get("zone", [])
        n = 0
        cand = {}
        for r in zr:
            tr = self._name_tokens(r.get("name"))
            if not tr:
                continue
            for c in zc:
                tc = self._name_tokens(c.get("name"))
                if len(tc) == len(tr) and all(self._tok_same(a, b) for a, b in zip(tr, tc)):
                    cand.setdefault(r["uid"], []).append(c)
        back = {}
        for ru, lst in cand.items():
            for c in lst:
                back.setdefault(c["uid"], []).append(ru)
        for r in zr:
            lst = cand.get(r["uid"], [])
            if len(lst) == 1 and len(back[lst[0]["uid"]]) == 1:
                self.link(r, lst[0], "zone-name")
                n += 1
        return n

    def stage_name(self):
        n0 = len(self.pr)
        fr, fc = self.free("r"), self.free("c")
        for cls, rs in fr.items():
            cs = {}
            for c in fc.get(cls, []):
                key = c["identity"] if c["identity"] is not None else ""
                cs.setdefault(key, []).append(c)
            for r in rs:
                key = r["identity"] if r["identity"] is not None else ""
                lst = [c for c in cs.get(key, []) if c["uid"] not in self.pc]
                if lst and (key or (r["info"] and r["info"]["unique"])):
                    self.link(r, lst[0], "name" if r.get("name") else "identity")
        return len(self.pr) - n0

    def stage_content(self):
        n0 = len(self.pr)
        fr, fc = self.free("r"), self.free("c")
        for cls, rs in fr.items():
            cs = fc.get(cls, [])
            if not cs:
                continue
            for r in rs:
                if r["uid"] in self.pr:
                    continue
                lst = [c for c in cs if c["uid"] not in self.pc and self.content_equal(r, c)]
                if not lst:
                    continue
                if len(lst) == 1:
                    self.link(r, lst[0], "content")
                else:                                              # identical candidates: the first in the file, but only when the reference has as many identical objects
                    twins = [x for x in rs if x["uid"] not in self.pr and self.content_equal(x, lst[0])]
                    if len(twins) <= len(lst):
                        self.link(r, lst[0], "content")
        return len(self.pr) - n0

    def _anchor(self, o, mapped):
        a = []
        for k, v in leaves(o):
            if V.kind_of(o["info"], k) == "ref":
                if mapped:
                    m = self.mapped(v)
                    if m is not None:
                        a.append((k, tuple(sorted(m))))
                else:
                    a.append((k, (str(v).strip().lower(),)))
        return a

    def stage_anchor(self):
        n0 = len(self.pr)
        fr, fc = self.free("r"), self.free("c")
        for cls, rs in fr.items():
            cs = [c for c in fc.get(cls, []) if c["uid"] not in self.pc]
            if not cs:
                continue
            cand_a = {c["uid"]: dict((k, v[0]) for k, v in self._anchor(c, False)) for c in cs}
            for r in rs:
                if r["uid"] in self.pr:
                    continue
                anc = self._anchor(r, True)
                if not anc:
                    continue
                weak = cls.startswith("schedule:") and all(k == "schedule_type_limits_name" for k, _ in anc)      # 2026-11-02: the type limits alone (all 'Fraction') are a weak anchor of a schedule: a unique candidate still pairs, but the greedy 'best of several' paired unrelated schedules (left to the similarity stage)
                lst = [c for c in cs if c["uid"] not in self.pc and all(cand_a[c["uid"]].get(k) in names for k, names in anc)]
                if len(lst) == 1:
                    self.link(r, lst[0], "anchor")
                elif len(lst) > 1 and not weak:
                    best = sorted(lst, key=lambda c: (-self.score(r, c), c["uid"]))
                    if self.score(r, best[0]) > self.score(r, best[1]):
                        self.link(r, best[0], "anchor")
        return len(self.pr) - n0

    def _ref_votes(self, cand_paired_ok=False):
        """{(ref target uid): {cand target uid: n}}: for every PAIRED object pair (r, c) and every field of kind `ref` that both have, the object that r names and the object that c names, when neither is paired yet and
        both are of the same class (the reverse of the anchor stage: the referrers are paired, the referred objects are not)."""
        by_name_r, by_name_c = {}, {}
        for o in self.ref:
            if o.get("name") and o["uid"] not in self.pr:
                by_name_r.setdefault(o["name"].strip().lower(), []).append(o)
        for o in self.cand:
            if o.get("name") and (cand_paired_ok or o["uid"] not in self.pc):
                by_name_c.setdefault(o["name"].strip().lower(), []).append(o)
        votes = {}
        for ru, cu in list(self.pr.items()) + (list(self.shared.items()) if cand_paired_ok else []):      # a shared pair also counts as a referrer (the glazing layer is named by the shared construction)
            r, c = self.ref[ru], self.cand[cu]
            for k, v in leaves(r):
                if V.kind_of(r["info"], k) != "ref":
                    continue
                cv = c["fields"].get(k)
                if cv is None or V.is_blank(cv):
                    continue
                for tr in by_name_r.get(str(v).strip().lower(), []):
                    for tc in by_name_c.get(str(cv).strip().lower(), []):
                        if tr["cls"].lower() == tc["cls"].lower():
                            d = votes.setdefault(tr["uid"], {})
                            d[tc["uid"]] = d.get(tc["uid"], 0) + 1
        return votes

    def stage_backanchor(self):
        """Pairs an unpaired object with the one that the partners of its referrers name in the same fields (when it is the only one in both directions)."""
        n0 = len(self.pr)
        votes = self._ref_votes()
        back = {}
        for ru, d in votes.items():
            for cu in d:
                back.setdefault(cu, set()).add(ru)
        for ru, d in sorted(votes.items()):
            if len(d) == 1:
                cu = next(iter(d))
                if len(back[cu]) == 1 and ru not in self.pr and cu not in self.pc:
                    self.link(self.ref[ru], self.cand[cu], "referrer")
        return len(self.pr) - n0

    def shared_objects(self):
        """Informational: a candidate object that the partners of the referrers of SEVERAL reference objects of one class all name (the reference has one object per user, the candidate shares one):
        [{cls, candidate, reference: [names]}]."""
        votes = self._ref_votes(True)
        back = {}
        for ru, d in votes.items():
            for cu in d:
                back.setdefault(cu, set()).add(ru)
        out = []
        for cu, rus in sorted(back.items()):
            if cu in self.pc:
                rus = set(rus) | {self.pc[cu]}
            cl = self.cand[cu]["cls"].lower()
            if len(rus) >= 2 and cl not in self.geom_classes and cl != "scheduletypelimits":   # surfaces: see split_merged; limits are shared by nature
                out.append(dict(cls=self.cand[cu]["cls"], candidate=self.cand[cu].get("name"), reference=[self.ref[r].get("name") for r in sorted(rus)]))
        return out

    def _fully_equal(self, r, c):
        """Every non-blank field of the reference object r is correct in the candidate object c (references through the pairing, schedules by their hourly values).
        With doc_only (idf_doc_compare): only the fields that have a documentary basis in either file decide, and the fields that name other objects are left out (the objects they name are decided by their own
        fields; this also breaks the circle construction <-> glazing); an object that has nothing but names of other objects is the same when both have the same number of them."""
        pr, pc = self.profile("r", r), self.profile("c", c)
        doc = self.doc_only and "basis" in r
        n = 0
        for k, v in leaves(r):
            if pr is not None and pc is not None and idf_sched.is_data_key(k):
                continue
            if doc:
                if V.kind_of(r["info"], k) in ("ref", "node"):
                    continue
                if "doc" not in ((r["basis"].get(k) or ("",))[0], (c.get("basis", {}).get(k) or ("",))[0]):
                    continue
            cv = c["fields"].get(k)
            if V.is_blank(cv):
                if not V.equals_default(v, V.field_prop(r["info"], k), self.tol):
                    return False
            elif not self.eq(k, v, cv, r):
                return False
            n += 1
        if pr is not None and pc is not None:
            return idf_sched.profiles_equal(pr, pc, self.tol)
        if doc and n == 0:
            return 0 < len(leaves(r)) == len(leaves(c))
        return True

    def stage_shared(self):
        """A candidate object that the users of SEVERAL reference objects of one class share (the reference has one object per user, the candidate shares one) is the partner of each of those reference objects that it
        equals completely: the model is the same, only the number of copies differs. The first reference object keeps the pairing of the earlier stages; the others are listed in `shared` (not for surfaces)."""
        votes = self._ref_votes(True)
        for ru, d in sorted(votes.items()):
            r = self.ref[ru]
            if ru in self.pr or ru in self.shared or r["cls"].lower() in self.geom_classes:
                continue
            full = [cu for cu in d if cu in self.pc and self._fully_equal(r, self.cand[cu])]
            if len(full) == 1:
                self.shared[ru] = full[0]
                if r.get("name") and self.cand[full[0]].get("name"):      # the users of the reference object name it: their field is correct when it names the shared candidate object
                    self.name_map.setdefault(r["name"].lower(), set()).add(self.cand[full[0]]["name"].lower())
        # schedules of the reference that are the same hourly values as a candidate schedule that is already paired (the reference writes the same schedule twice, in two classes or under two names; the
        # candidate has it once): the same schedule, whatever the type limits say (the type limits field is still compared on its own)
        pairs_c = [c for c in self.cand if c["uid"] in self.pc and c["cls"].lower() in ("schedule:compact", "schedule:constant") and self.profile("c", c) is not None]
        for r in self.ref:
            if r["uid"] in self.pr or r["uid"] in self.shared or r["cls"].lower() not in ("schedule:compact", "schedule:constant") or self.profile("r", r) is None:
                continue
            eqc = [c for c in pairs_c if idf_sched.profiles_equal(self.profile("r", r), self.profile("c", c), self.tol)]
            if eqc:
                c = eqc[0]
                self.shared[r["uid"]] = c["uid"]
                if r.get("name") and c.get("name"):
                    self.name_map.setdefault(r["name"].lower(), set()).add(c["name"].lower())
        return len(self.shared)

    def stage_schedule_cross(self):
        """A reference schedule and a candidate schedule of ANOTHER class (Schedule:Constant against Schedule:Compact) with the same hourly values in every period and day type are the same schedule written
        differently: they are paired (one to one; identical candidates only as many times as the reference has identical schedules)."""
        n0 = len(self.pr)
        fr, fc = self.free("r"), self.free("c")
        classes = ("schedule:compact", "schedule:constant", "schedule:file")      # schedule:file (2026-10-28): only when its CSV could be read (idf_sched.profile)
        rs = [o for c in classes for o in fr.get(c, []) if self.profile("r", o) is not None]
        cs = [o for c in classes for o in fc.get(c, []) if self.profile("c", o) is not None]
        for r in rs:
            if r["uid"] in self.pr:
                continue
            lst = [c for c in cs if c["uid"] not in self.pc and c["cls"].lower() != r["cls"].lower() and idf_sched.profiles_equal(self.profile("r", r), self.profile("c", c), self.tol)]
            if len(lst) >= 1:
                twins = [x for x in rs if x["uid"] not in self.pr and x["cls"].lower() == r["cls"].lower() and idf_sched.profiles_equal(self.profile("r", x), self.profile("c", lst[0]), self.tol)]
                if len(twins) <= len(lst):
                    self.link(r, lst[0], "schedule")
        return len(self.pr) - n0

    def stage_split(self):
        """A surface that one file has as ONE polygon and the other as several coplanar pieces (idf_pair.split_merged: same plane, the pieces inside the whole, areas add up) is the same surface cut differently. The
        reference objects that are not paired yet (the pieces of a reference cut, or the whole of a reference that the candidate cut) get the candidate counterpart (the whole, or the largest piece) as partner for
        the NON-vertex fields (type, construction, zone, boundary condition, exposure ...); their vertices stay wrong, because the polygons differ (the polygon test of kvor_aligned does not hold)."""
        cases = _split_cases([o for o in self.ref if o["cls"].lower() in self.geom_classes], [o for o in self.cand if o["cls"].lower() in self.geom_classes], self.tol)
        for c in cases:
            if c["whole_side"] == "candidate":
                cw = c["_whole_obj"]
                for r in c["_piece_objs"]:
                    if r["uid"] not in self.pr and r["uid"] not in self.split:
                        self.split[r["uid"]] = cw["uid"]
                        if r.get("name") and cw.get("name"):
                            self.name_map.setdefault(r["name"].lower(), set()).add(cw["name"].lower())
            else:
                rw = c["_whole_obj"]
                if rw["uid"] not in self.pr and rw["uid"] not in self.split:
                    cp = c["_piece_objs"][0]
                    self.split[rw["uid"]] = cp["uid"]
                    if rw.get("name") and cp.get("name"):
                        self.name_map.setdefault(rw["name"].lower(), set()).add(cp["name"].lower())
        return len(self.split)

    def stage_single(self):
        fr, fc = self.free("r"), self.free("c")
        for cls, rs in fr.items():
            cs = fc.get(cls, [])
            if len(rs) == 1 and len(cs) == 1:
                if self.score(rs[0], cs[0]) < SINGLE_MIN:
                    self.weak.append("%s %r and %r: the last objects of the class on each side, fewer than %d %% of the fields equal, not paired" % (rs[0]["cls"], rs[0].get("name"), cs[0].get("name"), int(SINGLE_MIN * 100)))
                    continue
                self.link(rs[0], cs[0], "single")

    def stage_similarity(self, threshold=0.5):
        fr, fc = self.free("r"), self.free("c")
        for cls, rs in fr.items():
            cs = fc.get(cls, [])
            if not cs:
                continue
            trip = sorted(((self.score(r, c), r["uid"], c["uid"]) for r in rs for c in cs), key=lambda t: (-t[0], t[1], t[2]))
            for s, ru, cu in trip:
                if s < threshold:
                    break
                if ru not in self.pr and cu not in self.pc:
                    self.link(self.ref[ru], self.cand[cu], "similarity")

    # ------------------------------------------------------------------ results
    def pairs(self):
        return [(self.ref[r], self.cand[c], self.method[r]) for r, c in sorted(self.pr.items())] + [(self.ref[r], self.cand[c], "shared") for r, c in sorted(self.shared.items())] + [(self.ref[r], self.cand[c], "split") for r, c in sorted(self.split.items())]

    def unpaired(self):
        return ([o for o in self.ref if o["uid"] not in self.pr and o["uid"] not in self.shared and o["uid"] not in self.split], [o for o in self.cand if o["uid"] not in self.pc])


def pair(ref, cand, tol=0.01, base_dirs=None, doc_only=False):
    p = Pairing(ref, cand, tol)
    p.doc_only = doc_only
    if base_dirs:
        p.base = dict(r=base_dirs.get("r"), c=base_dirs.get("c"))
    p.stage_unique()
    p.stage_geometry()
    p.stage_zone_names()          # zones with the same name first: the polygons of an invented layout can fit another zone by chance
    p.stage_zones()
    p.stage_zone_names()
    for _ in range(5):
        n = p.stage_name() + p.stage_content() + p.stage_anchor() + p.stage_backanchor()
        if n == 0:
            break
    p.stage_schedule_cross()
    for _ in range(3):
        n = p.stage_name() + p.stage_content() + p.stage_anchor() + p.stage_backanchor() + p.stage_schedule_cross()
        if n == 0:
            break
    p.stage_single()
    for _ in range(3):
        n = p.stage_name() + p.stage_content() + p.stage_anchor() + p.stage_backanchor()
        if n == 0:
            break
    p.stage_similarity()
    for _ in range(3):
        n = p.stage_name() + p.stage_content() + p.stage_anchor() + p.stage_backanchor()
        if n == 0:
            break
    n_shared = -1
    for _ in range(4):            # a shared object can only be recognised after the shared objects that name it (construction, then glazing layer)
        p.stage_shared()
        if len(p.shared) == n_shared:
            break
        n_shared = len(p.shared)
    p.stage_split()
    return p
