# Appendix (natural language): DOE Warehouse, Short IDF, Buffalo

Target IDF: `DOE/Warehouse/Short/DOE_Warehouse_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A one-storey warehouse, **45.72 m x 100.58 m** (150 ft x 330 ft) in plan, 8.53 m (28 ft) high at the highest zone, 4598 m2 of floor in 3 zones (PDF Table 13: aspect ratio 2.2, floor-to-floor height 28 ft). Local coordinates start at the south-west corner of the building: x to the east (the short side), y to the north (the long side), z up; all zone origins are 0, so the vertices are building coordinates (`GlobalGeometryRules`: upper-left corner, counterclockwise, relative). All coordinates are feet x 0.3048 x k with one scale factor k; the comment of every vertex shows the calculation, the blocks `Vertex formulas of the ...` explain the symbols and give k.

* **`Zone1 Office`** (office): a rectangle 25.91 m x 9.14 m (85 ft x 30 ft) in the south-west corner, 4.27 m (14 ft) high, 236.9 m2. Its front (south) wall and its left (west) wall are exterior walls with the four windows; its right (east) and rear (north) walls are interior walls to the Fine Storage, and its roof is an interior surface to the Fine Storage.
* **`Zone2 Fine Storage`** (fine storage): an L-shaped zone with 6 floor vertices: it fills the rest of the southern part of the building, y = 0 to 30.48 m, around the office, that is the part east of the office (x = 25.91 to 45.72 m, y = 0 to 9.14 m) and the band north of it (the full width, y = 9.14 to 30.48 m); 8.53 m (28 ft) high. The floor polygon is 1156.5 m2; its outdoor roof is 1393.4 m2, which is the xlsx area of the zone (the xlsx counts the office plan area in both the office and the fine storage: the roof of the fine storage is a plane over the office as well). The walls on the south, east and west sides are exterior walls, the wall to the bulk storage on the north side is an interior wall.
* **`Zone3 Bulk Storage`** (bulk storage): a rectangle 45.72 m x 70.10 m (150 ft x 230 ft) at the north end, 8.53 m high, 3204.8 m2, exterior walls on three sides.
* **Surfaces**: the floors are slab on grade (F-factor method, `Construction:FfactorGroundFloor`); the walls and the roofs, exterior and interior, all have the construction `GenericSurface` (one layer, 0.2 m2-K/W): the xlsx names a metal building wall and roof but neither the xlsx nor the PDF gives a U-value, so the layer is only what EnergyPlus needs. The interior wall pairs and the interior roof have the same single layer, as EnergyPlus requires.
* **Windows** (construction `Window`): 4 windows with together 17.66 m2 (the xlsx window glass area is 17.66 m2, all of it in the office; the window fraction of the exterior wall is the xlsx Building Summary N7 = 0.0071): two in the front wall (5.58 m2 each) and two in the left wall (3.25 m2 each). There are no doors in this IDF (the prototype has 28).

| Zone | x range m | y range m | z range m | Floor polygon area m2 |
|---|---|---|---|---|
| Zone1 Office | 0.00 to 25.91 | 0.00 to 9.14 | 0.00 to 4.27 | 236.9 |
| Zone2 Fine Storage | 0.00 to 45.72 | 0.00 to 30.48 | 0.00 to 8.53 | 1156.5 |
| Zone3 Bulk Storage | 0.00 to 45.72 | 30.48 to 100.58 | 0.00 to 8.53 | 3204.8 |

The IDF has 19 building surfaces: 3 floor (groundfcfactormethod), 2 roof (outdoors), 1 roof (zone), 10 wall (outdoors), 3 wall (zone). The vertex coordinates are in `Appendix_IDF.txt`.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per zone that has a value in the xlsx raw_data sheet (the zone names are those of the IDF; the xlsx writes them in capital letters). All fields not named here are empty (EnergyPlus default). The schedule of a zone is the one of its space type in the xlsx sheet Schedule Summary; the schedule names are the names of the `Schedule:Compact` objects of `Appendix_IDF.txt`.

* **`People`**: name `<zone>_People`; method `Area/Person`; floor area per person = xlsx raw_data column M; activity level schedule `ACTIVITY_SCH`. Zones and schedules:

| Object | Zone | Schedule |
|---|---|---|
| Zone1 Office_People | Zone1 Office | BLDG_OCC_SCH |
| Zone2 Fine Storage_People | Zone2 Fine Storage | BLDG_OCC_SCH |
| Zone3 Bulk Storage_People | Zone3 Bulk Storage | BLDG_OCC_SCH |

* **`Lights`**: name `<zone>_Lights`; method `Watts/Area`; watts per floor area = xlsx raw_data column L. Schedules:

| Object | Zone | Schedule |
|---|---|---|
| Zone1 Office_Lights | Zone1 Office | ltg_sch_office |
| Zone2 Fine Storage_Lights | Zone2 Fine Storage | ltg_sch_fine_storage |
| Zone3 Bulk Storage_Lights | Zone3 Bulk Storage | ltg_sch_bulk_storage |

* **`ElectricEquipment`**: name `<zone>_Equipment`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process; the fine storage has none). Schedules:

| Object | Zone | Schedule |
|---|---|---|
| Zone1 Office_Equipment | Zone1 Office | Office_Plug_SCH |
| Zone3 Bulk Storage_Equipment | Zone3 Bulk Storage | Bulk Storage Plug Schedule |

* **`ZoneInfiltration:DesignFlowRate`**: `<zone>_Infiltration`: method `Flow/ExteriorWallArea`, flow per exterior surface area = raw_data column R; `<zone>_Door_Infiltration` (the office only): method `Flow/Zone`, no schedule, design flow rate = column T (entrance). Schedules:

| Object | Zone | Method | Schedule |
|---|---|---|---|
| Zone1 Office_Infiltration | Zone1 Office | Flow/ExteriorWallArea | Office Infil Schedule |
| Zone1 Office_Door_Infiltration | Zone1 Office | Flow/Zone | (none: always on) |
| Zone2 Fine Storage_Infiltration | Zone2 Fine Storage | Flow/ExteriorWallArea | Fine Sorage Infil Schedule |
| Zone3 Bulk Storage_Infiltration | Zone3 Bulk Storage | Flow/ExteriorWallArea | Bulk Storage Infil_Base Schedule |

* **`HVACTemplate:Thermostat`** (xlsx Schedule Summary, Heating / Cooling Set Point):

| Object | Heating schedule | Cooling schedule |
|---|---|---|
| OfficeThermostat | Office Heating Schedule | Office Cooling Schedule |
| FineStorageThermostat | Fine Storage Heating Setpoint Schedule | Fine Storage Cooling Setpoint Schedule |
| BulkStorageThermostat | Bulk Storage Heating Setpoint Schedule | Fine Storage Cooling Setpoint Schedule |

* **`HVACTemplate:System:Unitary`** (3 objects, named by xlsx raw_data column I, one per zone): availability schedule `COMPACT HVAC-ALWAYS 1`; control zone = the zone; economizer type `NoEconomizer` (written explicitly: without it ExpandObjects writes an economizer type that EnergyPlus rejects); heating coil type `Gas`. The office and the fine storage are xlsx type 3 (PSZ-AC): cooling coil type `SingleSpeedDX` (the default). The bulk storage is xlsx type 9 (heating and ventilation, gas-fired warm air furnace): cooling coil type `None`.

* **`HVACTemplate:Zone:Unitary`**: zone name; template system = the unit of the zone; thermostat as in the table above (`OfficeThermostat`, `FineStorageThermostat`, `BulkStorageThermostat`); outdoor air method `Flow/Zone` with the outdoor air per zone of xlsx raw_data column P (m3/s) for the office and the fine storage; the bulk storage has none in the xlsx.

The bulk storage has no cooling in the xlsx and no cooling set point; the template thermostat needs one, so the cooling set point of the fine storage is written (the zone has no cooling equipment, so it has no effect). The window U and SHGC come from the NREL PDF (Chicago 5A, new construction): U = 0.57 Btu/h-ft2-F (Table 24), SHGC = 0.39 (Table 25). Where the xlsx gives no schedule for the people, lights or equipment of a zone, the schedule `AlwaysOff` (value 0) would be used; in this building every zone has one.
