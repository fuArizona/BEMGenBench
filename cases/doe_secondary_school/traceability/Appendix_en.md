# Appendix (natural language): DOE Secondary School, Short IDF, Buffalo

Target IDF: `DOE/Secondary_School/Short/DOE_SchoolSecondary_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas, the number of floors and the floor height; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A two-storey E-shaped secondary school, **141 m x 104 m** (463 ft x 341 ft) in the bounding box of the plan (the footprint is the prototype's; xlsx Building Summary: 2 floors; PDF Table 13: 210,887 ft2, E-shape, floor-to-floor height 13 ft), 19592 m2 of floor in 46 zones, all with multiplier 1. The coordinates of the prototype are whole metres and the zones are 8 m high (the PDF gives 13 ft = 3.96 m). Building coordinates: x to the east, y to the north, z up (`GlobalGeometryRules`: upper-left corner, counterclockwise, relative); the origin of the building is the south-west corner of the plan (the west end of pod 1), so x and y are positive everywhere; floor 2 zones have the Z origin 4. Every zone has an origin (`Zone` fields X, Y, Z Origin, in building coordinates; a blank field is 0) and the vertices of its surfaces are relative to that origin, so a zone is described by its origin and the sizes of its rectangle; the zone table below gives the extents in building coordinates.

The three arms of the E are the classroom pods, which run in x from the western end to the main corridor (a classroom row on each side of the pod corridor, on both floors; the floor 2 zones repeat the floor 1 layout); the spine (main corridor, lobby, bathrooms) and the rooms on the east side are the common spaces:

* **Pod 1** (10 zones on two floors, 2944 m2): on each floor a corridor `Corridor_Pod_1_ZN_1_FLR_1` / `Corridor_Pod_1_ZN_1_FLR_2` (64 m x 5 m, y = 9 to 14 m) with a row of classrooms on each side: `Corner_Class_1_Pod_1_ZN_1_FLR_1`, `Mult_Class_1_Pod_1_ZN_1_FLR_1`, `Corner_Class_2_Pod_1_ZN_1_FLR_1`, `Mult_Class_2_Pod_1_ZN_1_FLR_1`
* **Pod 2** (10 zones on two floors, 2944 m2): on each floor a corridor `Corridor_Pod_2_ZN_1_FLR_1` / `Corridor_Pod_2_ZN_1_FLR_2` (64 m x 5 m, y = 49 to 54 m) with a row of classrooms on each side: `Corner_Class_1_Pod_2_ZN_1_FLR_1`, `Mult_Class_1_Pod_2_ZN_1_FLR_1`, `Corner_Class_2_Pod_2_ZN_1_FLR_1`, `Mult_Class_2_Pod_2_ZN_1_FLR_1`
* **Pod 3** (10 zones on two floors, 2944 m2): on each floor a corridor `Corridor_Pod_3_ZN_1_FLR_1` / `Corridor_Pod_3_ZN_1_FLR_2` (64 m x 5 m, y = 90 to 95 m) with a row of classrooms on each side: `Corner_Class_1_Pod_3_ZN_1_FLR_1`, `Mult_Class_1_Pod_3_ZN_1_FLR_1`, `Corner_Class_2_Pod_3_ZN_1_FLR_1`, `Mult_Class_2_Pod_3_ZN_1_FLR_1`
* **Spine and common rooms** (16 zones): `Main_Corridor_ZN_1_FLR_1`, `Main_Corridor_ZN_1_FLR_2`, `Lobby_ZN_1_FLR_1`, `Lobby_ZN_1_FLR_2`, `Bathrooms_ZN_1_FLR_1`, `Bathrooms_ZN_1_FLR_2`, `Offices_ZN_1_FLR_1`, `Offices_ZN_1_FLR_2`, `Gym_ZN_1_FLR_1`, `Aux_Gym_ZN_1_FLR_1`, `Auditorium_ZN_1_FLR_1`, `Kitchen_ZN_1_FLR_1`, `LIBRARY_MEDIA_CENTER_ZN_1_FLR_2`, `Cafeteria_ZN_1_FLR_1`, `Mech_ZN_1_FLR_1`, `Mech_ZN_1_FLR_2`.
* **Surfaces**: 64 exterior wall surfaces (`ExteriorWall`) and 24 roof surfaces (`Roof`, one per zone) face outdoors; the 166 interior walls have the boundary condition `Surface` and the construction `GenericSurface` (a pair of reversed polygons). The 25 ground-floor floors have each their own slab-on-grade construction (F-factor method, `Construction:FfactorGroundFloor`); the floors and ceilings between the two storeys are interior surfaces with `GenericSurface`: 23 of them are in contact with the ground, 2 has the boundary condition `Adiabatic`.
* **Windows** (construction `Window`): 88 fenestration surfaces with together 2088.80 m2 (the xlsx window glass area is 2,088.8 m2). There are no swinging doors and no skylights in this IDF (the 32 doors and the 90 skylights of the roof of the prototype are not in the documents).

| Zone | Origin x, y, z m | x range m | y range m | z range m | Floor polygon area m2 | HVAC template |
|---|---|---|---|---|---|---|
| Corner_Class_1_Pod_1_ZN_1_FLR_1 | 0, 0, 0 | 0 to 11 | 0 to 9 | 0 to 4 | 99.0 | HVAC |
| Corner_Class_1_Pod_1_ZN_1_FLR_2 | 0, 0, 4 | 0 to 11 | 0 to 9 | 4 to 8 | 99.0 | HVAC |
| Mult_Class_1_Pod_1_ZN_1_FLR_1 | 11, 0, 0 | 11 to 64 | 0 to 9 | 0 to 4 | 477.0 | HVAC |
| Mult_Class_1_Pod_1_ZN_1_FLR_2 | 11, 0, 4 | 11 to 64 | 0 to 9 | 4 to 8 | 477.0 | HVAC |
| Corridor_Pod_1_ZN_1_FLR_1 | 0, 9, 0 | 0 to 64 | 9 to 14 | 0 to 4 | 320.0 | HVAC |
| Corridor_Pod_1_ZN_1_FLR_2 | 0, 9, 4 | 0 to 64 | 9 to 14 | 4 to 8 | 320.0 | HVAC |
| Corner_Class_2_Pod_1_ZN_1_FLR_1 | 0, 14, 0 | 0 to 11 | 14 to 23 | 0 to 4 | 99.0 | HVAC |
| Corner_Class_2_Pod_1_ZN_1_FLR_2 | 0, 14, 4 | 0 to 11 | 14 to 23 | 4 to 8 | 99.0 | HVAC |
| Mult_Class_2_Pod_1_ZN_1_FLR_1 | 11, 14, 0 | 11 to 64 | 14 to 23 | 0 to 4 | 477.0 | HVAC |
| Mult_Class_2_Pod_1_ZN_1_FLR_2 | 11, 14, 4 | 11 to 64 | 14 to 23 | 4 to 8 | 477.0 | HVAC |
| Corner_Class_1_Pod_2_ZN_1_FLR_1 | 0, 40, 0 | 0 to 11 | 40 to 49 | 0 to 4 | 99.0 | HVAC |
| Corner_Class_1_Pod_2_ZN_1_FLR_2 | 0, 40, 4 | 0 to 11 | 40 to 49 | 4 to 8 | 99.0 | HVAC |
| Mult_Class_1_Pod_2_ZN_1_FLR_1 | 11, 40, 0 | 11 to 64 | 40 to 49 | 0 to 4 | 477.0 | HVAC |
| Mult_Class_1_Pod_2_ZN_1_FLR_2 | 11, 40, 4 | 11 to 64 | 40 to 49 | 4 to 8 | 477.0 | HVAC |
| Corridor_Pod_2_ZN_1_FLR_1 | 0, 49, 0 | 0 to 64 | 49 to 54 | 0 to 4 | 320.0 | HVAC |
| Corridor_Pod_2_ZN_1_FLR_2 | 0, 49, 4 | 0 to 64 | 49 to 54 | 4 to 8 | 320.0 | HVAC |
| Corner_Class_2_Pod_2_ZN_1_FLR_1 | 0, 54, 0 | 0 to 11 | 54 to 63 | 0 to 4 | 99.0 | HVAC |
| Corner_Class_2_Pod_2_ZN_1_FLR_2 | 0, 54, 4 | 0 to 11 | 54 to 63 | 4 to 8 | 99.0 | HVAC |
| Mult_Class_2_Pod_2_ZN_1_FLR_1 | 11, 54, 0 | 11 to 64 | 54 to 63 | 0 to 4 | 477.0 | HVAC |
| Mult_Class_2_Pod_2_ZN_1_FLR_2 | 11, 54, 4 | 11 to 64 | 54 to 63 | 4 to 8 | 477.0 | HVAC |
| Corner_Class_1_Pod_3_ZN_1_FLR_1 | 0, 81, 0 | 0 to 11 | 81 to 90 | 0 to 4 | 99.0 | HVAC |
| Corner_Class_1_Pod_3_ZN_1_FLR_2 | 0, 81, 4 | 0 to 11 | 81 to 90 | 4 to 8 | 99.0 | HVAC |
| Mult_Class_1_Pod_3_ZN_1_FLR_1 | 11, 81, 0 | 11 to 64 | 81 to 90 | 0 to 4 | 477.0 | HVAC |
| Mult_Class_1_Pod_3_ZN_1_FLR_2 | 11, 81, 4 | 11 to 64 | 81 to 90 | 4 to 8 | 477.0 | HVAC |
| Corridor_Pod_3_ZN_1_FLR_1 | 0, 90, 0 | 0 to 64 | 90 to 95 | 0 to 4 | 320.0 | HVAC |
| Corridor_Pod_3_ZN_1_FLR_2 | 0, 90, 4 | 0 to 64 | 90 to 95 | 4 to 8 | 320.0 | HVAC |
| Corner_Class_2_Pod_3_ZN_1_FLR_1 | 0, 95, 0 | 0 to 11 | 95 to 104 | 0 to 4 | 99.0 | HVAC |
| Corner_Class_2_Pod_3_ZN_1_FLR_2 | 0, 95, 4 | 0 to 11 | 95 to 104 | 4 to 8 | 99.0 | HVAC |
| Mult_Class_2_Pod_3_ZN_1_FLR_1 | 11, 95, 0 | 11 to 64 | 95 to 104 | 0 to 4 | 477.0 | HVAC |
| Mult_Class_2_Pod_3_ZN_1_FLR_2 | 11, 95, 4 | 11 to 64 | 95 to 104 | 4 to 8 | 477.0 | HVAC |
| Main_Corridor_ZN_1_FLR_1 | 64, 14, 0 | 64 to 79 | 14 to 90 | 0 to 4 | 1140.0 | HVAC |
| Main_Corridor_ZN_1_FLR_2 | 64, 14, 4 | 64 to 79 | 14 to 90 | 4 to 8 | 1140.0 | HVAC |
| Lobby_ZN_1_FLR_1 | 64, 0, 0 | 64 to 79 | 0 to 14 | 0 to 4 | 210.0 | HVAC |
| Lobby_ZN_1_FLR_2 | 64, 0, 4 | 64 to 79 | 0 to 14 | 4 to 8 | 210.0 | HVAC |
| Bathrooms_ZN_1_FLR_1 | 64, 90, 0 | 64 to 79 | 90 to 104 | 0 to 4 | 210.0 | HVAC |
| Bathrooms_ZN_1_FLR_2 | 64, 90, 4 | 64 to 79 | 90 to 104 | 4 to 8 | 210.0 | HVAC |
| Offices_ZN_1_FLR_1 | 79, 0, 0 | 79 to 117 | 0 to 14 | 0 to 4 | 532.0 | HVAC |
| Offices_ZN_1_FLR_2 | 79, 0, 4 | 79 to 117 | 0 to 14 | 4 to 8 | 532.0 | HVAC |
| Gym_ZN_1_FLR_1 | 79, 14, 0 | 79 to 117 | 14 to 66 | 0 to 8 | 1976.0 | HVAC |
| Aux_Gym_ZN_1_FLR_1 | 117, 14, 0 | 117 to 141 | 14 to 66 | 0 to 8 | 1248.0 | HVAC |
| Auditorium_ZN_1_FLR_1 | 79, 75, 0 | 79 to 117 | 75 to 101 | 0 to 8 | 988.0 | HVAC |
| Kitchen_ZN_1_FLR_1 | 117, 66, 0 | 117 to 141 | 66 to 75 | 0 to 4 | 216.0 | HVAC |
| LIBRARY_MEDIA_CENTER_ZN_1_FLR_2 | 117, 66, 4 | 117 to 141 | 66 to 101 | 4 to 8 | 840.0 | HVAC |
| Cafeteria_ZN_1_FLR_1 | 117, 75, 0 | 117 to 141 | 75 to 101 | 0 to 4 | 624.0 | HVAC |
| Mech_ZN_1_FLR_1 | 79, 66, 0 | 79 to 117 | 66 to 75 | 0 to 4 | 342.0 | HVAC |
| Mech_ZN_1_FLR_2 | 79, 66, 4 | 79 to 117 | 66 to 75 | 4 to 8 | 342.0 | HVAC |

The IDF has 323 building surfaces: 22 ceiling (surface), 2 floor (adiabatic), 23 floor (groundfcfactormethod), 22 floor (surface), 24 roof (outdoors), 64 wall (outdoors), 166 wall (surface). The vertex coordinates are in `Appendix_IDF.txt`. The floor polygon area is the sum of the surfaces of type Floor of the zone.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per zone that has a value in the xlsx raw_data sheet (the zone names are those of the IDF; the xlsx writes them in capital letters). All fields not named here are empty (EnergyPlus default). Every schedule is a `Schedule:Compact` written from the xlsx sheet Schedule Summary rows (Mon - Fri, Sat, Sun). The schedules of Occupants, Lighting and Electric Equipment have one set of rows for the study periods and one for the summer holiday in the xlsx: they are written with three `Through` blocks (until 6/30 study periods, until 9/1 summer holiday, until 12/31 study periods; the dates are those of NREL PDF Table B-8). The occupancy schedule of a zone is the one of its space type in the xlsx: `BLDG_OCC_SCH_Cafeteria` for the cafeteria, `BLDG_OCC_SCH_Auditorium` for the auditorium, `BLDG_OCC_SCH_Extend` for the two classrooms `Mult_Class_1_Pod_3_ZN_1_FLR_2` and `Mult_Class_2_Pod_3_ZN_1_FLR_2` (their own xlsx rows), `BLDG_OCC_SCH_Gym` for the gym and the auxiliary gym, `BLDG_OCC_SCH_Offices` for the offices and `BLDG_OCC_SCH` (xlsx space type Others) for all other zones.

* **`People`**: name `<zone>_People`; method `Area/Person`; floor area per person = xlsx raw_data column M; activity level schedule `ACTIVITY_SCH`. Schedules:

| Schedule | Zones |
|---|---|
| BLDG_OCC_SCH | Corner_Class_1_Pod_1_ZN_1_FLR_1, Corner_Class_1_Pod_1_ZN_1_FLR_2, Mult_Class_1_Pod_1_ZN_1_FLR_1, ... (38 zones) |
| BLDG_OCC_SCH_Extend | Mult_Class_1_Pod_3_ZN_1_FLR_2, Mult_Class_2_Pod_3_ZN_1_FLR_2 |
| BLDG_OCC_SCH_Offices | Offices_ZN_1_FLR_1, Offices_ZN_1_FLR_2 |
| BLDG_OCC_SCH_Gym | Gym_ZN_1_FLR_1, Aux_Gym_ZN_1_FLR_1 |
| BLDG_OCC_SCH_Auditorium | Auditorium_ZN_1_FLR_1 |
| BLDG_OCC_SCH_Cafeteria | Cafeteria_ZN_1_FLR_1 |

* **`Lights`**: name `<zone>_Lights`; method `Watts/Area`; watts per floor area = xlsx raw_data column L; schedule `BLDG_LIGHT_SCH` (xlsx row Lighting, All).

* **`ElectricEquipment`**: name `<zone>_Equipment`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process; for the kitchen it includes the gas power of column O and for `Mech_ZN_1_FLR_1` the elevators, written as given); schedule `KITCHEN_ELEC_EQUIP_SCH` for the kitchen and the cafeteria (xlsx row Electric Equipment, Kitchen, Cafeteria) and `BLDG_EQUIP_SCH` for the other zones (xlsx row Electric Equipment, Others).

* **`GasEquipment`**: `Kitchen_ZN_1_FLR_1_Gas_Equipment`; method `EquipmentLevel`; design level = xlsx raw_data column O (gas power, W); schedule `KITCHEN_GAS_EQUIP_SCH` (xlsx row Gas Equipment, Kitchen).

* **`ZoneInfiltration:DesignFlowRate`**: name `<zone>_Infiltration` for every zone that has a value in xlsx raw_data column R (flow per exterior surface area); method `Flow/ExteriorWallArea`; schedule `INFIL_SCH_PNNL` (xlsx row Infiltration, All). The lobby has in addition `<zone>_Door_Infiltration` (method `Flow/Zone`, design flow rate = xlsx raw_data column T, infiltration through the entrances, no schedule); the column S (zone flow) is 0 in the xlsx.

* **`HVACTemplate:Thermostat`**: `OthersThermostat` (heating schedule `HTGSETP_SCH_VAV_OTHER`, cooling schedule `CLGSETP_SCH_NO_SETBACK`); `BathroomsMechanicalRoomsThermostat` (heating schedule `HTGSETP_SCH_Setback`, cooling schedule `CLGSETP_SCH_Setup`); `GymAuditoriumKitchenCafeteriaThermostat` (heating schedule `HTGSETP_SCH_NO_OPTIMUM`, cooling schedule `CLGSETP_SCH_NO_SETBACK`) (xlsx Schedule Summary, Heating Set Point and Cooling Set Point). The bathrooms and mechanical rooms use `BathroomsMechanicalRoomsThermostat`, the gym, the auxiliary gym, the auditorium, the kitchen and the cafeteria `GymAuditoriumKitchenCafeteriaThermostat` and all other zones `OthersThermostat`.

* **`HVACTemplate:System:VAV`** (4 objects, named by xlsx raw_data column I: `VAV_POD_1`, `VAV_POD_2`, `VAV_POD_3`, `VAV_OTHER`): availability schedule `HVACOperationSchd`; cooling coil type `ChilledWater`; heating coil type `HotWater`; economizer type `NoEconomizer`; all other fields are EnergyPlus defaults.

* **`HVACTemplate:Zone:VAV`** (41 objects, the zones of xlsx HVAC system type 7): zone name; template system = the system named in raw_data column I; thermostat as above; outdoor air method `Flow/Area` with the outdoor air per floor area that follows from the xlsx sheet Zone and HVAC System Summary (Total OSA Ventilation: column Q cfm/person x column N people per 1000 ft2 / 1000 + column R cfm/ft2 + column S cfm/zone / area, times 0.00508 m3/s-m2 per cfm/ft2); reheat coil type `HotWater`.

* **`HVACTemplate:System:Unitary`** (5 objects, named by xlsx raw_data column I: `PSZ-AC_1:5`, `PSZ-AC_2:6`, `PSZ-AC_3:7`, `PSZ-AC_4:8`, `PSZ-AC_5:9`): availability schedule `HVACOperationSchd`; control zone = the one zone of the system; heating coil type `Gas`; economizer type `NoEconomizer` (written because ExpandObjects writes the value `None` otherwise); all other fields are EnergyPlus defaults.

* **`HVACTemplate:Zone:Unitary`** (5 objects, the zones of xlsx HVAC system type 3: `Gym_ZN_1_FLR_1`, `Aux_Gym_ZN_1_FLR_1`, `Auditorium_ZN_1_FLR_1`, `Kitchen_ZN_1_FLR_1`, `Cafeteria_ZN_1_FLR_1`): template system = the system named in raw_data column I; thermostat as above; outdoor air method `Flow/Zone` with the outdoor air flow per zone = xlsx raw_data column P (total outdoor air, m3/s).

The plant (one chilled water loop with a chiller and a tower, one hot water loop with a boiler) is in `Appendix_IDF.txt`: the xlsx names the system type only; the chiller type and COP are required by EnergyPlus and are not in the documents. The wall and roof constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.084 Btu/h-ft2-F (Table 20, steel frame wall; Table 18) and roof U = 0.063 (Table 19, insulation entirely above deck; Table 17), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25); the slab F-factor 1.26363 W/m-K is the 90.1-2004 value of an uninsulated slab (Table 22: no insulation required).
