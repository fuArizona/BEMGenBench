# Appendix (natural language): DOE Large Office, Short IDF, Buffalo

Target IDF: `DOE/Large_Office/Short/DOE_OfficeLarge_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A 12-storey office building with a basement, **73.11 m x 48.74 m** (239.9 ft x 159.9 ft) in plan (PDF Table 13: 498,588 ft2, 12 floors, aspect ratio 1.5, floor-to-floor height 13 ft), 46320 m2 of floor in 20 conditioned zones and 3 plenum zones. Local coordinates start at the south-west corner of the building: x to the east, y to the north, z up (z = 0 is the ground floor; the basement is below it, from z = -2.44 m to 0). `GlobalGeometryRules`: upper-left corner, counterclockwise, relative. **The vertices of the surfaces are relative to the origin of their zone**: the zones of the data centers have non-zero origins (`Zone` fields X, Y, Z Origin); all other zones have the origin 0. All coordinates are feet x 0.3048 x k with one scale factor k; the comment of every vertex shows the calculation, the blocks `Vertex formulas of the ...` explain the symbols and give k.

Three levels are modelled, and the middle level stands for ten floors by the zone multiplier 10 (z = 16.77 m is the position of the modelled middle floor):

* **Ground floor ("bottom")**, z = 0 to 2.74 m ceiling height (2.74 m = 9 ft), plus a plenum of 1.22 m (4 ft) above it: the core `Core_bottom` (63.05 m x 39.59 m), four perimeter zones around it (`Perimeter_bot_ZN_1` south, `_ZN_2` east, `_ZN_3` north, `_ZN_4` west) 4.57 m (15 ft) deep, the plenum `GroundFloor_Plenum` over the whole plate, and the thin data center `DataCenter_bot_ZN_6` between the west perimeter zone and the core.
* **Middle floor**: the same zones with the names `..._mid_...` and `MidFloor_Plenum`, all with multiplier 10.
* **Top floor**: the same zones with the names `..._top_...` and `TopFloor_Plenum`.
* **Basement** (`Basement`, 57.03 m x 48.74 m, 2779 m2) and the data center `DataCenter_basement_ZN_6` (16.08 m x 48.74 m, 784 m2) west of it, from z = -2.44 m to 0.
* The four perimeter zones of a level meet at the corners along 45 degree lines (trapezoids), so the plan sizes in the zone table are bounding rectangles. The floors of the perimeter zones of the ground floor are in two parts: the part over the basement and the part over the ground.
* **Surfaces**: the exterior walls (`ExteriorWall`) and the flat roof of the top plenum (`Roof`) face outdoors; the walls below grade of the basement and the data center basement use the C-factor method (`Construction:CfactorUndergroundWall`); the floor of the basement is adiabatic; between the zones the walls, floors and ceilings are interior surfaces (`Surface` or `Zone` boundary condition, reversed pairs of surfaces of the construction `GenericSurface`; the ceilings of the occupied zones face the plenum).
* **Windows** (construction `Window`): 24 windows with together 1158.95 m2 on the perimeter zones (the xlsx window glass area is 4,635.8 m2 with the multipliers). There are no doors in this IDF (the prototype has 12).

| Zone | Multiplier | x range m | y range m | z range m | Floor polygon area m2 | HVAC template |
|---|---|---|---|---|---|---|
| Basement | 1 | 16.08 to 73.11 | 0.00 to 48.74 | -2.44 to 0.00 | 2779.4 | HVAC |
| Core_bottom | 1 | 5.49 to 68.53 | 4.57 to 44.16 | 0.00 to 2.74 | 2496.1 | HVAC |
| Core_mid | 10 | 5.49 to 68.53 | 4.57 to 44.16 | 16.77 to 19.51 | 2496.1 | HVAC |
| Core_top | 1 | 5.49 to 68.53 | 4.57 to 44.16 | 33.54 to 36.28 | 2496.1 | HVAC |
| Perimeter_bot_ZN_3 | 1 | 0.00 to 73.11 | 44.16 to 48.74 | 0.00 to 2.74 | 313.4 | HVAC |
| Perimeter_bot_ZN_2 | 1 | 68.53 to 73.11 | 0.00 to 48.74 | 0.00 to 2.74 | 202.0 | HVAC |
| Perimeter_bot_ZN_1 | 1 | 0.00 to 73.11 | 0.00 to 4.57 | 0.00 to 2.74 | 313.4 | HVAC |
| Perimeter_bot_ZN_4 | 1 | 0.00 to 4.57 | 0.00 to 48.74 | 0.00 to 2.74 | 202.0 | HVAC |
| Perimeter_mid_ZN_3 | 10 | 0.00 to 73.11 | 44.16 to 48.74 | 16.77 to 19.51 | 313.4 | HVAC |
| Perimeter_mid_ZN_2 | 10 | 68.53 to 73.11 | 0.00 to 48.74 | 16.77 to 19.51 | 202.0 | HVAC |
| Perimeter_mid_ZN_1 | 10 | 0.00 to 73.11 | 0.00 to 4.57 | 16.77 to 19.51 | 313.4 | HVAC |
| Perimeter_mid_ZN_4 | 10 | 0.00 to 4.57 | 0.00 to 48.74 | 16.77 to 19.51 | 202.0 | HVAC |
| Perimeter_top_ZN_3 | 1 | 0.00 to 73.11 | 44.16 to 48.74 | 33.54 to 36.28 | 313.4 | HVAC |
| Perimeter_top_ZN_2 | 1 | 68.53 to 73.11 | 0.00 to 48.74 | 33.54 to 36.28 | 202.0 | HVAC |
| Perimeter_top_ZN_1 | 1 | 0.00 to 73.11 | 0.00 to 4.57 | 33.54 to 36.28 | 313.4 | HVAC |
| Perimeter_top_ZN_4 | 1 | 0.00 to 4.57 | 0.00 to 48.74 | 33.54 to 36.28 | 202.0 | HVAC |
| GroundFloor_Plenum | 1 | 0.00 to 73.11 | 0.00 to 48.74 | 2.74 to 3.96 | - | none |
| MidFloor_Plenum | 10 | 0.00 to 73.11 | 0.00 to 48.74 | 19.51 to 20.73 | - | none |
| TopFloor_Plenum | 1 | 0.00 to 73.11 | 0.00 to 48.74 | 36.28 to 37.50 | - | none |
| DataCenter_bot_ZN_6 | 1 | 4.57 to 5.49 | 4.57 to 44.16 | 0.00 to 2.74 | 36.2 | HVAC |
| DataCenter_mid_ZN_6 | 10 | 4.57 to 5.49 | 4.57 to 44.16 | 16.77 to 19.51 | 36.2 | HVAC |
| DataCenter_top_ZN_6 | 1 | 4.57 to 5.49 | 4.57 to 44.16 | 33.54 to 36.28 | 36.2 | HVAC |
| DataCenter_basement_ZN_6 | 1 | 0.00 to 16.08 | 0.00 to 48.74 | -2.44 to 0.00 | 783.7 | HVAC |

The IDF has 151 building surfaces: 11 ceiling (surface), 18 ceiling (zone), 2 floor (adiabatic), 21 floor (surface), 1 roof (outdoors), 6 wall (groundfcfactormethod), 24 wall (outdoors), 68 wall (surface). The vertex coordinates are in `Appendix_IDF.txt`. The floor polygon area is the sum of the surfaces of type Floor of the zone (the plenums have none: their floors are the ceilings of the zones below; the area of the plenum rows of the xlsx is the plate area).

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per zone that has a value in the xlsx raw_data sheet (the zone names are those of the IDF; the xlsx writes them in capital letters). All fields not named here are empty (EnergyPlus default). The schedule of a zone is the one of its space type in the xlsx sheet Schedule Summary; where the xlsx gives none for a load the schedule `AlwaysOn` (when the schedule of the prototype is constant 1) or `AlwaysOff` is written; the schedule names are the names of the `Schedule:Compact` objects of `Appendix_IDF.txt`.

* **`People`**: name `<zone>_People`; method `Area/Person`; floor area per person = xlsx raw_data column M; activity level schedule `ACTIVITY_SCH`. Schedules:

| Schedule | Zones |
|---|---|
| BLDG_OCC_SCH_wo_SB | Basement, Core_bottom, Core_mid, Core_top, Perimeter_bot_ZN_3, Perimeter_bot_ZN_2, Perimeter_bot_ZN_1, Perimeter_bot_ZN_4, Perimeter_mid_ZN_3, Perimeter_mid_ZN_1, Perimeter_mid_ZN_4, Perimeter_top_ZN_3, Perimeter_top_ZN_2, Perimeter_top_ZN_1, Perimeter_top_ZN_4, DataCenter_bot_ZN_6, DataCenter_mid_ZN_6, DataCenter_top_ZN_6, DataCenter_basement_ZN_6 |
| AlwaysOff | Perimeter_mid_ZN_2 |

* **`Lights`**: name `<zone>_Lights`; method `Watts/Area`; watts per floor area = xlsx raw_data column L. Schedules:

| Schedule | Zones |
|---|---|
| ltg_sch_office | Basement, Core_bottom, Core_mid, Core_top, Perimeter_bot_ZN_3, Perimeter_bot_ZN_2, Perimeter_bot_ZN_1, Perimeter_bot_ZN_4, Perimeter_mid_ZN_3, Perimeter_mid_ZN_2, Perimeter_mid_ZN_1, Perimeter_mid_ZN_4, Perimeter_top_ZN_3, Perimeter_top_ZN_2, Perimeter_top_ZN_1, Perimeter_top_ZN_4, DataCenter_basement_ZN_6 |
| ltg_sch_datacenter | DataCenter_bot_ZN_6, DataCenter_mid_ZN_6, DataCenter_top_ZN_6 |

* **`ElectricEquipment`**: name `<zone>_Equipment`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process). Schedules:

| Schedule | Zones |
|---|---|
| AlwaysOn | Basement, DataCenter_bot_ZN_6, DataCenter_mid_ZN_6, DataCenter_top_ZN_6, DataCenter_basement_ZN_6 |
| BLDG_EQUIP_SCH | Core_bottom, Core_mid, Core_top, Perimeter_bot_ZN_3, Perimeter_bot_ZN_2, Perimeter_bot_ZN_1, Perimeter_bot_ZN_4, Perimeter_mid_ZN_3, Perimeter_mid_ZN_2, Perimeter_mid_ZN_1, Perimeter_mid_ZN_4, Perimeter_top_ZN_3, Perimeter_top_ZN_2, Perimeter_top_ZN_1, Perimeter_top_ZN_4 |

* **`ZoneInfiltration:DesignFlowRate`**: name `<zone>_Infiltration` for every perimeter zone and every plenum (xlsx raw_data column R, flow per exterior surface area); method `Flow/ExteriorWallArea`; schedule `INFIL_SCH_PNNL`. The columns S and T (zone flow, entrances) are 0 in the xlsx.

* **`HVACTemplate:Thermostat`**: one object `OfficeThermostat` for all zones: heating schedule `HTGSETP_SCH_YES_OPTIMUM`, cooling schedule `CLGSETP_SCH_NO_SETBACK` (xlsx Schedule Summary, Heating / Cooling Set Point; the xlsx excepts the basement and the data centers from them, but the template needs a thermostat for every zone).

* **`HVACTemplate:System:VAV`** (3 objects, named by xlsx raw_data column I: `VAV_BOT WITH REHEAT`, `VAV_MID WITH REHEAT`, `VAV_TOP WITH REHEAT`; one per level): availability schedule `HVACOperationSchd`; cooling coil type `ChilledWater`; heating coil type `HotWater`; economizer type `NoEconomizer`.

* **`HVACTemplate:Zone:VAV`** (15 objects, the cores and the perimeter zones): zone name; template system = the VAV system of its level; thermostat as above; outdoor air method `Flow/Area` with the outdoor air per floor area of the xlsx sheet Zone and HVAC System Summary (0.000508 m3/s-m2); reheat coil type `HotWater`.

* **`HVACTemplate:System:ConstantVolume`** (1 object `CAV_BAS` of the basement, xlsx type 12 SZ-CV-HW) with `HVACTemplate:Zone:ConstantVolume` (zone name, outdoor air `Flow/Zone` = xlsx raw_data column P): cooling coil `ChilledWater`, heating coil `HotWater`, economizer `NoEconomizer`.

* **`HVACTemplate:Zone:WaterToAirHeatPump`** (4 objects, the data centers, xlsx type 14 WSHP (CRAC)): zone name; thermostat as above; outdoor air `Flow/Zone` = xlsx raw_data column P; no availability schedule (always on).

The plant loops (chilled water, hot water, mixed water with their chiller, boilers and towers) are in `Appendix_IDF.txt`: the xlsx names the system types only. The wall and roof constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.151 Btu/h-ft2-F (Table 21, mass wall) and roof U = 0.063 (Table 19, insulation entirely above deck), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25).
