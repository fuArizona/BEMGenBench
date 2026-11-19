# Appendix (natural language): DOE Medium Office, Short IDF, Buffalo

Target IDF: `DOE/Medium_Office/Short/DOE_OfficeMedium_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A three-storey office building, **49.91 m x 33.27 m** (163.75 ft x 109.17 ft) in plan, 4982 m2 of conditioned floor (1660.7 m2 per storey). Local coordinates start at the south-west corner of the building: x to the east, y to the north, z up; all zone origins are 0, so the vertices are building coordinates (`GlobalGeometryRules`: upper-left corner, counterclockwise, relative).

* **Every storey has five conditioned zones**: a core zone, 40.76 m x 24.13 m, and four perimeter zones, strips 4.57 m (15 ft) deep around it. `Perimeter_*_ZN_1` is the south strip and `Perimeter_*_ZN_3` the north strip (the full width of the building); `Perimeter_*_ZN_2` is the east strip and `Perimeter_*_ZN_4` the west strip. The four strips meet at the corners along 45 degree lines, so the plan sizes in the zone table are bounding rectangles and the floor areas are smaller than the rectangles. The zones are called `Core_bottom`, `Core_mid`, `Core_top` and `Perimeter_bot_ZN_1` ... `Perimeter_top_ZN_4`.
* **Every storey has a plenum zone above it** (`FirstFloor_Plenum`, `MidFloor_Plenum`, `TopFloor_Plenum`), the full plan of the building and 1.22 m (4 ft) high. The conditioned zones are 2.74 m (9 ft) high, so the floor-to-floor height is 3.96 m (13 ft). The plenums are rows of the xlsx (area, multiplier, infiltration) and have no HVAC.
* **Surfaces**: the ceiling of every conditioned zone faces the plenum above it, and the floor of every conditioned zone of the middle and top storey faces the plenum below it (interior surfaces, construction `InteriorSurface`, boundary condition `Zone`); the plenum zones have no floor or ceiling of their own, only their four exterior walls (the top plenum also the roof). The walls between the core and the perimeter zones and between neighbouring perimeter zones are interior walls. The exterior walls (`ExteriorWall`) of the perimeter zones and of the plenums face outdoors; the roof (`Roof`) is one flat surface on top of the top plenum. The floors of the four perimeter zones of the bottom storey are slab on grade (F-factor method, `Construction:FfactorGroundFloor`); the floor of `Core_bottom` is adiabatic.
* **Windows** (construction `Window`, 18 windows, no doors): a window band in the exterior wall of every perimeter zone.

| Exterior wall | Windows | Widths | Height | Sill z | Glass area m2 |
|---|---|---|---|---|---|
| Perimeter_bot_ZN_1_Wall_South | 3 | 15.82 m + 15.82 m + 15.82 m | 1.37 m | 0.95 m | 65.3 |
| Perimeter_bot_ZN_3_Wall_North | 3 | 15.82 m + 15.82 m + 15.82 m | 1.37 m | 0.95 m | 65.3 |
| Perimeter_bot_ZN_2_Wall_East | 2 | 30.84 m + 1.22 m | 1.36 m | 0.97 m | 43.5 |
| Perimeter_bot_ZN_4_Wall_West | 2 | 30.84 m + 1.22 m | 1.36 m | 0.97 m | 43.5 |
| Perimeter_mid_ZN_1_Wall_South | 1 | 49.91 m | 1.31 m | 4.98 m | 65.3 |
| Perimeter_mid_ZN_2_Wall_East | 1 | 33.27 m | 1.31 m | 4.98 m | 43.5 |
| Perimeter_mid_ZN_3_Wall_North | 1 | 49.91 m | 1.31 m | 4.98 m | 65.3 |
| Perimeter_mid_ZN_4_Wall_West | 1 | 33.27 m | 1.31 m | 4.98 m | 43.5 |
| Perimeter_top_ZN_1_Wall_South | 1 | 49.91 m | 1.31 m | 8.95 m | 65.3 |
| Perimeter_top_ZN_2_Wall_East | 1 | 33.27 m | 1.31 m | 8.95 m | 43.5 |
| Perimeter_top_ZN_3_Wall_North | 1 | 49.91 m | 1.31 m | 8.95 m | 65.3 |
| Perimeter_top_ZN_4_Wall_West | 1 | 33.27 m | 1.31 m | 8.95 m | 43.5 |

The windows add up to 652.62 m2. On the bottom storey the south and north walls have three windows each and the east and west walls one long window and one short window; on the middle and top storey every perimeter wall has one continuous window band.

| Zone | Plan x by y m | z range m | Floor area m2 |
|---|---|---|---|
| Core_bottom | 40.76 x 24.13 | 0.00 to 2.74 | 983.5 |
| TopFloor_Plenum | 49.91 x 33.27 | 10.67 to 11.89 | plenum |
| MidFloor_Plenum | 49.91 x 33.27 | 6.71 to 7.92 | plenum |
| FirstFloor_Plenum | 49.91 x 33.27 | 2.74 to 3.96 | plenum |
| Core_mid | 40.76 x 24.13 | 3.96 to 6.71 | 983.5 |
| Core_top | 40.76 x 24.13 | 7.92 to 10.67 | 983.5 |
| Perimeter_top_ZN_3 | 49.91 x 4.57 | 7.92 to 10.67 | 207.3 |
| Perimeter_top_ZN_2 | 4.57 x 33.27 | 7.92 to 10.67 | 131.3 |
| Perimeter_top_ZN_1 | 49.91 x 4.57 | 7.92 to 10.67 | 207.3 |
| Perimeter_top_ZN_4 | 4.57 x 33.27 | 7.92 to 10.67 | 131.3 |
| Perimeter_bot_ZN_3 | 49.91 x 4.57 | 0.00 to 2.74 | 207.3 |
| Perimeter_bot_ZN_2 | 4.57 x 33.27 | 0.00 to 2.74 | 131.3 |
| Perimeter_bot_ZN_1 | 49.91 x 4.57 | 0.00 to 2.74 | 207.3 |
| Perimeter_bot_ZN_4 | 4.57 x 33.27 | 0.00 to 2.74 | 131.3 |
| Perimeter_mid_ZN_3 | 49.91 x 4.57 | 3.96 to 6.71 | 207.3 |
| Perimeter_mid_ZN_2 | 4.57 x 33.27 | 3.96 to 6.71 | 131.3 |
| Perimeter_mid_ZN_1 | 49.91 x 4.57 | 3.96 to 6.71 | 207.3 |
| Perimeter_mid_ZN_4 | 4.57 x 33.27 | 3.96 to 6.71 | 131.3 |

The IDF has 79 building surfaces: 15 ceiling (zone), 1 floor (adiabatic), 4 floor (groundfcfactormethod), 10 floor (zone), 1 roof (outdoors), 24 wall (outdoors), 24 wall (zone). The vertex coordinates are in `Appendix_IDF.txt`.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per conditioned zone (the 15 zones of the xlsx that have an HVAC system; not the plenums, except the infiltration). All fields not named here are empty (EnergyPlus default).

* **`People`**: name `<zone>_People`; schedule `BLDG_OCC_SCH_wo_SB`; method `Area/Person`; floor area per person = xlsx raw_data column M (18.58 m2/person); activity level schedule `ACTIVITY_SCH`.
* **`Lights`**: name `<zone>_Lights`; schedule `ltg_sch_office`; method `Watts/Area`; watts per floor area = xlsx raw_data column L (11.0267 W/m2).
* **`ElectricEquipment`**: name `<zone>_Equipment`; schedule `BLDG_EQUIP_SCH`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process, including the elevators: 25.0366 W/m2 in `Core_bottom`, about 8.07 W/m2 elsewhere).
* **`ZoneInfiltration:DesignFlowRate`**: name `<zone>_Infiltration` for every zone with a value in raw_data column R (the perimeter zones and the plenums: 0.00103 m3/s-m2); schedule `INFIL_SCH_PNNL`; method `Flow/ExteriorWallArea`. For `Perimeter_bot_ZN_1` also `<zone>_Door_Infiltration`: method `Flow/Zone`, no schedule, design flow rate = raw_data column T (1.043 m3/s).
* **`HVACTemplate:Thermostat`**: one object `OfficeThermostat`; heating schedule `HTGSETP_SCH_PACU_VAV_bot`, cooling schedule `CLGSETP_SCH_NO_SETBACK` (xlsx Schedule Summary).
* **`HVACTemplate:System:PackagedVAV`**: three objects `PACU_VAV_bot`, `PACU_VAV_mid`, `PACU_VAV_top` (xlsx raw_data column I); availability schedule `HVACOperationSchd`; heating coil type `Gas` (xlsx HVAC system type 5.1, packaged VAV with gas central heating and electric reheat).
* **`HVACTemplate:Zone:VAV`**: zone name; template system `PACU_VAV_<floor>` of the floor of the zone; thermostat `OfficeThermostat`; outdoor air method `Flow/Area` with the outdoor air per zone floor area of the xlsx sheet Zone and HVAC System Summary (0.000508 m3/s-m2); reheat coil type `Electric`.

The wall and roof constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.084 and roof U = 0.063 Btu/h-ft2-F (Tables 20 and 19), written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25).
