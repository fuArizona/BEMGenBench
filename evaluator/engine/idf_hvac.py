"""idf_hvac.py - the HVAC of an IDF as a set of SYSTEM TYPES, so that two files that write the same kind of HVAC differently (HVACTemplate objects against the full air loops, coils, fans and plant objects) are the same.

  is_hvac_class(cls)      True for every class that belongs to the HVAC (templates, air loops, zone equipment, terminals, coils, fans, plant, controls, sizing, outdoor air specifications ...)
  tags(objects)           {type tag: {"present": True, "doc": bool, "classes": [..]}}: the system types the file has; `doc` = at least one object of that type has a field with a documentary basis

A type tag is a coarse system type: vav, packaged unitary (DX cooling), heat pump air to air, heat pump water to air, constant volume central air handler, ptac, pthp, fan coil, baseboard, unit heater, vrf, dedicated
outdoor air system, chiller, boiler, heat rejection (cooling tower or fluid cooler). The HVACTemplate form and the real objects map to the same tag. The detection is by class (and, for AirLoopHVAC:UnitarySystem, by the type of its heating coil):
it does not look at sizes, efficiencies, set points or schedules: "the same type of HVAC" is all that is compared.
"""
import re

HVAC_PREFIXES = (
    "hvactemplate:", "airloophvac", "zonehvac:", "airterminal:", "coil:", "coilsystem:", "fan:", "boiler:", "chiller:", "coolingtower:", "plantloop", "condenserloop", "plantequipment", "condenserequipment",
    "branch", "connector:", "pump:", "heatexchanger:", "humidifier:", "dehumidifier:", "outdoorair:", "controller:", "setpointmanager:", "availabilitymanager", "unitarysystemperformance:", "sizing:",
    "zonecontrol:", "thermostatsetpoint:", "designspecification:outdoorair", "designspecification:zoneairdistribution", "evaporativecooler:", "waterheater:", "heatpump:", "centralheatpump", "distr",
    "plantcomponent:", "airconditioner:", "energymanagementsystem", "pipe:", "temperingvalve", "exhaustsystem", "fluidcooler:", "evaporativefluidcooler:", "groundheatexchanger:", "nodelist", "plantequipmentoperation", "plantcomponenttemperaturesource",
)


def is_hvac_class(cls):
    c = cls.lower()
    return c.startswith(HVAC_PREFIXES)


# (tag, class prefixes that carry it)
TAGS = [
    ("variable air volume (VAV)", ("hvactemplate:system:vav", "hvactemplate:system:packagedvav", "hvactemplate:zone:vav", "airterminal:singleduct:vav")),
    ("packaged unitary, DX cooling", ("hvactemplate:system:unitary",)),          # HVACTemplate:Zone:Unitary is the zone side of both System:Unitary and System:UnitaryHeatPump, so it carries no type; AirLoopHVAC:UnitarySystem is added below by its coils
    ("heat pump, air to air", ("hvactemplate:system:unitaryheatpump:airtoair", "airloophvac:unitaryheatpump:airtoair", "hvactemplate:zone:pthp", "zonehvac:packagedterminalheatpump")),
    ("heat pump, water to air", ("hvactemplate:zone:watertoairheatpump", "airloophvac:unitaryheatpump:watertoair", "zonehvac:waterToairheatpump".lower())),
    ("PTAC", ("hvactemplate:zone:ptac", "zonehvac:packagedterminalairconditioner")),
    ("fan coil", ("hvactemplate:zone:fancoil", "zonehvac:fourpipefancoil")),
    ("baseboard", ("hvactemplate:zone:baseboardheat", "zonehvac:baseboard:")),
    ("unit heater", ("hvactemplate:zone:unitheater", "zonehvac:unitheater")),
    ("variable refrigerant flow", ("hvactemplate:system:vrf", "hvactemplate:zone:vrf", "airconditioner:variablerefrigerantflow")),
    ("dedicated outdoor air system", ("hvactemplate:system:dedicatedoutdoorair",)),
    ("constant volume central air handler", ("hvactemplate:system:constantvolume", "hvactemplate:zone:constantvolume")),
    ("chiller", ("hvactemplate:plant:chiller", "chiller:")),
    ("boiler", ("hvactemplate:plant:boiler", "boiler:")),
    ("heat rejection (cooling tower or fluid cooler)", ("hvactemplate:plant:tower", "coolingtower:", "fluidcooler:", "evaporativefluidcooler:")),
]


def _match(c, p):
    """The class name c is the class p or one of its sub-classes (a boundary at a colon: `hvactemplate:system:unitary` is not `hvactemplate:system:unitaryheatpump:airtoair`); a prefix that ends with a colon is a family."""
    return c.startswith(p) and (p.endswith(":") or len(c) == len(p) or c[len(p)] == ":")


def tags(objects):
    """{tag: dict(doc=bool, classes=[...])} of the system types in a list of Flat objects (with o["basis"] when idf_basis.annotate ran)."""
    found = {}

    def add(tag, o):
        d = found.setdefault(tag, dict(doc=False, classes=[]))
        if o["cls"] not in d["classes"]:
            d["classes"].append(o["cls"])
        if any(v[0] == "doc" for v in (o.get("basis") or {}).values()):
            d["doc"] = True

    classes = [o["cls"].lower() for o in objects]
    has_cw_coil = any(c.startswith("coil:cooling:water") for c in classes)
    for o in objects:
        c = o["cls"].lower()
        for tag, prefixes in TAGS:
            if any(_match(c, p) for p in prefixes):
                add(tag, o)
        if c == "airloophvac:unitarysystem":
            heat = (o["fields"].get("heating_coil_object_type") or "").lower()
            add("heat pump, air to air" if heat.startswith("coil:heating:dx") else "packaged unitary, DX cooling", o)
        elif c.startswith("airterminal:singleduct:constantvolume") and has_cw_coil:
            add("constant volume central air handler", o)       # a constant volume terminal on a chilled-water air loop
    return found
