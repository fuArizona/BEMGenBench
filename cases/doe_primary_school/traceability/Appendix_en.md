# Appendix (natural language): DOE Primary School, Short IDF, Buffalo

Target IDF: `DOE/Primary_School/Short/DOE_SchoolPrimary_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas, the number of floors and the floor height; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A one-storey E-shaped primary school, **104 m x 82 m** (341 ft x 269 ft) in the bounding box of the plan (the footprint is the prototype's; xlsx Building Summary: 1 floor; PDF Table 13: 73,960 ft2, E-shape, floor-to-floor height 13 ft), 6871 m2 of floor in 25 zones, all with multiplier 1. The coordinates of the prototype are whole metres and the zones are 4 m high (the PDF gives 13 ft = 3.96 m). Building coordinates: x to the east, y to the north, z up (`GlobalGeometryRules`: upper-left corner, counterclockwise, relative); the origin of the building is the south-west corner of the lobby, so the three pods at the west have negative x. Every zone has an origin (`Zone` fields X, Y, Z Origin, in building coordinates; a blank field is 0) and the vertices of its surfaces are relative to that origin, so a zone is described by its origin and the sizes of its rectangle; the zone table below gives the extents in building coordinates.

The three arms of the E are the classroom pods, which run from the main corridor to the west; the spine and the rooms on the east side are the common spaces:

* **Pod 1** (5 zones, 1344 m2): a corridor `Corridor_Pod_1_ZN_1_FLR_1` (64 m x 3 m, y = 9 to 12 m) with a row of classrooms on each side: `Corner_Class_1_Pod_1_ZN_1_FLR_1`, `Mult_Class_1_Pod_1_ZN_1_FLR_1`, `Corner_Class_2_Pod_1_ZN_1_FLR_1`, `Mult_Class_2_Pod_1_ZN_1_FLR_1`
* **Pod 2** (5 zones, 1344 m2): a corridor `Corridor_Pod_2_ZN_1_FLR_1` (64 m x 3 m, y = 39 to 42 m) with a row of classrooms on each side: `Corner_Class_1_Pod_2_ZN_1_FLR_1`, `Mult_Class_1_Pod_2_ZN_1_FLR_1`, `Corner_Class_2_Pod_2_ZN_1_FLR_1`, `Mult_Class_2_Pod_2_ZN_1_FLR_1`
* **Pod 3** (5 zones, 1182 m2): a corridor `Corridor_Pod_3_ZN_1_FLR_1` (64 m x 3 m, y = 70 to 73 m) with a row of classrooms on each side: `Corner_Class_1_Pod_3_ZN_1_FLR_1`, `Mult_Class_1_Pod_3_ZN_1_FLR_1`, `Corner_Class_2_Pod_3_ZN_1_FLR_1`, `Mult_Class_2_Pod_3_ZN_1_FLR_1`
* **Spine and common rooms** (10 zones): `Computer_Class_ZN_1_FLR_1`, `Main_Corridor_ZN_1_FLR_1`, `Lobby_ZN_1_FLR_1`, `Mech_ZN_1_FLR_1`, `Bath_ZN_1_FLR_1`, `Offices_ZN_1_FLR_1`, `Gym_ZN_1_FLR_1`, `Kitchen_ZN_1_FLR_1`, `Cafeteria_ZN_1_FLR_1`, `Library_Media_Center_ZN_1_FLR_1`.
* **Surfaces**: 33 exterior wall surfaces (`ExteriorWall`) and 25 roof surfaces (`Roof`, one per zone) face outdoors; the 88 interior walls have the boundary condition `Surface` and the construction `GenericSurface` (a pair of reversed polygons). The 25 floors have each their own slab-on-grade construction (F-factor method, `Construction:FfactorGroundFloor`): 24 of them are in contact with the ground, 1 (the mechanical room) has the boundary condition `Adiabatic`.
* **Windows** (construction `Window`): 58 fenestration surfaces with together 879.14 m2 (the xlsx window glass area is 879.14 m2). There are no swinging doors and no skylights in this IDF (the 25 doors and the 9 skylights of the Gym roof of the prototype are not in the documents).

| Zone | Origin x, y, z m | x range m | y range m | z range m | Floor polygon area m2 | HVAC template |
|---|---|---|---|---|---|---|
| Corner_Class_1_Pod_1_ZN_1_FLR_1 | -64, 0, 0 | -64 to -53 | 0 to 9 | 0 to 4 | 99.0 | HVAC |
| Mult_Class_1_Pod_1_ZN_1_FLR_1 | -53, 0, 0 | -53 to 0 | 0 to 9 | 0 to 4 | 477.0 | HVAC |
| Corridor_Pod_1_ZN_1_FLR_1 | -64, 9, 0 | -64 to 0 | 9 to 12 | 0 to 4 | 192.0 | HVAC |
| Corner_Class_2_Pod_1_ZN_1_FLR_1 | -64, 12, 0 | -64 to -53 | 12 to 21 | 0 to 4 | 99.0 | HVAC |
| Mult_Class_2_Pod_1_ZN_1_FLR_1 | -53, 12, 0 | -53 to 0 | 12 to 21 | 0 to 4 | 477.0 | HVAC |
| Corner_Class_1_Pod_2_ZN_1_FLR_1 | -64, 30, 0 | -64 to -53 | 30 to 39 | 0 to 4 | 99.0 | HVAC |
| Mult_Class_1_Pod_2_ZN_1_FLR_1 | -53, 30, 0 | -53 to 0 | 30 to 39 | 0 to 4 | 477.0 | HVAC |
| Corridor_Pod_2_ZN_1_FLR_1 | -64, 39, 0 | -64 to 0 | 39 to 42 | 0 to 4 | 192.0 | HVAC |
| Corner_Class_2_Pod_2_ZN_1_FLR_1 | -64, 42, 0 | -64 to -53 | 42 to 51 | 0 to 4 | 99.0 | HVAC |
| Mult_Class_2_Pod_2_ZN_1_FLR_1 | -53, 42, 0 | -53 to 0 | 42 to 51 | 0 to 4 | 477.0 | HVAC |
| Corner_Class_1_Pod_3_ZN_1_FLR_1 | -64, 61, 0 | -64 to -53 | 61 to 70 | 0 to 4 | 99.0 | HVAC |
| Mult_Class_1_Pod_3_ZN_1_FLR_1 | -53, 61, 0 | -53 to 0 | 61 to 70 | 0 to 4 | 477.0 | HVAC |
| Corridor_Pod_3_ZN_1_FLR_1 | -64, 70, 0 | -64 to 0 | 70 to 73 | 0 to 4 | 192.0 | HVAC |
| Corner_Class_2_Pod_3_ZN_1_FLR_1 | -64, 73, 0 | -64 to -53 | 73 to 82 | 0 to 4 | 99.0 | HVAC |
| Mult_Class_2_Pod_3_ZN_1_FLR_1 | -53, 73, 0 | -53 to -18 | 73 to 82 | 0 to 4 | 315.0 | HVAC |
| Computer_Class_ZN_1_FLR_1 | -18, 73, 0 | -18 to 0 | 73 to 82 | 0 to 4 | 162.0 | HVAC |
| Main_Corridor_ZN_1_FLR_1 | 0, 9, 0 | 0 to 13 | 9 to 51 | 0 to 4 | 546.0 | HVAC |
| Lobby_ZN_1_FLR_1 | 0, 0, 0 | 0 to 19 | 0 to 9 | 0 to 4 | 171.0 | HVAC |
| Mech_ZN_1_FLR_1 | 13, 9, 0 | 13 to 19 | 9 to 51 | 0 to 4 | 252.0 | HVAC |
| Bath_ZN_1_FLR_1 | 0, 51, 0 | 0 to 19 | 51 to 61 | 0 to 4 | 190.0 | HVAC |
| Offices_ZN_1_FLR_1 | 19, 0, 0 | 19 to 40 | 0 to 21 | 0 to 4 | 441.0 | HVAC |
| Gym_ZN_1_FLR_1 | 19, 21, 0 | 19 to 40 | 21 to 38 | 0 to 4 | 357.0 | HVAC |
| Kitchen_ZN_1_FLR_1 | 19, 38, 0 | 19 to 40 | 38 to 46 | 0 to 4 | 168.0 | HVAC |
| Cafeteria_ZN_1_FLR_1 | 19, 46, 0 | 19 to 40 | 46 to 61 | 0 to 4 | 315.0 | HVAC |
| Library_Media_Center_ZN_1_FLR_1 | 0, 61, 0 | 0 to 19 | 61 to 82 | 0 to 4 | 399.0 | HVAC |

The IDF has 171 building surfaces: 1 floor (adiabatic), 24 floor (groundfcfactormethod), 25 roof (outdoors), 33 wall (outdoors), 88 wall (surface). The vertex coordinates are in `Appendix_IDF.txt`. The floor polygon area is the sum of the surfaces of type Floor of the zone.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per zone that has a value in the xlsx raw_data sheet (the zone names are those of the IDF; the xlsx writes them in capital letters). All fields not named here are empty (EnergyPlus default). Every schedule is a `Schedule:Compact` written from the xlsx sheet Schedule Summary rows (Mon - Fri, Sat, Sun). The schedules of Occupants, Lighting and Electric Equipment have one set of rows for the study periods and one for the summer holiday in the xlsx: they are written with three `Through` blocks (until 6/30 study periods, until 9/1 summer holiday, until 12/31 study periods; the dates are those of NREL PDF Table B-8). The occupancy schedule of a zone is the one of its space type in the xlsx: `BLDG_OCC_SCH_Cafeteria` for the cafeteria, `BLDG_OCC_SCH_Extend` for the computer classroom, `BLDG_OCC_SCH_Gym` for the gym, `BLDG_OCC_SCH_Offices` for the offices and `BLDG_OCC_SCH` (xlsx space type Others) for all other zones.

* **`People`**: name `<zone>_People`; method `Area/Person`; floor area per person = xlsx raw_data column M; activity level schedule `ACTIVITY_SCH`. Schedules:

| Schedule | Zones |
|---|---|
| BLDG_OCC_SCH | Corner_Class_1_Pod_1_ZN_1_FLR_1, Mult_Class_1_Pod_1_ZN_1_FLR_1, Corridor_Pod_1_ZN_1_FLR_1, ... (21 zones) |
| BLDG_OCC_SCH_Extend | Computer_Class_ZN_1_FLR_1 |
| BLDG_OCC_SCH_Offices | Offices_ZN_1_FLR_1 |
| BLDG_OCC_SCH_Gym | Gym_ZN_1_FLR_1 |
| BLDG_OCC_SCH_Cafeteria | Cafeteria_ZN_1_FLR_1 |

* **`Lights`**: name `<zone>_Lights`; method `Watts/Area`; watts per floor area = xlsx raw_data column L; schedule `BLDG_LIGHT_SCH` (xlsx row Lighting, All).

* **`ElectricEquipment`**: name `<zone>_Equipment`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process; for the kitchen it includes the gas power of column O, written as given); schedule `KITCHEN_ELEC_EQUIP_SCH` for the kitchen and the cafeteria (xlsx row Electric Equipment, Kitchen, Cafeteria) and `BLDG_EQUIP_SCH` for the other zones (xlsx row Electric Equipment, Others).

* **`GasEquipment`**: `Kitchen_ZN_1_FLR_1_Gas_Equipment`; method `EquipmentLevel`; design level = xlsx raw_data column O (gas power, W); schedule `KITCHEN_GAS_EQUIP_SCH` (xlsx row Gas Equipment, Kitchen).

* **`ZoneInfiltration:DesignFlowRate`**: name `<zone>_Infiltration` for every zone that has a value in xlsx raw_data column R (flow per exterior surface area); method `Flow/ExteriorWallArea`; schedule `INFIL_SCH_PNNL` (xlsx row Infiltration, All). The lobby has in addition `<zone>_Door_Infiltration` (method `Flow/Zone`, design flow rate = xlsx raw_data column T, infiltration through the entrances, no schedule); the column S (zone flow) is 0 in the xlsx.

* **`HVACTemplate:Thermostat`**: `OthersThermostat` (heating schedule `HTGSETP_SCH_VAV_OTHER`, cooling schedule `CLGSETP_SCH_NO_SETBACK`); `MechanicalBathroomThermostat` (heating schedule `HTGSETP_SCH_Setback`, cooling schedule `CLGSETP_SCH_Setup`); `GymKitchenCafeteriaThermostat` (heating schedule `HTGSETP_SCH_VAV_OTHER`, cooling schedule `CLGSETP_SCH_NO_OPTIMUM`) (xlsx Schedule Summary, Heating Set Point and Cooling Set Point). The mechanical room and the bathroom use `MechanicalBathroomThermostat`, the gym, the kitchen and the cafeteria `GymKitchenCafeteriaThermostat` and all other zones `OthersThermostat`.

* **`HVACTemplate:System:PackagedVAV`** (4 objects, named by xlsx raw_data column I: `VAV_POD_1`, `VAV_POD_2`, `VAV_POD_3`, `VAV_OTHER`): availability schedule `HVACOperationSchd`; heating coil type `HotWater`; all other fields are EnergyPlus defaults (direct expansion cooling).

* **`HVACTemplate:Zone:VAV`** (22 objects, the zones of xlsx HVAC system type 5): zone name; template system = the system named in raw_data column I; thermostat as above; outdoor air method `Flow/Area` with the outdoor air per floor area that follows from the xlsx sheet Zone and HVAC System Summary (Total OSA Ventilation: column Q cfm/person x column N people per 1000 ft2 / 1000 + column R cfm/ft2 + column S cfm/zone / area, times 0.00508 m3/s-m2 per cfm/ft2); reheat coil type `HotWater`.

* **`HVACTemplate:System:Unitary`** (3 objects, named by xlsx raw_data column I: `PSZ-AC_2:5`, `PSZ-AC_1:6`, `PSZ-AC_2:7`): availability schedule `HVACOperationSchd`; control zone = the one zone of the system; heating coil type `Gas`; economizer type `NoEconomizer` (written because ExpandObjects writes the value `None` otherwise); all other fields are EnergyPlus defaults.

* **`HVACTemplate:Zone:Unitary`** (3 objects, the zones of xlsx HVAC system type 3: `Gym_ZN_1_FLR_1`, `Kitchen_ZN_1_FLR_1`, `Cafeteria_ZN_1_FLR_1`): template system = the system named in raw_data column I; thermostat as above; outdoor air method `Flow/Zone` with the outdoor air flow per zone = xlsx raw_data column P (total outdoor air, m3/s).

The plant (one hot water loop with a boiler, for the reheat coils of the packaged VAV systems) is in `Appendix_IDF.txt`: the xlsx names the boiler type and the fuel only. The wall and roof constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.084 Btu/h-ft2-F (Table 20, steel frame wall; Table 18) and roof U = 0.063 (Table 19, insulation entirely above deck; Table 17), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25); the slab F-factor 1.26363 W/m-K is the 90.1-2004 value of an uninsulated slab (Table 22: no insulation required).
