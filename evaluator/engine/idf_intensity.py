"""idf_intensity.py - the same documented load written with another CALCULATION METHOD.

A load object states one number in one of several ways: People `number_of_people` (a count), `people_per_floor_area`, `floor_area_per_person`; Lights / ElectricEquipment / GasEquipment / OtherEquipment a total
power (`lighting_level`, `design_level`) or a power per zone floor area. One file may write the count that the other writes as a density: the documented fact is the same. This module reduces the value of such
an object to ONE intensity per square metre of the floor of its zone (the floor area is computed from the Floor surfaces of the zone in the same file), so that the two files can be compared.

  zone_areas(objects)            {zone name (lower case): floor area in m2} from the BuildingSurface:Detailed objects of type Floor
  unit(o, areas)                 ([value field], [calculation-method field], intensity) of a load object, or None when it has no value or the zone floor area is unknown (a ZoneList ...)
Classes handled (power per area in W/m2, people per area in 1/m2):
  People; Lights; ElectricEquipment; GasEquipment; OtherEquipment.
"""
import idf_pair
import idf_values as V

ZONE_KEY = "zone_or_zonelist_or_space_or_spacelist_name"
# class (lower case) -> {field: kind}; kind: total (value for the whole zone), per_area, area_per (m2 per unit), plus the field that names the method (structure, left out of the comparison)
CLASSES = {
    "people": ({"number_of_people": "total", "people_per_floor_area": "per_area", "floor_area_per_person": "area_per"}, "number_of_people_calculation_method"),
    "lights": ({"lighting_level": "total", "watts_per_zone_floor_area": "per_area"}, "design_level_calculation_method"),
    "electricequipment": ({"design_level": "total", "watts_per_zone_floor_area": "per_area"}, "design_level_calculation_method"),
    "gasequipment": ({"design_level": "total", "power_per_zone_floor_area": "per_area"}, "design_level_calculation_method"),
    "otherequipment": ({"design_level": "total", "power_per_zone_floor_area": "per_area"}, "design_level_calculation_method"),
}

# the calculation method (lower case) -> the value field that EnergyPlus uses
METHOD_FIELD = {
    "people": {"people": "number_of_people", "people/area": "people_per_floor_area", "area/person": "floor_area_per_person"},
    "lights": {"lightinglevel": "lighting_level", "watts/area": "watts_per_zone_floor_area"},
    "electricequipment": {"equipmentlevel": "design_level", "watts/area": "watts_per_zone_floor_area"},
    "gasequipment": {"equipmentlevel": "design_level", "power/area": "power_per_zone_floor_area"},
    "otherequipment": {"equipmentlevel": "design_level", "power/area": "power_per_zone_floor_area"},
}


def _area(poly):
    sx = sy = sz = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1, z1 = poly[i]
        x2, y2, z2 = poly[(i + 1) % n]
        sx += (y1 - y2) * (z1 + z2)
        sy += (z1 - z2) * (x1 + x2)
        sz += (x1 - x2) * (y1 + y2)
    return 0.5 * (sx * sx + sy * sy + sz * sz) ** 0.5


def zone_areas(objects):
    out = {}
    for o in objects:
        if o["cls"].lower() != "buildingsurface:detailed" or (o["fields"].get("surface_type") or "").strip().lower() != "floor":
            continue
        p = idf_pair.polygon(o)
        z = (o["fields"].get("zone_name") or "").strip().lower()
        if p and z:
            out[z] = out.get(z, 0.0) + _area(p)
    return out


def unit(o, areas):
    spec = CLASSES.get(o["cls"].lower())
    if spec is None:
        return None
    fields, method = spec
    keys = [k for k in fields if not V.is_blank(o["fields"].get(k))]
    chosen = METHOD_FIELD.get(o["cls"].lower(), {}).get((o["fields"].get(method) or "").strip().lower())
    if chosen in keys:
        # the calculation method says which of the value fields EnergyPlus uses; the others (a prototype often writes both, for example `Lighting Level 0` next to `Watts per Zone Floor Area`) are not used
        keys = [chosen]
        unused = [k for k in fields if k != chosen and not V.is_blank(o["fields"].get(k))]
    else:
        unused = []
    if not keys:
        return [], ([method] if not V.is_blank(o["fields"].get(method)) else []), 0.0      # no value at all: no load (the other file may state the zero)
    if len(keys) != 1:
        return None
    k = keys[0]
    try:
        v = float(o["fields"][k])
    except ValueError:
        return None
    area = areas.get((o["fields"].get(ZONE_KEY) or "").strip().lower())
    kind = fields[k]
    if kind == "per_area":
        val = v
    elif kind == "area_per":
        val = (1.0 / v) if v else None
    else:
        val = (v / area) if area else None
    if val is None:
        return None
    return [k], ([method] if not V.is_blank(o["fields"].get(method)) else []) + unused, val


SCHEDULE_KEY = {"people": "number_of_people_schedule_name"}      # the other load classes: schedule_name


def schedule_key(cls):
    return SCHEDULE_KEY.get(cls.lower(), "schedule_name")


def effective_multipliers(objects):
    """{zone name (lower case): multiplier} = the Zone multiplier (blank = 1) times the multiplier of every ZoneGroup whose ZoneList holds the zone (a file may write the multiplier of the middle floors on the zone or as a ZoneGroup)."""
    lists = {}
    for o in objects:
        if o["cls"].lower() == "zonelist":
            lists[(o["name"] or "").strip().lower()] = [str(v).strip().lower() for k, v in o["fields"].items() if k.startswith("zones[") and not V.is_blank(v)]
    groups = {}
    for o in objects:
        if o["cls"].lower() == "zonegroup":
            try:
                m = float(o["fields"].get("zone_list_multiplier") or 1)
            except ValueError:
                m = 1.0
            for z in lists.get((o["fields"].get("zone_list_name") or "").strip().lower(), []):
                groups[z] = groups.get(z, 1.0) * m
    out = {}
    for o in objects:
        if o["cls"].lower() == "zone":
            try:
                m = float(o["fields"].get("multiplier") or 1)
            except ValueError:
                m = 1.0
            z = (o["name"] or "").strip().lower()
            out[z] = m * groups.get(z, 1.0)
    return out


INFIL_CLASS = "zoneinfiltration:designflowrate"
INFIL_METHOD = {"flow/zone": "design_flow_rate", "flow/area": "flow_rate_per_floor_area", "flow/exteriorarea": "flow_rate_per_exterior_surface_area",
                "flow/exteriorwallarea": "flow_rate_per_exterior_surface_area", "airchanges/hour": "air_changes_per_hour"}
INFIL_FIELDS = ("design_flow_rate", "flow_rate_per_floor_area", "flow_rate_per_exterior_surface_area", "air_changes_per_hour")


def zone_geometry(objects):
    """{zone (lower case): dict(floor, wall, ext, volume)}: the floor area, the area of the exterior walls (type Wall, boundary condition Outdoors), the area of all exterior surfaces (boundary condition Outdoors) and the
    volume of the Zone object (None when it is not a number), in m2 and m3, from the BuildingSurface:Detailed objects of one file."""
    geo = {}
    for o in objects:
        c = o["cls"].lower()
        if c == "zone":
            z = (o["name"] or "").strip().lower()
            try:
                vol = float(o["fields"].get("volume"))
            except (TypeError, ValueError):
                vol = None
            geo.setdefault(z, dict(floor=0.0, wall=0.0, ext=0.0, volume=None))["volume"] = vol
        elif c == "buildingsurface:detailed":
            p = idf_pair.polygon(o)
            if not p:
                continue
            f = o["fields"]
            z = (f.get("zone_name") or "").strip().lower()
            a = _area(p)
            g = geo.setdefault(z, dict(floor=0.0, wall=0.0, ext=0.0, volume=None))
            t, bc = (f.get("surface_type") or "").strip().lower(), (f.get("outside_boundary_condition") or "").strip().lower()
            if t == "floor":
                g["floor"] += a
            if bc == "outdoors":
                g["ext"] += a
                if t == "wall":
                    g["wall"] += a
    return geo


def infil_unit(o, geo):
    """([value field], [fields that only name the method or are not used], vector) of a ZoneInfiltration:DesignFlowRate object, or None when its flow cannot be told (a ZoneList, an air change rate without a zone volume).
    The vector is (flow in m3/s, flow per m2 of floor, flow per m2 of exterior wall, flow per m2 of exterior surface); an entry is None when that area is 0. The calculation method says which value field is used; the
    flow is the value times the area (or volume) that the method names, in the geometry of the same file."""
    f = o["fields"]
    zone = (f.get(ZONE_KEY) or "").strip().lower()
    g = geo.get(zone)
    if g is None:
        return None
    method = (f.get("design_flow_rate_calculation_method") or "").strip().lower()
    key = INFIL_METHOD.get(method)
    nonblank = [k for k in INFIL_FIELDS if not V.is_blank(f.get(k))]
    if key is None or V.is_blank(f.get(key)):
        if len(nonblank) != 1:
            return None
        key = nonblank[0]
        method = {v: k for k, v in INFIL_METHOD.items()}.get(key, "")
    try:
        v = float(f[key])
    except ValueError:
        return None
    if key == "design_flow_rate":
        q = v
    elif key == "flow_rate_per_floor_area":
        q = v * g["floor"]
    elif key == "flow_rate_per_exterior_surface_area":
        q = v * (g["wall"] if method == "flow/exteriorwallarea" else g["ext"])
    else:
        if not g["volume"]:
            return None
        q = v * g["volume"] / 3600.0
    vec = (q, q / g["floor"] if g["floor"] > 0 else None, q / g["wall"] if g["wall"] > 0 else None, q / g["ext"] if g["ext"] > 0 else None)
    unused = [k for k in INFIL_FIELDS if k != key and not V.is_blank(f.get(k))]
    if not V.is_blank(f.get("design_flow_rate_calculation_method")):
        unused.append("design_flow_rate_calculation_method")
    return [key], unused, vec
