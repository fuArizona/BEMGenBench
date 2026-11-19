# Appendix (natural language): DOE Strip Mall, Short IDF, Buffalo

Target IDF: `DOE/Strip_Mall/Short/DOE_RetailStripmall_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A one-storey strip mall, **91.44 m x 22.86 m** (300 ft x 75 ft) in plan, 5.18 m (17 ft) high, 2090 m2 of floor in 10 zones (PDF Table 13: 22,500 ft2, aspect ratio 4.0, floor-to-floor height 17 ft). Local coordinates start at the south-west corner of the building: x to the east (the long side), y to the north, z up; all zone origins are 0, so the vertices are building coordinates. `GlobalGeometryRules`: upper-left corner, counterclockwise, relative. All coordinates are feet x 0.3048; the comment of every vertex shows the calculation, the block `Vertex formulas of the ...` explains the symbols.

* **Ten stores in a row** along the long side of the building, each the full depth of the building (22.86 m = 75 ft) and 5.18 m high, separated by interior walls: from west to east `LGstore1` (x = 0.00 to 15.24 m), `SMstore1` (x = 15.24 to 22.86 m), `SMstore2` (x = 22.86 to 30.48 m), `SMstore3` (x = 30.48 to 38.10 m), `SMstore4` (x = 38.10 to 45.72 m), `LGstore2` (x = 45.72 to 60.96 m), `SMstore5` (x = 60.96 to 68.58 m), `SMstore6` (x = 68.58 to 76.20 m), `SMstore7` (x = 76.20 to 83.82 m), `SMstore8` (x = 83.82 to 91.44 m). The two large stores (`LGstore1`, `LGstore2`) are 15.24 m (50 ft) wide, the eight small stores 7.62 m (25 ft).
* **Surfaces**: each store has a floor (slab on grade, F-factor method, `Construction:FfactorGroundFloor`), a flat roof (`Roof`) and four walls; the exterior walls (`ExteriorWall`) are the front, rear and end walls; the walls between neighbouring stores are interior walls (reversed pairs of surfaces of the construction `GenericSurface`).
* **Windows and glass doors** (construction `Window`): 24 windows and 12 glass doors with together 124.40 m2, in the front wall (south, y = 0) of the stores: LGstore1: 4 windows, 2 glass doors, SMstore1: 2 windows, 1 glass doors, SMstore2: 2 windows, 1 glass doors, SMstore3: 2 windows, 1 glass doors, SMstore4: 2 windows, 1 glass doors, LGstore2: 4 windows, 2 glass doors, SMstore5: 2 windows, 1 glass doors, SMstore6: 2 windows, 1 glass doors, SMstore7: 2 windows, 1 glass doors, SMstore8: 2 windows, 1 glass doors. There are no swinging doors in this IDF (the prototype has 12).

| Zone | Origin x, y, z m | x range m | y range m | z range m | Floor polygon area m2 | HVAC template |
|---|---|---|---|---|---|---|
| LGstore1 | 0.00, 0.00, 0.00 | 0.00 to 15.24 | 0.00 to 22.86 | 0.00 to 5.18 | 348.4 | HVAC |
| SMstore1 | 0.00, 0.00, 0.00 | 15.24 to 22.86 | 0.00 to 22.86 | 0.00 to 5.18 | 174.2 | HVAC |
| SMstore2 | 0.00, 0.00, 0.00 | 22.86 to 30.48 | 0.00 to 22.86 | 0.00 to 5.18 | 174.2 | HVAC |
| SMstore3 | 0.00, 0.00, 0.00 | 30.48 to 38.10 | 0.00 to 22.86 | 0.00 to 5.18 | 174.2 | HVAC |
| SMstore4 | 0.00, 0.00, 0.00 | 38.10 to 45.72 | 0.00 to 22.86 | 0.00 to 5.18 | 174.2 | HVAC |
| LGstore2 | 0.00, 0.00, 0.00 | 45.72 to 60.96 | 0.00 to 22.86 | 0.00 to 5.18 | 348.4 | HVAC |
| SMstore5 | 0.00, 0.00, 0.00 | 60.96 to 68.58 | 0.00 to 22.86 | 0.00 to 5.18 | 174.2 | HVAC |
| SMstore6 | 0.00, 0.00, 0.00 | 68.58 to 76.20 | 0.00 to 22.86 | 0.00 to 5.18 | 174.2 | HVAC |
| SMstore7 | 0.00, 0.00, 0.00 | 76.20 to 83.82 | 0.00 to 22.86 | 0.00 to 5.18 | 174.2 | HVAC |
| SMstore8 | 0.00, 0.00, 0.00 | 83.82 to 91.44 | 0.00 to 22.86 | 0.00 to 5.18 | 174.2 | HVAC |

The IDF has 60 building surfaces: 10 floor (groundfcfactormethod), 10 roof (outdoors), 22 wall (outdoors), 18 wall (surface). The vertex coordinates are in `Appendix_IDF.txt`.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per zone that has a value in the xlsx raw_data sheet (the zone names are those of the IDF; the xlsx writes them in capital letters). All fields not named here are empty (EnergyPlus default). The schedule of a zone is the one of its space type in the xlsx sheet Schedule Summary; where the xlsx gives none for a load the schedule `AlwaysOn` or `AlwaysOff` would be written (not needed in this building); the schedule names are the names of the `Schedule:Compact` objects of `Appendix_IDF.txt`.

* **`People`**: name `<zone>_People`; method `Area/Person`; floor area per person = xlsx raw_data column M; activity level schedule `ACTIVITY_SCH`. Schedules:

| Schedule | Zones |
|---|---|
| Type1_OCC_SCH | LGstore1, SMstore1 |
| Type2_OCC_SCH | SMstore2, SMstore3, SMstore4 |
| Type3_OCC_SCH | LGstore2, SMstore5, SMstore6, SMstore7, SMstore8 |

* **`Lights`**: name `<zone>_Lights`; method `Watts/Area`; watts per floor area = xlsx raw_data column L. Schedules:

| Schedule | Zones |
|---|---|
| ltg_sch_base_lpd1 | LGstore1 |
| ltg_sch_base_small_lpd1 | SMstore1 |
| ltg_sch_base_small_lpd2_type2 | SMstore2, SMstore3, SMstore4 |
| ltg_sch_base_lpd2 | LGstore2 |
| ltg_sch_base_small_lpd2_type3 | SMstore5, SMstore6, SMstore7, SMstore8 |

* **`ElectricEquipment`**: name `<zone>_Equipment`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process). Schedules:

| Schedule | Zones |
|---|---|
| Type1_EQUIP_SCH | LGstore1, SMstore1 |
| Type2_EQUIP_SCH | SMstore2, SMstore3, SMstore4 |
| Type3_EQUIP_SCH | LGstore2, SMstore5, SMstore6, SMstore7, SMstore8 |

* **`ZoneInfiltration:DesignFlowRate`**: `<zone>_Infiltration`: method `Flow/ExteriorWallArea`, flow per exterior surface area = raw_data column R; `<zone>_Door_Infiltration` (every store): method `Flow/Zone`, no schedule, design flow rate = column T (entrance). Schedules:

| Object | Zone | Method | Schedule |
|---|---|---|---|
| LGstore1_Infiltration | LGstore1 | Flow/ExteriorWallArea | Type1_Infil_SCH |
| LGstore1_Door_Infiltration | LGstore1 | Flow/Zone | (none: always on) |
| SMstore1_Infiltration | SMstore1 | Flow/ExteriorWallArea | Type1_Infil_SCH |
| SMstore1_Door_Infiltration | SMstore1 | Flow/Zone | (none: always on) |
| SMstore2_Infiltration | SMstore2 | Flow/ExteriorWallArea | Type2_Infil_SCH |
| SMstore2_Door_Infiltration | SMstore2 | Flow/Zone | (none: always on) |
| SMstore3_Infiltration | SMstore3 | Flow/ExteriorWallArea | Type2_Infil_SCH |
| SMstore3_Door_Infiltration | SMstore3 | Flow/Zone | (none: always on) |
| SMstore4_Infiltration | SMstore4 | Flow/ExteriorWallArea | Type2_Infil_SCH |
| SMstore4_Door_Infiltration | SMstore4 | Flow/Zone | (none: always on) |
| LGstore2_Infiltration | LGstore2 | Flow/ExteriorWallArea | Type3_Infil_SCH |
| LGstore2_Door_Infiltration | LGstore2 | Flow/Zone | (none: always on) |
| SMstore5_Infiltration | SMstore5 | Flow/ExteriorWallArea | Type3_Infil_SCH |
| SMstore5_Door_Infiltration | SMstore5 | Flow/Zone | (none: always on) |
| SMstore6_Infiltration | SMstore6 | Flow/ExteriorWallArea | Type3_Infil_SCH |
| SMstore6_Door_Infiltration | SMstore6 | Flow/Zone | (none: always on) |
| SMstore7_Infiltration | SMstore7 | Flow/ExteriorWallArea | Type3_Infil_SCH |
| SMstore7_Door_Infiltration | SMstore7 | Flow/Zone | (none: always on) |
| SMstore8_Infiltration | SMstore8 | Flow/ExteriorWallArea | Type3_Infil_SCH |
| SMstore8_Door_Infiltration | SMstore8 | Flow/Zone | (none: always on) |

* **`HVACTemplate:Thermostat`** (xlsx Schedule Summary, Heating / Cooling Set Point; each zone uses the schedules of its set point control in the prototype, checked against the xlsx hourly values):

| Object | Heating schedule | Cooling schedule | Zones |
|---|---|---|---|
| StripMallThermostat1 | Type1_HTGSETP_SCH_NO_OPTIMUM | Type1_CLGSETP_SCH_NO_SETBACK | LGstore1, SMstore1 |
| StripMallThermostat2 | Type2_HTGSETP_SCH_NO_OPTIMUM | Type2_CLGSETP_SCH_NO_SETBACK | SMstore2, SMstore3, SMstore4 |
| StripMallThermostat3 | Type3_HTGSETP_SCH_NO_OPTIMUM | Type3_CLGSETP_SCH_NO_SETBACK | LGstore2, SMstore5, SMstore6, SMstore7, SMstore8 |

* **`HVACTemplate:System:Unitary`** (10 objects, named by xlsx raw_data column I, one per zone): availability schedule `Type1_FAN_SCH`; control zone = the zone; economizer type `NoEconomizer` (written explicitly: without it ExpandObjects writes an economizer type that EnergyPlus rejects); heating coil type `Gas`. All stores are xlsx type 3 (PSZ-AC): cooling coil type `SingleSpeedDX` (the default).

* **`HVACTemplate:Zone:Unitary`**: zone name; template system = the unit of the zone; thermostat as above; outdoor air method `Flow/Zone` with the outdoor air per zone of xlsx raw_data column P (m3/s) (all stores).

The wall and roof constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.084 Btu/h-ft2-F (Table 20, steel-frame wall: the xlsx names a steel-framed wall) and roof U = 0.063 (Table 19, insulation entirely above deck), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25).
