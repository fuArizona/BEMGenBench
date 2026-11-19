# Appendix (natural language): DOE Full Service Restaurant, Short IDF, Buffalo

Target IDF: `DOE/Full_Service_Restaurant/Short/DOE_RestaurantSitDown_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A one-storey restaurant building, a **square of 22.61 m x 22.61 m** (74.2 ft x 74.2 ft) in plan, 511 m2 of conditioned floor (NREL PDF Table 13: 5,500 ft2, aspect ratio 1.0, one floor, floor-to-floor height 10 ft), with a hip-roof attic above it. Local coordinates start at the south-west corner of the building: x to the east, y to the north, z up (`GlobalGeometryRules`: upper-left corner, counterclockwise, relative). The origins of the two conditioned zones are 0; the attic zone origin is raised by the storey height (3.05 m), so its vertices are relative to the ceiling level.

* **Two conditioned zones**, each 22.61 m x 11.30 m (74.2 ft x 37.1 ft) and 3.05 m (10 ft) high: `Dining` is the south half and `Kitchen` the north half. They share an interior wall along y = 11.30 m (two surfaces, one in each zone).
* **The attic** (`attic`, not conditioned) lies on top of the two zones, from z = 3.05 m to 6.82 m. It has four roof planes (hip roof: two triangular planes at the east and west ends and two trapezoids on the south and north sides) with a pitch of about 45 degrees. The ridge runs east-west at y = 11.30 m from x = 3.77 m (W / 6) to x = 18.84 m (W - W / 6), and its height above the ceiling is 3.77 m (W / 6). There is no soffit overhang. The attic floor is two interior surfaces, one above each zone. It is a row of the xlsx (area, infiltration, no HVAC); its roof planes are not in the documents.
* **Surfaces**: the ceiling of each zone and the attic floor above it are a pair of interior surfaces (boundary condition `Surface`, construction `RoofCeiling`); the shared wall between the zones is a pair of interior walls (`GenericSurface`); the exterior walls (`ExteriorWall`) are the south, east and west walls of the dining zone and the north, east and west walls of the kitchen zone; the roof planes (`GenericSurface`) face outdoors. The floors of the two zones are slab on grade (F-factor method, `Construction:FfactorGroundFloor`).
* **Windows** (construction `Window`, 3 windows, all in the dining zone; no swinging door): east, south and west walls of the dining zone. The windows are 19.30 m2 at most (south) and together 47.17 m2, the xlsx window glass area (17 % of the exterior wall area, PDF Table 13). The number and the walls of the windows, the edge margins (0.6029 m at the east and west walls, 0.754 m at the south wall) and the top height 1.9817 m are values of the prototype, not in the documents; the window height 0.9146 m is back-calculated from the xlsx window area: the three windows have the same height h (a prototype property, not in the documents), so 47.17 m2 = h x (15.2368 m + 21.1007 m + 15.2368 m) (east, south and west window widths) and h = 0.9146 m. The kitchen has no window.

| Zone | Plan x by y m | z range m | Floor area m2 |
|---|---|---|---|
| Dining | 22.61 x 16.44 | 0.00 to 3.05 | 371.7 |
| Kitchen | 22.61 x 6.17 | 0.00 to 3.05 | 139.4 |
| attic | 22.61 x 22.61 | 3.05 to 6.82 | attic |

The IDF has 18 building surfaces: 2 ceiling (surface), 2 floor (groundfcfactormethod), 2 floor (surface), 4 roof (outdoors), 6 wall (outdoors), 2 wall (surface). The vertex coordinates are in `Appendix_IDF.txt`.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per conditioned zone (`Dining`, `Kitchen`; not the attic, except the infiltration). All fields not named here are empty (EnergyPlus default).

* **`People`**: name `<zone>_People`; schedule `BLDG_OCC_SCH`; method `Area/Person`; floor area per person = xlsx raw_data column M (Dining 1.33 m2/person, Kitchen 18.52 m2/person); activity level schedule `ACTIVITY_SCH`.
* **`Lights`**: name `<zone>_Lights`; schedule `ltg_sch_dining` (dining) or `ltg_sch_kitchen` (kitchen), both with the hourly values of the xlsx row Lighting; method `Watts/Area`; watts per floor area = xlsx raw_data column L (Dining 20.6319 W/m2, Kitchen 11.3949 W/m2).
* **`ElectricEquipment`**: name `<zone>_Equipment`; schedule `BLDG_EQUIP_SCH`; method `Watts/Area`; watts per floor area = xlsx raw_data column N, plug and process (Dining 64.9275 W/m2, Kitchen 1063.08 W/m2).
* **`GasEquipment`**: one object `Kitchen_Gas_Equipment` for the kitchen; schedule `Rest_GAS_EQUIP_SCH` (xlsx row Gas Equipment, Kitchen); method `EquipmentLevel`; design level = xlsx raw_data column O, gas power (90512.5 W).
* **`ZoneInfiltration:DesignFlowRate`**: name `<zone>_Infiltration` for both conditioned zones (raw_data column R, 0.00102523 m3/s-m2); schedule `INFIL_SCH_PNNL`; method `Flow/ExteriorWallArea`. For `Dining` also `Dining_Door_Infiltration`: method `Flow/Zone`, no schedule, design flow rate = raw_data column T (0.614475 m3/s). For `attic` `attic_Zone_Infiltration`: method `Flow/Zone`, no schedule, design flow rate = raw_data column S (0.2378 m3/s).
* **`HVACTemplate:Thermostat`**: `DiningThermostat` (heating `HTGSETP_SCH_NO_OPTIMUM`, cooling `CLGSETP_SCH_NO_SETBACK`) and `KitchenThermostat` (heating `HTGSETP_KITCHEN_SCH_NO_OPTIMUM`, cooling `CLGSETP_KITCHEN_SCH_NO_SETBACK`), schedules of the xlsx Schedule Summary rows Heating Set Point and Cooling Set Point of the zone.
* **`HVACTemplate:System:Unitary`**: two objects, one per conditioned zone, named by xlsx raw_data column I (`PSZ-AC_1:1` for `Dining`, `PSZ-AC_2:2` for `Kitchen`); availability schedule `HVACOperationSchd`; control zone = the zone; heating coil type `Gas` (xlsx HVAC system type 3, PSZ-AC); economizer type `NoEconomizer`.
* **`HVACTemplate:Zone:Unitary`**: zone name; template system = the unit of the zone; thermostat `<zone>Thermostat`; outdoor air method `Flow/Zone` with the xlsx raw_data column P (Dining 2.6439 m3/s, Kitchen 0.1242 m3/s).

The schedules (`BLDG_OCC_SCH`, `ltg_sch_dining`, `ltg_sch_kitchen`, `BLDG_EQUIP_SCH`, `Rest_GAS_EQUIP_SCH`, `INFIL_SCH_PNNL`, `HVACOperationSchd` and the four set point schedules) are `Schedule:Compact` objects written from the hourly values of the xlsx sheet Schedule Summary: clause `For: Weekdays SummerDesignDay WinterDesignDay` = row Mon - Fri, `For: Saturday` = row Sat, `For: AllOtherDays` = row Sun; each `Until: h:00,value` joins the hours with equal values.

The wall and the ceiling below the attic come from the NREL PDF (Chicago 5A, new construction): wall U = 0.084 Btu/h-ft2-F (Table 20, steel frame; Table 18) and ceiling U = 0.034 (Table 19, roof, attic and other; Table 17), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25). The exterior wall is the steel frame wall of PDF Table 18 with U = 0.084 Btu/h-ft2-F (Table 20), written as one layer in the same way; the interior wall and the attic roof planes are the generic layer of 0.2 m2-K/W (not in the documents).
