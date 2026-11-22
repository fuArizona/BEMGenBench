"""idf_equiv.py - the same physical quantity written another way (annotation, not in the key score).

  equivalences(P, res_doc, root=None, weather=None, tol=0.01)   P = the pairing (idf_pair), res_doc = the result of kvor_doc.kvor_doc

Three kinds of equivalence are computed, all deterministic (no judgement by a language model):

  CONSTRUCTIONS (opaque)   A reference construction and its partner in the candidate are the same when the thermal resistance of their layers (the sum of thickness / conductivity of Material, the resistance of
                           Material:NoMass and Material:AirGap) is the same within the tolerance. The surface films are not added: they are the same on both sides. The heat capacity per m2 (density x specific heat x
                           thickness) is reported next to it (`capacity_ratio`); since 2026-11-21 it IS a condition of the equivalence (user decision): the heat capacity within MASS_TOL and the order of the layers (the centroid of the heat capacity along the resistance, ORDER_TOL) must also be the same. The partner is the construction that the paired surfaces (the same polygon) name; a pair of constructions that the pairing
                           found is the fallback.
  WINDOWS                  The U-factor and the SHGC of the window constructions (layered glazing and gas, or WindowMaterial:SimpleGlazingSystem) are those that EnergyPlus itself reports in the eio file for a small IDF that
                           holds the window materials and constructions of the file (one run of about 0.1 s per file, with a weather file; `Output:Constructions`). Without a program or a weather file two constructions
                           of one simple glazing system are compared by the numbers they state. Frames and dividers are not included.
  AIR (outdoor air and ventilation)   Per paired zone, the design flow in m3/s of ZoneVentilation:DesignFlowRate plus the outdoor air specification of the zone (DesignSpecification:OutdoorAir named by its Sizing:Zone;
                           methods Flow/Person, Flow/Area, Flow/Zone, AirChanges/Hour, Sum, Maximum), with the occupancy and the floor area of the zone of the same file. Infiltration is already compared by its
                           flow per zone in the key score (`idf_intensity.infil_unit`); it is not repeated here.

U-ONLY CONSTRUCTIONS (user decision 2026-11-21): a construction that the documents give only as a U-value of the assembly (`cases/<id>/traceability/u_only_constructions.json`, the reference writes its
resistance as one layer without mass) is equivalent by the thermal resistance ALONE: the heat capacity and the order of the layers are not compared (the documents do not give them).

A construction pair that is the same by its quantities gives back the keys of the score that were lost only because the layers are written differently: the keys of the construction and of its layer materials
by the table RULES below (which field is given back under which condition; the same table is `docs/equivalence_rules.md`, written by `rules_markdown()`). In short: the layer names, the thickness, the conductivity
and the resistance when the thermal resistance is the same; the density and the specific heat only when the heat capacity per m2 is also the same within MASS_TOL; for a window all fields of the glazing, gas and
simple glazing objects. The absorptances, the roughness and the frame objects are NOT given back. `rate_with_equivalents` = (same + recovered keys) / keys: a supplementary number, the key score itself does not change.
"""
import collections
import os
import re
import shutil
import subprocess
import tempfile

import idf_intensity
import idf_pair
import idf_run
import idf_values as V

TOL = 0.01
ABS = 1e-6
LAYER_FIELDS = ["outside_layer"] + ["layer_%d" % i for i in range(2, 11)]
OPAQUE_CLASSES = ("material", "material:nomass", "material:airgap", "material:infraredtransparent")
ORDER_TOL = 0.10         # two constructions have the same order of the layers when the centroids of the heat capacity along the resistance are less than 0.10 apart (both without mass: the order does not matter)
MASS_TOL = 0.10          # two constructions have the same heat capacity per m2 when the values are within 10 % (both 0 = both without mass)

# The rules of the keys that an equivalent construction gives back. condition: "equivalent" = the construction pair has the same thermal resistance (windows: the same U-factor and SHGC);
# "equivalent and mass" = also the same heat capacity per m2 (MASS_TOL) for EVERY construction that uses the material; "never" = not given back.
RULES = [
    dict(cls="Construction", fields=None, label="the layer names (outside_layer, layer_2 ...)", condition="equivalent",
         why="the layer names are the way the stack is written; the stack of the other file has the same thermal resistance. The order of the layers is checked by the position of the heat capacity along the resistance (ORDER_TOL)."),
    dict(cls="Material", fields=("thickness",), label="thickness", condition="equivalent",
         why="with the conductivity, one of the two ways to write the resistance (thickness / conductivity). The resistance is that of the whole construction, not of this layer."),
    dict(cls="Material", fields=("conductivity",), label="conductivity", condition="equivalent", why="see thickness."),
    dict(cls="Material", fields=("density",), label="density", condition="equivalent and mass",
         why="the resistance does not determine it; it is given back only when the heat capacity per m2 of the construction is the same too."),
    dict(cls="Material", fields=("specific_heat",), label="specific heat", condition="equivalent and mass", why="see density."),
    dict(cls="Material", fields=("roughness", "thermal_absorptance", "solar_absorptance", "visible_absorptance"), label="roughness, absorptances", condition="never",
         why="they are not part of the thermal resistance or the heat capacity; a file that does not write them has not given the documented value."),
    dict(cls="Material:NoMass", fields=("thermal_resistance",), label="thermal resistance", condition="equivalent", why="the quantity itself (the whole construction has the same resistance)."),
    dict(cls="Material:NoMass", fields=("roughness", "thermal_absorptance", "solar_absorptance", "visible_absorptance"), label="roughness, absorptances", condition="never", why="see Material."),
    dict(cls="Material:AirGap", fields=("thermal_resistance",), label="thermal resistance", condition="equivalent", why="the quantity itself."),
    dict(cls="Material:InfraredTransparent", fields=(), label="all fields", condition="never", why="it has no resistance."),
    dict(cls="WindowMaterial:* (glazing, gas, simple glazing system, ...)", fields=None, label="all fields", condition="equivalent",
         why="the U-factor and the SHGC that EnergyPlus reports for the construction are the same; the glazing data are only the way they are written. The visible transmittance is not compared."),
    dict(cls="WindowProperty:FrameAndDivider, shading and shading control", fields=(), label="all fields", condition="never", why="frames, dividers and shading are not part of the U-factor and SHGC computed here."),
]


def allowed_fields(cls, mass_ok):
    """The fields of the opaque material class `cls` (lower case) that are given back; mass_ok = the heat capacity per m2 is the same for every construction that uses the material."""
    out = set()
    for r in RULES:
        if r["cls"].lower() == cls and r["fields"]:
            if r["condition"] == "equivalent" or (r["condition"] == "equivalent and mass" and mass_ok):
                out.update(r["fields"])
    return out


def rules_markdown():
    """The text of docs/equivalence_rules.md (the test compares the file with it)."""
    L = ["# Keys that an equivalent construction gives back", "",
         "Written by `rules_markdown()` of `evaluator/engine/idf_equiv.py`; `evaluator/tests/test_equivalences.py` checks that this file is the same as its output. Do not edit it by hand: edit `RULES` in the code.", "",
         "A construction of the reference and its partner in the candidate (the construction named by the paired surfaces) are **equivalent** when the thermal resistance of their layers is the same within 1 %% **and** the heat capacity per m2 within %d %% **and** the order of the layers is the same (the centroid of the heat capacity along the resistance within %.2f; an opaque "
         "construction; the surface films are the same on both sides and are not added) or the U-factor and the SHGC that EnergyPlus reports are the same within 1 %% (a window construction). The heat capacity per m2 is density x specific heat x thickness, summed over the layers; both without mass is the same. A pair with the same resistance but another heat capacity or order is NOT equivalent and gives nothing back, EXCEPT for a construction that the documents give only as a U-value (listed in `traceability/u_only_constructions.json`): there the resistance alone decides, and the density and the specific heat are not given back (the mass is not known to be the same). "
         "A verdict of a judge (idf_judge.py) can make a pair equivalent that the numbers cannot decide; then the mass is not known and the density and the specific heat are not given back." % (round(100 * MASS_TOL), ORDER_TOL), "",
         "A key of the score that is lost only because the two files write the layers differently is given back when its field is in the table below and its condition holds. The keys of an object that the other file "
         "does not have at all (a material that one file writes as layers and the other as one resistance) are given back only for the fields that the table allows. For a material that several constructions use, the condition "
         "must hold for every one of them. The key score is not changed; the number with the keys given back is `rate_with_equivalents`.", "",
         "| class | field | condition | why |", "|---|---|---|---|"]
    for r in RULES:
        L.append("| %s | %s | %s | %s |" % (r["cls"], r["label"], r["condition"], r["why"]))
    L += ["", "Not checked: frames and dividers, shading, the visible transmittance."]
    return "\n".join(L) + "\n"



def _f(o, k):
    v = o["fields"].get(k)
    if V.is_blank(v):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _near(a, b, tol=TOL):
    return a is not None and b is not None and abs(a - b) <= max(ABS, tol * max(abs(a), abs(b)))


def layers(con):
    out = []
    for k in LAYER_FIELDS:
        v = con["fields"].get(k)
        if not V.is_blank(v):
            out.append(str(v).strip().lower())
    return out


def opaque_quantities(con, mats):
    """dict(r, capacity, centroid) of an opaque construction, or None when a layer is unknown or has no value. r in m2K/W (the layers only), capacity in J/m2K, centroid = where the heat capacity sits along the
    thermal resistance, from 0 (outside layer) to 1 (inside layer), None without mass."""
    r = cap = 0.0
    prof = []
    for n in layers(con):
        m = mats.get(n)
        if m is None:
            return None
        c = m["cls"].lower()
        if c == "material":
            t, k = _f(m, "thickness"), _f(m, "conductivity")
            if t is None or not k:
                return None
            r += t / k
            d, cp = _f(m, "density"), _f(m, "specific_heat")
            cap += (d or 0.0) * (cp or 0.0) * t
            prof.append((t / k, (d or 0.0) * (cp or 0.0) * t))
        elif c in ("material:nomass", "material:airgap"):
            x = _f(m, "thermal_resistance")
            if x is None:
                return None
            r += x
            prof.append((x, 0.0))
        elif c == "material:infraredtransparent":
            pass
        else:
            return None
    centroid = None
    if cap > 0 and r > 0:
        before = s = 0.0
        for ri, ci in prof:
            s += ci * (before + ri / 2) / r
            before += ri
        centroid = s / cap
    return dict(r=r, capacity=cap, centroid=centroid) if layers(con) else None


def _is_window_layer(o):
    return o["cls"].lower().startswith("windowmaterial:")


def mini_window_idf(objs):
    """The IDF that holds the window materials and the window constructions of a file, to be run to read the U-factor and the SHGC from the eio file."""
    wm = {(o.get("name") or "").strip().lower(): o for o in objs if _is_window_layer(o)}
    cons = [o for o in objs if o["cls"].lower() == "construction" and layers(o) and all(n in wm for n in layers(o))]
    if not cons:
        return None, []
    out = ["Version, 23.1;", "SimulationControl, No, No, No, No, Yes;", "Building, B, 0, Suburbs, 0.04, 0.4, FullExterior, 25, 6;", "GlobalGeometryRules, UpperLeftCorner, Counterclockwise, Relative;",
           "RunPeriod, rp, 1, 1, 2025, 1, 1, 2025, , Yes, Yes, No, Yes, Yes;"]
    used = {n for c in cons for n in layers(c)}
    for o in objs:
        if (_is_window_layer(o) and (o.get("name") or "").strip().lower() in used) or o in cons:
            out.append(o["cls"] + ",\n  " + ",\n  ".join(o["values"]) + ";")
    out.append("Output:Constructions, Constructions;")
    return "\n".join(out) + "\n", [(c.get("name") or "").strip().lower() for c in cons]


def run_window_quantities(objs, root, weather, timeout=120):
    """{construction name (lower case): dict(u, shgc, vt, source "EnergyPlus")} for the window constructions of a file; (None, reason) when the program cannot be run."""
    text, names = mini_window_idf(objs)
    if text is None:
        return {}, ""
    exe = idf_run.exe_of(root) if root else None
    if exe is None or not weather or not os.path.isfile(weather):
        return None, "no EnergyPlus program or no weather file"
    tmp = tempfile.mkdtemp(prefix="bemgen_win_")
    try:
        p = os.path.join(tmp, "w.idf")
        open(p, "w", encoding="utf8").write(text)
        try:
            subprocess.run([exe, "-w", os.path.abspath(weather), "-d", tmp, p], cwd=tmp, capture_output=True, text=True, timeout=timeout, errors="replace")
        except subprocess.TimeoutExpired:
            return None, "EnergyPlus did not end in %d s" % timeout
        eio = os.path.join(tmp, "eplusout.eio")
        if not os.path.isfile(eio):
            return None, "no eio file"
        out = {}
        for line in open(eio, encoding="utf8", errors="replace"):
            if line.lstrip().startswith("WindowConstruction,"):
                f = [x.strip() for x in line.strip().split(",")]

                def num(i):
                    try:
                        return float(f[i])
                    except (IndexError, ValueError):
                        return None
                out[f[1].lower()] = dict(u=num(5), shgc=num(8), vt=num(10), source="EnergyPlus")
        return out, ""
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def simple_window(con, mats):
    ls = layers(con)
    if len(ls) == 1 and ls[0] in mats and mats[ls[0]]["cls"].lower() == "windowmaterial:simpleglazingsystem":
        m = mats[ls[0]]
        return dict(u=_f(m, "u_factor"), shgc=_f(m, "solar_heat_gain_coefficient"), vt=_f(m, "visible_transmittance"), source="stated")
    return None


def construction_partners(P):
    """{reference construction (lower case): candidate construction} by the votes of the paired surfaces; a pair of Construction objects that the pairing found is used when no surface votes."""
    votes = collections.defaultdict(collections.Counter)
    for r in P.ref:
        cu = P.pr.get(r["uid"])
        if cu is None:
            continue
        rc = r["fields"].get("construction_name")
        cc = P.cand[cu]["fields"].get("construction_name")
        if not V.is_blank(rc) and not V.is_blank(cc):
            votes[str(rc).strip().lower()][str(cc).strip().lower()] += 1
    out = {n: v.most_common(1)[0][0] for n, v in votes.items()}
    for r in P.ref:
        if r["cls"].lower() == "construction" and (r.get("name") or "").strip():
            cu = P.pr.get(r["uid"])
            if cu is not None and P.cand[cu].get("name"):
                out.setdefault(r["name"].strip().lower(), P.cand[cu]["name"].strip().lower())
    return out


def _catalogue(objs):
    mats = {}
    for o in objs:
        c = o["cls"].lower()
        if c in OPAQUE_CLASSES or c.startswith("windowmaterial:"):
            mats[(o.get("name") or "").strip().lower()] = o
    cons = {(o.get("name") or "").strip().lower(): o for o in objs if o["cls"].lower() == "construction"}
    return mats, cons


def _doc_fields(o, allowed):
    """The number of fields of an object that have a documentary basis and are in `allowed` (None = all)."""
    b = o.get("basis") or {}
    return sum(1 for k, v in b.items() if v[0] == "doc" and (allowed is None or k in allowed))


def construction_equivalence(P, root=None, weather=None, tol=TOL, u_only=()):
    rm, rc = _catalogue(P.ref)
    cm, cc = _catalogue(P.cand)
    partner = construction_partners(P)
    note = ""
    rw = cw = None
    if any(_is_window_layer(m) for m in list(rm.values()) + list(cm.values())):
        rw, why1 = run_window_quantities(P.ref, root, weather)
        cw, why2 = run_window_quantities(P.cand, root, weather)
        note = why1 or why2
    pairs = []
    for rn, con in rc.items():
        cn = partner.get(rn)
        if cn is None or cn not in cc:
            continue
        ccon = cc[cn]
        lr, lc = layers(con), layers(ccon)
        win = any(rm.get(n) is not None and _is_window_layer(rm[n]) for n in lr)
        winc = any(cm.get(n) is not None and _is_window_layer(cm[n]) for n in lc)
        row = dict(reference=con.get("name"), candidate=ccon.get("name"), kind="window" if win else "opaque", same=False, why="")
        if win != winc:
            row["why"] = "one is a window construction, the other is not"
        elif win:
            a = (rw or {}).get(rn) or simple_window(con, rm)
            b = (cw or {}).get(cn) or simple_window(ccon, cm)
            if a is None or b is None or a.get("u") is None or b.get("u") is None:
                row["why"] = "the U-factor / SHGC of a window construction could not be computed (%s)" % (note or "layers not readable")
            else:
                row.update(u_reference=a["u"], u_candidate=b["u"], shgc_reference=a.get("shgc"), shgc_candidate=b.get("shgc"), source=a["source"] if a["source"] == b["source"] else "mixed")
                row["same"] = _near(a["u"], b["u"], tol) and (a.get("shgc") is None or b.get("shgc") is None or _near(a["shgc"], b["shgc"], tol))
        else:
            a, b = opaque_quantities(con, rm), opaque_quantities(ccon, cm)
            if a is None or b is None:
                row["why"] = "the thermal resistance could not be computed (a layer is unknown or has no value)"
            else:
                row.update(r_reference=round(a["r"], 5), r_candidate=round(b["r"], 5), capacity_ratio=round(b["capacity"] / a["capacity"], 3) if a["capacity"] else None)
                row["same_r"] = _near(a["r"], b["r"], tol)
                row["mass_same"] = (a["capacity"] <= 0 and b["capacity"] <= 0) or (a["capacity"] > 0 and b["capacity"] > 0 and _near(a["capacity"], b["capacity"], MASS_TOL))
                row["order_same"] = (a["capacity"] <= 0 and b["capacity"] <= 0) or (a["centroid"] is not None and b["centroid"] is not None and abs(a["centroid"] - b["centroid"]) <= ORDER_TOL)
                row.update(centroid_reference=None if a["centroid"] is None else round(a["centroid"], 3), centroid_candidate=None if b["centroid"] is None else round(b["centroid"], 3))
                row["same"] = row["same_r"] and row["mass_same"] and row["order_same"]          # equivalent: the resistance, the heat capacity and the order of the layers
                if rn in u_only:
                    # the documents give this construction only as a U-value (traceability/u_only_constructions.json): the thermal resistance ALONE decides (user decision 2026-11-21)
                    row["u_only"] = True
                    row["same"] = row["same_r"]
        pairs.append(row)
    return pairs, note, rm, rc, cm, cc


def recovered_keys(P, res_doc, pairs, rm, rc, cm, cc):
    """The keys of the score that an equivalent construction pair gives back (see the module text). Returns (keys, list of dict(key, keys))."""
    ok_ref = {(r["reference"] or "").strip().lower() for r in pairs if r["same"]}
    ok_cand = {(r["candidate"] or "").strip().lower() for r in pairs if r["same"]}
    bad_ref = {(r["reference"] or "").strip().lower() for r in pairs if not r["same"]} | {n for n in rc if n not in ok_ref}
    bad_cand = {(r["candidate"] or "").strip().lower() for r in pairs if not r["same"]} | {n for n in cc if n not in ok_cand}
    rmat = collections.defaultdict(set)
    for n, c in rc.items():
        for m in layers(c):
            rmat[m].add(n)
    cmat = collections.defaultdict(set)
    for n, c in cc.items():
        for m in layers(c):
            cmat[m].add(n)
    free_r = {m for m, users in rmat.items() if users and not (users & bad_ref)}              # materials that only equivalent constructions use
    free_c = {m for m, users in cmat.items() if users and not (users & bad_cand)}
    mass_ref = {(r["reference"] or "").strip().lower() for r in pairs if r["same"] and r.get("mass_same")}
    mass_cand = {(r["candidate"] or "").strip().lower() for r in pairs if r["same"] and r.get("mass_same")}
    free_r_mass = {m for m, users in rmat.items() if users and users <= mass_ref}             # ... and whose heat capacity is also the same
    free_c_mass = {m for m, users in cmat.items() if users and users <= mass_cand}
    out = []
    for x in res_doc["losses"]:
        cls = x["cls"].lower()
        key = x["key"].lower()
        parts = key.split("/")
        win = cls.startswith("windowmaterial:")
        if not (cls == "construction" or cls in OPAQUE_CLASSES or win):
            continue
        name = parts[1] if len(parts) > 1 else ""
        field = parts[2] if len(parts) > 2 else None
        cand_side = x["kind"] == "extra_object"
        allowed = None if win or cls == "construction" else allowed_fields(cls, name in (free_c_mass if cand_side else free_r_mass))
        if allowed is not None and field is not None and field not in allowed:
            continue
        if x["kind"] == "extra_object":
            who_ok = name in free_c if cls != "construction" else name in ok_cand
            obj = (cc if cls == "construction" else cm).get(name)
        else:
            who_ok = name in free_r if cls != "construction" else name in ok_ref
            obj = (rc if cls == "construction" else rm).get(name)
        if not who_ok:
            continue
        n = x["keys"]
        if x["kind"] in ("missing_object", "extra_object") and obj is not None and allowed is not None:
            n = min(n, _doc_fields(obj, allowed))
        if n:
            out.append(dict(key=x["key"], keys=n))
    return sum(o["keys"] for o in out), out


# ------------------------------------------------------------------ outdoor air and ventilation
def _people(objs, zone, area):
    """The number of people of a zone (the sum of its People objects), None when it cannot be told."""
    tot = 0.0
    seen = False
    for o in objs:
        if o["cls"].lower() != "people" or (o["fields"].get("zone_or_zonelist_or_space_or_spacelist_name") or "").strip().lower() != zone:
            continue
        m = (o["fields"].get("number_of_people_calculation_method") or "").strip().lower()
        try:
            if m == "people" or (m == "" and _f(o, "number_of_people") is not None):
                tot += _f(o, "number_of_people") or 0.0
            elif m == "people/area":
                tot += (_f(o, "people_per_floor_area") or 0.0) * area
            elif m == "area/person":
                x = _f(o, "floor_area_per_person")
                tot += area / x if x else 0.0
            else:
                continue
        except TypeError:
            continue
        seen = True
    return tot if seen else None


def zone_air(objs):
    """{zone (lower case): dict(total, parts)}: the design flow in m3/s of the ventilation objects and of the outdoor air specification of each zone of one file."""
    areas = idf_intensity.zone_areas(objs)
    geo = idf_intensity.zone_geometry(objs)
    spec = {(o.get("name") or "").strip().lower(): o for o in objs if o["cls"].lower() == "designspecification:outdoorair"}
    out = {}

    def add(zone, label, q):
        d = out.setdefault(zone, dict(total=0.0, parts={}))
        d["total"] += q
        d["parts"][label] = d["parts"].get(label, 0.0) + q
    for o in objs:
        c = o["cls"].lower()
        if c == "sizing:zone":
            zone = (o["fields"].get("zone_or_zonelist_name") or "").strip().lower()
            s = spec.get((o["fields"].get("design_specification_outdoor_air_object_name") or "").strip().lower())
            if s is None or zone not in geo:
                continue
            a = areas.get(zone, 0.0)
            n = _people(objs, zone, a)
            vol = geo[zone].get("volume")
            m = (s["fields"].get("outdoor_air_method") or "Flow/Person").strip().lower()
            pp, pa, pz, ach = _f(s, "outdoor_air_flow_per_person"), _f(s, "outdoor_air_flow_per_zone_floor_area"), _f(s, "outdoor_air_flow_rate_per_zone"), _f(s, "outdoor_air_flow_air_changes_per_hour")
            pz = pz if pz is not None else _f(s, "outdoor_air_flow_per_zone")
            comp = {"flow/person": (pp or 0.0) * n if n is not None else None, "flow/area": (pa or 0.0) * a, "flow/zone": pz or 0.0, "airchanges/hour": (ach or 0.0) * vol / 3600.0 if vol else None}
            if m in comp:
                q = comp[m]
            elif m in ("sum", "maximum"):
                vals = [comp["flow/person"], comp["flow/area"], comp["flow/zone"], comp["airchanges/hour"]]
                if any(v is None for v in vals[:3]):
                    q = None
                else:
                    vals = [v for v in vals if v is not None]
                    q = sum(vals) if m == "sum" else max(vals)
            else:
                q = None
            if q is not None:
                add(zone, "outdoor air specification", q)
        elif c == "zoneventilation:designflowrate":
            zone = (o["fields"].get("zone_or_zonelist_or_space_or_spacelist_name") or o["fields"].get("zone_or_zonelist_name") or "").strip().lower()
            if zone not in geo:
                continue
            a = areas.get(zone, 0.0)
            m = (o["fields"].get("design_flow_rate_calculation_method") or "").strip().lower()
            vol = geo[zone].get("volume")
            if m == "flow/zone":
                q = _f(o, "design_flow_rate")
            elif m == "flow/area":
                q = (_f(o, "flow_rate_per_floor_area") or 0.0) * a
            elif m == "flow/person":
                n = _people(objs, zone, a)
                q = (_f(o, "flow_rate_per_person") or 0.0) * n if n is not None else None
            elif m == "airchanges/hour" and vol:
                q = (_f(o, "air_changes_per_hour") or 0.0) * vol / 3600.0
            else:
                q = None
            if q is not None:
                add(zone, "zone ventilation", q)
    return out


def air_equivalence(P, tol=TOL):
    ra, ca = zone_air(P.ref), zone_air(P.cand)
    rows = []
    for r in P.ref:
        if r["cls"].lower() != "zone":
            continue
        zr = (r.get("name") or "").strip().lower()
        cu = P.pr.get(r["uid"])
        if cu is None:
            continue
        zc = (P.cand[cu].get("name") or "").strip().lower()
        a, b = ra.get(zr), ca.get(zc)
        if a is None and b is None:
            continue
        qa, qb = (a or {}).get("total", 0.0), (b or {}).get("total", 0.0)
        both = a is not None and b is not None          # a file that states the outdoor air in another form (HVACTemplate fields, the air loop) has no total here: the zone is listed, not compared
        rows.append(dict(zone=r.get("name"), reference=None if a is None else round(qa, 6), candidate=None if b is None else round(qb, 6), comparable=both, same=both and (_near(qa, qb, tol) or (qa < ABS and qb < ABS)),
                         reference_parts={k: round(v, 6) for k, v in (a or {}).get("parts", {}).items()}, candidate_parts={k: round(v, 6) for k, v in (b or {}).get("parts", {}).items()}))
    return rows


def equivalences(P, res_doc, root=None, weather=None, tol=TOL, judgements=None, ignore_ids=(), u_only=()):
    import idf_judge
    u_only = {str(n).strip().lower() for n in u_only}
    pairs, note, rm, rc, cm, cc = construction_equivalence(P, root, weather, tol, u_only)
    keys, listed = recovered_keys(P, res_doc, pairs, rm, rc, cm, cc)
    reqs = idf_judge.requests(P, res_doc, pairs, rm, rc, cm, cc, u_only)
    llm = idf_judge.apply(P, res_doc, pairs, rm, rc, cm, cc, reqs, judgements, ignore_ids, u_only) if judgements else None
    air = air_equivalence(P, tol)
    n = res_doc["keys"]
    r4 = lambda x: round(x, 4)
    return dict(constructions=dict(pairs=len(pairs), u_only_pairs=sum(1 for p in pairs if p.get("u_only")), equivalent=sum(1 for p in pairs if p["same"]), differ=sum(1 for p in pairs if not p["same"]), rows=pairs[:60], note=note),
                recovered_keys=keys, recovered=listed[:60], rate_with_equivalents=r4(min(n, res_doc["correct"] + keys) / n) if n else None,
                air=dict(zones=len(air), comparable=sum(1 for a in air if a["comparable"]), same=sum(1 for a in air if a["same"]), rows=air[:60]),
                judgement_requests=reqs, llm=llm,
                infiltration="compared in the key score by the flow per zone (idf_intensity.infil_unit); not repeated here",
                rule="constructions: the thermal resistance of the layers (opaque) or the U-factor and SHGC of EnergyPlus (window) within %g %%; the keys of the fields that carry the quantity are given back; absorptances, roughness and frames are not; "
                     "air: the design flow per zone in m3/s, only for a zone that both files state with a DesignSpecification:OutdoorAir or a ZoneVentilation object; not in the key score" % (100 * tol))
