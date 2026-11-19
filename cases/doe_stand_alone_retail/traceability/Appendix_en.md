# Appendix (natural language): DOE Stand-alone Retail, Short IDF, Buffalo

Target IDF: `DOE/Stand-alone_Retail/Short/DOE_RetailStandalone_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A one-storey retail store, **54.27 m x 42.27 m** (178.1 ft x 138.7 ft) in plan, 6.10 m (20 ft) high, 2294 m2 of floor in 5 zones (PDF Table 13: 24,962 ft2, aspect ratio 1.3, floor-to-floor height 20 ft). Local coordinates start at the south-west corner of the building: x to the east, y to the north (the entrance side is the south wall), z up. `GlobalGeometryRules`: upper-left corner, counterclockwise, relative. **The vertices of the surfaces are relative to the origin of their zone** (the `Zone` fields X, Y, Z Origin give the origins). All coordinates are in metres on a 0.01 m grid; the comment of every vertex shows the calculation, the block `Vertex formulas of the ...` explains the symbols.

* **Front row** along the south wall (y = 0 to 6 m): `Point_Of_Sale` (x = 0.00 to 25.14 m, the point of sale, y = 0.00 to 6.00 m), the small `Front_Entry` (x = 25.14 to 29.14 m, y = 0.00 to 3.00 m) and `Front_Retail` (x = 29.14 to 54.27 m, y = 0.00 to 6.00 m). The entry is only 3 m deep: behind it the core zone has a notch (x = 25.14 to 29.14 m, down to y = 9.00 m).
* **`Core_Retail`**: the large sales floor, a polygon with 8 floor vertices, x = 0.00 to 54.27 m, y = 3.00 to 35.27 m: it fills the middle of the building behind the front row, and its notch lies between the point of sale and the front retail zone, behind the entry. 1600 m2.
* **`Back_Space`**: the strip along the north wall, y = 35.27 to 42.27 m, x = 0.00 to 54.27 m, 380 m2.
* All zones are 6.10 m high. The floors are slab on grade (F-factor method, `Construction:FfactorGroundFloor`); the walls between zones are interior walls (reversed pairs of surfaces of the construction `GenericSurface`); the exterior walls (`ExteriorWall`) and the flat roofs (`Roof`, one per zone) face outdoors.
* **Windows** (construction `Window`): 3 windows with together 83.95 m2, all in the south wall: 38.06 m2 in `Point_Of_Sale_Wall_South`, 38.06 m2 in `Front_Retail_Wall_South`, 7.83 m2 in `Front_Entry_Wall_South`. There are no doors in this IDF (the prototype has 13).

| Zone | Origin x, y, z m | x range m | y range m | z range m | Floor polygon area m2 | HVAC template |
|---|---|---|---|---|---|---|
| Back_Space | 0.00, 35.27, 0.00 | 0.00 to 54.27 | 35.27 to 42.27 | 0.00 to 6.10 | 379.9 | HVAC |
| Core_Retail | 0.00, 6.00, 0.00 | 0.00 to 54.27 | 3.00 to 35.27 | 0.00 to 6.10 | 1600.5 | HVAC |
| Point_Of_Sale | 0.00, 0.00, 0.00 | 0.00 to 25.14 | 0.00 to 6.00 | 0.00 to 6.10 | 150.8 | HVAC |
| Front_Retail | 29.14, 0.00, 0.00 | 29.14 to 54.27 | 0.00 to 6.00 | 0.00 to 6.10 | 150.8 | HVAC |
| Front_Entry | 25.14, 0.00, 0.00 | 25.14 to 29.14 | 0.00 to 3.00 | 0.00 to 6.10 | 12.0 | HVAC |

The IDF has 36 building surfaces: 5 floor (groundfcfactormethod), 5 roof (outdoors), 10 wall (outdoors), 16 wall (surface). The vertex coordinates are in `Appendix_IDF.txt`.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per zone that has a value in the xlsx raw_data sheet (the zone names are those of the IDF; the xlsx writes them in capital letters). All fields not named here are empty (EnergyPlus default). The schedule of a zone is the one of its space type in the xlsx sheet Schedule Summary; where the xlsx gives none for a load the schedule `AlwaysOn` or `AlwaysOff` would be written (not needed in this building); the schedule names are the names of the `Schedule:Compact` objects of `Appendix_IDF.txt`.

* **`People`**: name `<zone>_People`; method `Area/Person`; floor area per person = xlsx raw_data column M; activity level schedule `ACTIVITY_SCH`. Schedules:

| Schedule | Zones |
|---|---|
| BLDG_OCC_SCH | Back_Space, Core_Retail, Point_Of_Sale, Front_Retail, Front_Entry |

* **`Lights`**: name `<zone>_Lights`; method `Watts/Area`; watts per floor area = xlsx raw_data column L. Schedules:

| Schedule | Zones |
|---|---|
| ltg_sch_back | Back_Space |
| ltg_sch_core | Core_Retail |
| ltg_sch_sale | Point_Of_Sale |
| ltg_sch_front | Front_Retail |
| ltg_sch_entry | Front_Entry |

* **`ElectricEquipment`**: name `<zone>_Equipment`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process; the entry has none). Schedules:

| Schedule | Zones |
|---|---|
| BLDG_EQUIP_SCH | Back_Space, Core_Retail, Point_Of_Sale, Front_Retail |

* **`ZoneInfiltration:DesignFlowRate`**: `<zone>_Infiltration`: method `Flow/ExteriorWallArea`, flow per exterior surface area = raw_data column R; `<zone>_Door_Infiltration` (`Front_Entry` only): method `Flow/Zone`, no schedule, design flow rate = column T (entrance). Schedules:

| Object | Zone | Method | Schedule |
|---|---|---|---|
| Back_Space_Infiltration | Back_Space | Flow/ExteriorWallArea | INFIL_SCH_PNNL |
| Core_Retail_Infiltration | Core_Retail | Flow/ExteriorWallArea | INFIL_SCH_PNNL |
| Point_Of_Sale_Infiltration | Point_Of_Sale | Flow/ExteriorWallArea | INFIL_SCH_PNNL |
| Front_Retail_Infiltration | Front_Retail | Flow/ExteriorWallArea | INFIL_SCH_PNNL |
| Front_Entry_Infiltration | Front_Entry | Flow/ExteriorWallArea | INFIL_SCH_PNNL |
| Front_Entry_Door_Infiltration | Front_Entry | Flow/Zone | (none: always on) |

* **`HVACTemplate:Thermostat`**: one object `RetailThermostat` for all zones: heating schedule `HTGSETP_SCH_NO_OPTIMUM`, cooling schedule `CLGSETP_SCH_NO_SETBACK` (xlsx Schedule Summary, Heating / Cooling Set Point; the xlsx excepts `Core_Retail` (heating) and `Front_Entry` (cooling), but the template needs both for every zone).

* **`HVACTemplate:System:Unitary`** (5 objects, named by xlsx raw_data column I, one per zone): availability schedule `HVACOperationSchd`; control zone = the zone; economizer type `NoEconomizer` (written explicitly: without it ExpandObjects writes an economizer type that EnergyPlus rejects); heating coil type `Gas`. The four retail zones are xlsx type 3 (PSZ-AC): cooling coil type `SingleSpeedDX` (the default). `Front_Entry` is xlsx type 9 (heating and ventilation, gas-fired warm air furnace): cooling coil type `None`.

* **`HVACTemplate:Zone:Unitary`**: zone name; template system = the unit of the zone; thermostat as above; outdoor air method `Flow/Zone` with the outdoor air per zone of xlsx raw_data column P (m3/s) where the xlsx gives one (not for the entry).

The wall and roof constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.151 Btu/h-ft2-F (Table 21, mass wall: the xlsx names a concrete block wall) and roof U = 0.063 (Table 19, insulation entirely above deck), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25).
