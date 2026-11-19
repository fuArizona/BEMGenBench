# Appendix (natural language): DOE Large Hotel, Short IDF, Buffalo

Target IDF: `DOE/Large_Hotel/Short/DOE_HotelLarge_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas, the footprint and the floor heights; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A hotel with a basement, **86.56 m x 22.86 m** (284 ft x 75 ft) in plan (xlsx Building Summary: 284 ft x 75 ft, 6 floors above ground plus a basement; PDF Table 13: 122,120 ft2, floor-to-floor height 13 ft on the ground floor and 10 ft above), 11345 m2 of floor in 22 zones (with the zone multipliers). Local coordinates start at the south-west corner of the building: x to the east (the long side), y to the north, z up; all zone origins are 0, so the vertices are building coordinates (`GlobalGeometryRules`: upper-left corner, counterclockwise, relative). Three floor levels are modelled; the guest-room and corridor zones of the middle level stand for several floors by the zone multiplier (xlsx raw_data column G):

* **z = -2.44 to 0.00 m** (8 ft): `Basement`.
* **z = 0.00 to 3.96 m** (13 ft): `Retail_1_Flr_1`, `Retail_2_Flr_1`, `Mech_Flr_1`, `Storage_Flr_1`, `Laundry_Flr_1`, `Cafe_Flr_1`, `Lobby_Flr_1`.
* **z = 7.01 to 10.06 m** (10 ft): `Room_1_Flr_3` (x4), `Room_2_Flr_3` (x4), `Room_3_Mult19_Flr_3` (x76), `Room_4_Mult19_Flr_3` (x76), `Room_5_Flr_3` (x4), `Room_6_Flr_3` (x4), `Corridor_Flr_3` (x4).
* **z = 16.15 to 19.20 m** (10 ft): `Room_1_Flr_6`, `Room_2_Flr_6`, `Room_3_Mult9_Flr_6` (x9), `Banquet_Flr_6`, `Dining_Flr_6`, `Kitchen_Flr_6`, `Corridor_Flr_6`.

* **Basement** (`Basement`, 86.56 m x 22.86 m, 1979 m2): the whole footprint, from z = -2.44 m (8 ft) to 0.
* **Ground floor** (z = 0 to 3.96 m): the lobby `Lobby_Flr_1` fills the building from the west wall to x = 81.99 m; the cafe (south-east), mechanical room, storage and laundry (north-east) and two retail zones (south-west) are rectangles of the footprint.
* **Middle and top floors**: guest rooms along the west and east ends (`Room_1` ... `Room_6`, each 4.57 m = 15 ft wide), the corridor `Corridor_Flr_3` / `Corridor_Flr_6` between them over the full length (x from 4.57 to 81.99 m) and, on the top floor, the banquet hall, the dining room and the kitchen along the north side. `Room_3` and `Room_4` of the middle floor have multiplier 76 (xlsx: 19 rooms of the type on each of 4 floors) and the rooms of the top floor 9.
* **Surfaces**: the exterior walls (`ExteriorWall`) and the roofs (`Roof`: the top-floor zones and the ground-floor zones `Retail_1_Flr_1`, `Cafe_Flr_1` and `Lobby_Flr_1`) face outdoors; the walls below grade of the basement use the C-factor method (`Construction:CfactorUndergroundWall`); the floor of the basement is adiabatic; between the zones the walls, floors and ceilings are interior surfaces (boundary condition `Surface`, construction `GenericSurface`), each a pair of reversed polygons.
* **Windows** (construction `Window`): 30 windows with together 401.94 m2 on the exterior walls (the xlsx window glass area is 1,213.79 m2 with the multipliers: the polygons of the zones with a multiplier count once here). There are no swinging doors in this IDF.

| Zone | Multiplier | x range m | y range m | z range m | Floor polygon area m2 | HVAC template |
|---|---|---|---|---|---|---|
| Basement | 1 | 0.00 to 86.56 | 0.00 to 22.86 | -2.44 to 0.00 | 1978.8 | HVAC |
| Retail_1_Flr_1 | 1 | 0.00 to 11.58 | 0.00 to 5.79 | 0.00 to 3.96 | 67.1 | HVAC |
| Retail_2_Flr_1 | 1 | 0.00 to 11.58 | 5.79 to 12.50 | 0.00 to 3.96 | 77.7 | HVAC |
| Mech_Flr_1 | 1 | 53.95 to 69.80 | 12.50 to 22.86 | 0.00 to 3.96 | 164.2 | HVAC |
| Storage_Flr_1 | 1 | 69.80 to 78.94 | 12.50 to 22.86 | 0.00 to 3.96 | 94.8 | HVAC |
| Laundry_Flr_1 | 1 | 81.99 to 86.56 | 5.79 to 22.86 | 0.00 to 3.96 | 78.0 | HVAC |
| Cafe_Flr_1 | 1 | 53.95 to 86.56 | 0.00 to 5.79 | 0.00 to 3.96 | 188.9 | HVAC |
| Lobby_Flr_1 | 1 | 0.00 to 81.99 | 0.00 to 22.86 | 0.00 to 3.96 | 1308.2 | HVAC |
| Room_1_Flr_3 | 4 | 0.00 to 4.57 | 5.79 to 14.33 | 7.01 to 10.06 | 39.0 | HVAC |
| Room_2_Flr_3 | 4 | 0.00 to 4.57 | 14.33 to 22.86 | 7.01 to 10.06 | 39.0 | HVAC |
| Room_3_Mult19_Flr_3 | 76 | 6.71 to 10.36 | 5.79 to 12.50 | 7.01 to 10.06 | 24.5 | HVAC |
| Room_4_Mult19_Flr_3 | 76 | 10.36 to 14.02 | 16.15 to 22.86 | 7.01 to 10.06 | 24.5 | HVAC |
| Room_5_Flr_3 | 4 | 81.99 to 86.56 | 5.79 to 14.33 | 7.01 to 10.06 | 39.0 | HVAC |
| Room_6_Flr_3 | 4 | 81.99 to 86.56 | 14.33 to 22.86 | 7.01 to 10.06 | 39.0 | HVAC |
| Corridor_Flr_3 | 4 | 4.57 to 81.99 | 5.79 to 22.86 | 7.01 to 10.06 | 389.4 | HVAC |
| Room_1_Flr_6 | 1 | 0.00 to 4.57 | 5.79 to 14.33 | 16.15 to 19.20 | 39.0 | HVAC |
| Room_2_Flr_6 | 1 | 0.00 to 4.57 | 14.33 to 22.86 | 16.15 to 19.20 | 39.0 | HVAC |
| Room_3_Mult9_Flr_6 | 9 | 4.57 to 11.28 | 5.79 to 9.45 | 16.15 to 19.20 | 24.5 | HVAC |
| Banquet_Flr_6 | 1 | 10.36 to 42.37 | 12.50 to 22.86 | 16.15 to 19.20 | 331.7 | HVAC |
| Dining_Flr_6 | 1 | 47.55 to 79.55 | 12.50 to 22.86 | 16.15 to 19.20 | 331.7 | HVAC |
| Kitchen_Flr_6 | 1 | 79.55 to 86.56 | 5.79 to 22.86 | 16.15 to 19.20 | 103.3 | HVAC |
| Corridor_Flr_6 | 1 | 4.57 to 81.99 | 5.79 to 22.86 | 16.15 to 19.20 | 412.1 | HVAC |

The IDF has 177 building surfaces: 22 ceiling (surface), 1 floor (adiabatic), 24 floor (surface), 11 roof (outdoors), 4 wall (groundfcfactormethod), 40 wall (outdoors), 75 wall (surface). The vertex coordinates are in `Appendix_IDF.txt`. The floor polygon area is the sum of the surfaces of type Floor of the zone.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per zone that has a value in the xlsx raw_data sheet (the zone names are those of the IDF; the xlsx writes them in capital letters). All fields not named here are empty (EnergyPlus default). The schedule of a zone is the one of its space type in the xlsx sheet Schedule Summary (Guest Rooms, Others, Kitchen / Dining / Banquet, Common Areas); where the xlsx gives no schedule for a load, `AlwaysOn` (the prototype schedule is constant 1) or `AlwaysOff` is written.

* **`People`**: name `<zone>_People`; method `Area/Person`; floor area per person = xlsx raw_data column M; activity level schedule `ACTIVITY_SCH`. Schedules:

| Schedule | Zones |
|---|---|
| BLDG_OCC_SCH | Basement, Retail_1_Flr_1, Retail_2_Flr_1, Mech_Flr_1, Storage_Flr_1, Laundry_Flr_1, Cafe_Flr_1, Lobby_Flr_1, Corridor_Flr_3, Banquet_Flr_6, Dining_Flr_6, Kitchen_Flr_6, Corridor_Flr_6 |
| GuestRoom_Occ_Sch | Room_1_Flr_3, Room_2_Flr_3, Room_3_Mult19_Flr_3, Room_4_Mult19_Flr_3, Room_5_Flr_3, Room_6_Flr_3, Room_1_Flr_6, Room_2_Flr_6, Room_3_Mult9_Flr_6 |

* **`Lights`**: name `<zone>_Lights`; method `Watts/Area`; watts per floor area = xlsx raw_data column L. Schedules:

| Schedule | Zones |
|---|---|
| ltg_sch_basement | Basement |
| ltg_sch_retail | Retail_1_Flr_1, Retail_2_Flr_1 |
| ltg_sch_mechanic | Mech_Flr_1 |
| ltg_sch_storage | Storage_Flr_1 |
| ltg_sch_laundry | Laundry_Flr_1 |
| ltg_sch_dining | Cafe_Flr_1, Banquet_Flr_6, Dining_Flr_6 |
| ltg_sch_lobby | Lobby_Flr_1 |
| ltg_sch_guestroom | Room_1_Flr_3, Room_2_Flr_3, Room_3_Mult19_Flr_3, Room_4_Mult19_Flr_3, Room_5_Flr_3, Room_6_Flr_3, Room_1_Flr_6, Room_2_Flr_6, Room_3_Mult9_Flr_6 |
| ltg_sch_corridor | Corridor_Flr_3, Corridor_Flr_6 |
| ltg_sch_kitchen | Kitchen_Flr_6 |

* **`ElectricEquipment`**: name `<zone>_Equipment`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process). Schedules:

| Schedule | Zones |
|---|---|
| BASEMENT_EQUIP_SCH | Basement |
| BLDG_EQUIP_SCH | Retail_1_Flr_1, Retail_2_Flr_1, Mech_Flr_1, Storage_Flr_1, Laundry_Flr_1, Cafe_Flr_1, Lobby_Flr_1 |
| GuestRoom_Eqp_Sch_Base | Room_1_Flr_3, Room_2_Flr_3, Room_3_Mult19_Flr_3, Room_4_Mult19_Flr_3, Room_5_Flr_3, Room_6_Flr_3, Room_1_Flr_6, Room_2_Flr_6, Room_3_Mult9_Flr_6 |
| Kitchen_Elec_Equip_SCH | Banquet_Flr_6, Dining_Flr_6, Kitchen_Flr_6 |

* **`GasEquipment`**: `Laundry_Flr_1_Gas_Equipment`, `Kitchen_Flr_6_Gas_Equipment`; method `EquipmentLevel`; design level = xlsx raw_data column O (gas power, W); schedule of the xlsx row Gas Equipment (Kitchen).

* **`ZoneInfiltration:DesignFlowRate`**: name `<zone>_Infiltration` for every zone that has a value in xlsx raw_data column R (flow per exterior surface area); method `Flow/ExteriorWallArea`; schedule `INFIL_QUARTER_ON_SCH`. The columns S and T (zone flow, entrances) are 0 in the xlsx.

* **`HVACTemplate:Thermostat`**: `GuestRoomThermostat` (heating schedule `Base_S_OccGuestRoom_HtgSP_Sch`, cooling schedule `Base_S_OccGuestRoom_ClgSP_Sch`); `CommonAreaThermostat` (heating schedule `HTGSETP_SCH`, cooling schedule `CLGSETP_SCH`) (xlsx Schedule Summary, Heating / Cooling Set Point, space types Guest Rooms and Common Areas; the xlsx gives the same value, 21.11 C, for the heating and the cooling set point of the guest rooms).

* **`HVACTemplate:System:VAV`** (1 object, named by xlsx raw_data column I: `VAV WITH REHEAT`): availability schedule `HVACOperationSchd`; cooling coil type `ChilledWater`; heating coil type `HotWater`; economizer type `NoEconomizer`.

* **`HVACTemplate:Zone:VAV`** (13 objects, the basement, the ground floor zones, the corridors, the banquet hall, the dining room and the kitchen): zone name; template system = the VAV system; thermostat `CommonAreaThermostat`; outdoor air method `Flow/Area` with the outdoor air per floor area that follows from the xlsx sheet Zone and HVAC System Summary (Total OSA Ventilation: cfm/person x people, cfm/ft2 or cfm/zone); reheat coil type `HotWater`.

* **`HVACTemplate:System:DedicatedOutdoorAir`** (1 object, `FLR_3_DOAS`) and **`HVACTemplate:Zone:FanCoil`** (9 objects, the guest rooms, xlsx type 16.1 four-pipe fan-coil with DOAS): the zone object has the zone name, thermostat `GuestRoomThermostat`, outdoor air method `Flow/Area` (as above), cooling coil `ChilledWater`, heating coil `HotWater` and the name of the DOAS system; the DOAS has cooling coil `ChilledWater` and heating coil `HotWater`.

The plant loops (one chilled water loop with a chiller and a tower, one hot water loop with a boiler) are in `Appendix_IDF.txt`: the xlsx names the system types only; the chiller type and COP are required by EnergyPlus and are not in the documents. The wall and roof constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.151 Btu/h-ft2-F (Table 21, mass wall; Table 18) and roof U = 0.063 (Table 19, insulation entirely above deck; Table 17), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25).
