# Appendix (natural language): DOE Small Hotel, Short IDF, Buffalo

Target IDF: `DOE/Small_Hotel/Short/DOE_HotelSmall_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A 4-storey hotel, **54.86 m x 18.29 m** (180.0 ft x 60.0 ft) in plan and 11.58 m high, 4013 m2 of floor in 67 zones. Local coordinates start near the south-west corner of the building (the outer face of the walls is at x = y = 0.00 m): x to the east, y to the north, z up; all zone origins are 0, so the vertices are building coordinates (`GlobalGeometryRules`: upper-left corner, counterclockwise, relative). Every storey is one long block: a row of rooms along the south wall, a row of rooms along the north wall, and the corridor between the two rows.

* **Storey 1**: z = 0.00 m to 3.35 m (3.35 m = 11.0 ft high), 19 zones, 1003 m2.
* **Storey 2**: z = 3.35 m to 6.10 m (2.75 m = 9.0 ft high), 16 zones, 1003 m2.
* **Storey 3**: z = 6.10 m to 8.84 m (2.74 m = 9.0 ft high), 16 zones, 1003 m2.
* **Storey 4**: z = 8.84 m to 11.58 m (2.74 m = 9.0 ft high), 16 zones, 1003 m2.
* Storey 1, corridor `CorridorFlr1`: floor polygon of 12 vertices, 150.5 m2. Main strip x = 0.00 to 54.86 m, y = 8.23 to 10.06 m (1.83 m = 6.0 ft wide, 54.86 m long); branch to the south: x = 23.77 to 26.82 m, y = 0.00 to 8.23 m (3.05 m wide, 8.23 m long, up to the exterior wall); branch to the north: x = 23.77 to 26.82 m, y = 10.06 to 18.29 m (3.05 m wide, 8.23 m long, up to the exterior wall).
* Storey 2, corridor `CorridorFlr2`: floor polygon of 8 vertices, 125.4 m2. Main strip x = 0.00 to 54.86 m, y = 8.23 to 10.06 m (1.83 m = 6.0 ft wide, 54.86 m long); branch to the north: x = 23.77 to 26.82 m, y = 10.06 to 18.29 m (3.05 m wide, 8.23 m long, up to the exterior wall).
* Storey 3, corridor `CorridorFlr3`: floor polygon of 8 vertices, 125.4 m2. Main strip x = 0.00 to 54.86 m, y = 8.23 to 10.06 m (1.83 m = 6.0 ft wide, 54.86 m long); branch to the north: x = 23.77 to 26.82 m, y = 10.06 to 18.29 m (3.05 m wide, 8.23 m long, up to the exterior wall).
* Storey 4, corridor `CorridorFlr4`: floor polygon of 8 vertices, 125.4 m2. Main strip x = 0.00 to 54.86 m, y = 8.23 to 10.06 m (1.83 m = 6.0 ft wide, 54.86 m long); branch to the north: x = 23.77 to 26.82 m, y = 10.06 to 18.29 m (3.05 m wide, 8.23 m long, up to the exterior wall).

Storey 1 is the public floor. From west to east, the south row is: FrontLoungeFlr1 (x 0.00 to 19.81 m), RestroomFlr1 (x 19.81 to 23.77 m), MeetingRoomFlr1 (x 26.82 to 36.58 m), MechanicalRoomFlr1 (x 36.58 to 40.54 m), GuestRoom101 (x 40.54 to 44.50 m), GuestRoom102 (x 44.50 to 48.46 m), GuestRoom103 (x 48.46 to 52.43 m), RearStorageFlr1 (x 52.43 to 54.86 m); the north row is: FrontStairsFlr1 (x 0.00 to 2.44 m), FrontStorageFlr1 (x 2.44 to 3.96 m), FrontOfficeFlr1 (x 3.96 to 19.81 m), ExerciseCenterFlr1 (x 19.81 to 23.77 m), ElevatorCoreFlr1 (x 26.82 to 28.65 m), LaundryRoomFlr1 (x 28.65 to 40.54 m), EmployeeLoungeFlr1 (x 40.54 to 44.50 m), GuestRoom105 (x 44.50 to 48.46 m), GuestRoom104 (x 48.46 to 52.43 m), RearStairsFlr1 (x 52.43 to 54.86 m). The gap in both rows at x = 23.77 to 26.82 m is the corridor branch to the exterior wall. Storeys 2 to 4 are guest floors: guest rooms along both walls (a zone is one room, or a row of equal neighbouring rooms: `GuestRoom202_205` is one zone for the rooms 202 to 205), the two stairs, two storage zones, the elevator core and the corridor of the floor. The corridor is not a plain strip: besides the main east-west strip between the two rows it has branches to the exterior walls (listed above for each storey). The rooms of both rows are 8.23 m (27 ft) deep, a single guest room is 3.96 m (13 ft) wide.

* **Surfaces**: the floor of storey 1 is slab on grade (F-factor method, `Construction:FfactorGroundFloor`); the walls between neighbouring zones, the floors and the ceilings between storeys are interior surfaces (boundary condition `Surface` or `Zone`, a reversed pair of surfaces of the construction `GenericSurface`); the exterior walls (`ExteriorWall`) and the flat roof (`Roof`) face outdoors. Every surface polygon has comments `Derived from:` that show how each vertex coordinate is calculated from the building dimensions (ft x 0.3048) and the wall thickness; the blocks `Vertex formulas of the ...` explain the symbols.
* **Windows** (construction `Window`): 103 windows with together 184.30 m2 (the xlsx window glass area is 184.30 m2; the window fraction of the exterior wall is the xlsx Building Summary L7 = 0.1088). There are no doors in this IDF.

| Zone | Position | x range m | y range m (bounding box) | z range m | Floor area m2 | HVAC template |
|---|---|---|---|---|---|---|
| RearStairsFlr1 | north row | 52.43 to 54.86 | 10.06 to 18.29 | 0.00 to 3.35 | 20.1 | HVAC |
| CorridorFlr1 | corridor | 0.00 to 54.86 | 0.00 to 18.29 | 0.00 to 3.35 | 150.5 | HVAC |
| RearStorageFlr1 | south row | 52.43 to 54.86 | 0.00 to 8.23 | 0.00 to 3.35 | 20.1 | none |
| FrontLoungeFlr1 | south row | 0.00 to 19.81 | 0.00 to 8.23 | 0.00 to 3.35 | 163.0 | HVAC |
| RestroomFlr1 | south row | 19.81 to 23.77 | 0.00 to 8.23 | 0.00 to 3.35 | 32.6 | HVAC |
| MeetingRoomFlr1 | south row | 26.82 to 36.58 | 0.00 to 8.23 | 0.00 to 3.35 | 80.3 | HVAC |
| MechanicalRoomFlr1 | south row | 36.58 to 40.54 | 0.00 to 8.23 | 0.00 to 3.35 | 32.6 | HVAC |
| GuestRoom101 | south row | 40.54 to 44.50 | 0.00 to 8.23 | 0.00 to 3.35 | 32.6 | HVAC |
| GuestRoom102 | south row | 44.50 to 48.46 | 0.00 to 8.23 | 0.00 to 3.35 | 32.6 | HVAC |
| GuestRoom103 | south row | 48.46 to 52.43 | 0.00 to 8.23 | 0.00 to 3.35 | 32.6 | HVAC |
| GuestRoom104 | north row | 48.46 to 52.43 | 10.06 to 18.29 | 0.00 to 3.35 | 32.6 | HVAC |
| GuestRoom105 | north row | 44.50 to 48.46 | 10.06 to 18.29 | 0.00 to 3.35 | 32.6 | HVAC |
| EmployeeLoungeFlr1 | north row | 40.54 to 44.50 | 10.06 to 18.29 | 0.00 to 3.35 | 32.6 | HVAC |
| LaundryRoomFlr1 | north row | 28.65 to 40.54 | 10.06 to 18.29 | 0.00 to 3.35 | 97.8 | none |
| ElevatorCoreFlr1 | north row | 26.82 to 28.65 | 10.06 to 18.29 | 0.00 to 3.35 | 15.1 | none |
| ExerciseCenterFlr1 | north row | 19.81 to 23.77 | 10.06 to 18.29 | 0.00 to 3.35 | 32.6 | HVAC |
| FrontOfficeFlr1 | north row | 3.96 to 19.81 | 10.06 to 18.29 | 0.00 to 3.35 | 130.4 | HVAC |
| FrontStairsFlr1 | north row | 0.00 to 2.44 | 10.06 to 18.29 | 0.00 to 3.35 | 20.1 | HVAC |
| FrontStorageFlr1 | north row | 2.44 to 3.96 | 10.06 to 18.29 | 0.00 to 3.35 | 12.5 | none |
| RearStairsFlr2 | north row | 52.43 to 54.86 | 10.06 to 18.29 | 3.35 to 6.10 | 20.1 | HVAC |
| CorridorFlr2 | corridor | 0.00 to 54.86 | 8.23 to 18.29 | 3.35 to 6.10 | 125.4 | HVAC |
| RearStorageFlr2 | south row | 52.43 to 54.86 | 0.00 to 8.23 | 3.35 to 6.10 | 20.1 | none |
| GuestRoom201 | south row | 0.00 to 3.96 | 0.00 to 8.23 | 3.35 to 6.10 | 32.6 | HVAC |
| GuestRoom202_205 | south row | 3.96 to 19.81 | 0.00 to 8.23 | 3.35 to 6.10 | 130.4 | HVAC |
| GuestRoom206_208 | south row | 19.81 to 32.61 | 0.00 to 8.23 | 3.35 to 6.10 | 105.4 | HVAC |
| GuestRoom209_212 | south row | 32.61 to 48.46 | 0.00 to 8.23 | 3.35 to 6.10 | 130.4 | HVAC |
| GuestRoom213 | south row | 48.46 to 52.43 | 0.00 to 8.23 | 3.35 to 6.10 | 32.6 | HVAC |
| GuestRoom214 | north row | 48.46 to 52.43 | 10.06 to 18.29 | 3.35 to 6.10 | 32.6 | HVAC |
| GuestRoom215_218 | north row | 32.61 to 48.46 | 10.06 to 18.29 | 3.35 to 6.10 | 130.4 | HVAC |
| ElevatorCoreFlr2 | north row | 26.82 to 28.65 | 10.06 to 18.29 | 3.35 to 6.10 | 15.1 | none |
| GuestRoom219 | north row | 28.65 to 32.61 | 10.06 to 18.29 | 3.35 to 6.10 | 32.6 | HVAC |
| GuestRoom220_223 | north row | 7.92 to 23.77 | 10.06 to 18.29 | 3.35 to 6.10 | 130.4 | HVAC |
| GuestRoom224 | north row | 3.96 to 7.92 | 10.06 to 18.29 | 3.35 to 6.10 | 32.6 | HVAC |
| FrontStorageFlr2 | north row | 2.44 to 3.96 | 10.06 to 18.29 | 3.35 to 6.10 | 12.5 | none |
| FrontStairsFlr2 | north row | 0.00 to 2.44 | 10.06 to 18.29 | 3.35 to 6.10 | 20.1 | HVAC |
| RearStairsFlr3 | north row | 52.43 to 54.86 | 10.06 to 18.29 | 6.10 to 8.84 | 20.1 | HVAC |
| CorridorFlr3 | corridor | 0.00 to 54.86 | 8.23 to 18.29 | 6.10 to 8.84 | 125.4 | HVAC |
| RearStorageFlr3 | south row | 52.43 to 54.86 | 0.00 to 8.23 | 6.10 to 8.84 | 20.1 | none |
| GuestRoom301 | south row | 0.00 to 3.96 | 0.00 to 8.23 | 6.10 to 8.84 | 32.6 | HVAC |
| GuestRoom302_305 | south row | 3.96 to 19.81 | 0.00 to 8.23 | 6.10 to 8.84 | 130.4 | HVAC |
| GuestRoom306_308 | south row | 19.81 to 32.61 | 0.00 to 8.23 | 6.10 to 8.84 | 105.4 | HVAC |
| GuestRoom309_312 | south row | 32.61 to 48.46 | 0.00 to 8.23 | 6.10 to 8.84 | 130.4 | HVAC |
| GuestRoom313 | south row | 48.46 to 52.43 | 0.00 to 8.23 | 6.10 to 8.84 | 32.6 | HVAC |
| GuestRoom314 | north row | 48.46 to 52.43 | 10.06 to 18.29 | 6.10 to 8.84 | 32.6 | HVAC |
| GuestRoom315_318 | north row | 32.61 to 48.46 | 10.06 to 18.29 | 6.10 to 8.84 | 130.4 | HVAC |
| ElevatorCoreFlr3 | north row | 26.82 to 28.65 | 10.06 to 18.29 | 6.10 to 8.84 | 15.1 | none |
| GuestRoom319 | north row | 28.65 to 32.61 | 10.06 to 18.29 | 6.10 to 8.84 | 32.6 | HVAC |
| GuestRoom320_323 | north row | 7.92 to 23.77 | 10.06 to 18.29 | 6.10 to 8.84 | 130.4 | HVAC |
| GuestRoom324 | north row | 3.96 to 7.92 | 10.06 to 18.29 | 6.10 to 8.84 | 32.6 | HVAC |
| FrontStorageFlr3 | north row | 2.44 to 3.96 | 10.06 to 18.29 | 6.10 to 8.84 | 12.5 | none |
| FrontStairsFlr3 | north row | 0.00 to 2.44 | 10.06 to 18.29 | 6.10 to 8.84 | 20.1 | HVAC |
| RearStairsFlr4 | north row | 52.43 to 54.86 | 10.06 to 18.29 | 8.84 to 11.58 | 20.1 | HVAC |
| CorridorFlr4 | corridor | 0.00 to 54.86 | 8.23 to 18.29 | 8.84 to 11.58 | 125.4 | HVAC |
| RearStorageFlr4 | south row | 52.43 to 54.86 | 0.00 to 8.23 | 8.84 to 11.58 | 20.1 | none |
| GuestRoom401 | south row | 0.00 to 3.96 | 0.00 to 8.23 | 8.84 to 11.58 | 32.6 | HVAC |
| GuestRoom402_405 | south row | 3.96 to 19.81 | 0.00 to 8.23 | 8.84 to 11.58 | 130.4 | HVAC |
| GuestRoom406_408 | south row | 19.81 to 32.61 | 0.00 to 8.23 | 8.84 to 11.58 | 105.4 | HVAC |
| GuestRoom409_412 | south row | 32.61 to 48.46 | 0.00 to 8.23 | 8.84 to 11.58 | 130.4 | HVAC |
| GuestRoom413 | south row | 48.46 to 52.43 | 0.00 to 8.23 | 8.84 to 11.58 | 32.6 | HVAC |
| GuestRoom414 | north row | 48.46 to 52.43 | 10.06 to 18.29 | 8.84 to 11.58 | 32.6 | HVAC |
| GuestRoom415_418 | north row | 32.61 to 48.46 | 10.06 to 18.29 | 8.84 to 11.58 | 130.4 | HVAC |
| ElevatorCoreFlr4 | north row | 26.82 to 28.65 | 10.06 to 18.29 | 8.84 to 11.58 | 15.1 | none |
| GuestRoom419 | north row | 28.65 to 32.61 | 10.06 to 18.29 | 8.84 to 11.58 | 32.6 | HVAC |
| GuestRoom420_423 | north row | 7.92 to 23.77 | 10.06 to 18.29 | 8.84 to 11.58 | 130.4 | HVAC |
| GuestRoom424 | north row | 3.96 to 7.92 | 10.06 to 18.29 | 8.84 to 11.58 | 32.6 | HVAC |
| FrontStorageFlr4 | north row | 2.44 to 3.96 | 10.06 to 18.29 | 8.84 to 11.58 | 12.5 | none |
| FrontStairsFlr4 | north row | 0.00 to 2.44 | 10.06 to 18.29 | 8.84 to 11.58 | 20.1 | HVAC |

The IDF has 485 building surfaces: 56 ceiling (surface), 19 floor (groundfcfactormethod), 56 floor (surface), 16 roof (outdoors), 92 wall (outdoors), 246 wall (surface). The vertex coordinates are in `Appendix_IDF.txt`.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per zone that has a value in the xlsx raw_data sheet (the zone names are those of the IDF; the xlsx writes them in capital letters). All fields not named here are empty (EnergyPlus default). The schedule of a zone is the one of its space type in the xlsx sheet Schedule Summary; the schedule names are the names of the `Schedule:Compact` objects of `Appendix_IDF.txt`.

* **`People`**: name `<zone>_People`; method `Area/Person`; floor area per person = xlsx raw_data column M; activity level schedule `ACTIVITY_SCH`. Schedules:

| Schedule | Zones (zone name without number: count) |
|---|---|
| AlwaysOff | RearStairs (4), Corridor (4), RearStorage (4), MechanicalRoom (1), ElevatorCore (4), FrontStairs (4), FrontStorage (4) |
| Lobby_Occ_Sch | FrontLounge (1), Restroom (1) |
| MeetingRoom_Occ_w_SB_Sch | MeetingRoom (1) |
| GuestRoom_Occ_Sch | GuestRoom (35) |
| EmployeeLounge_Occ_Sch | EmployeeLounge (1) |
| LaundryRoom_Occ_Sch | LaundryRoom (1) |
| ExerciseCenter_Occ_Sch | ExerciseCenter (1) |
| Office_Occ_w_SB_Sch | FrontOffice (1) |

* **`Lights`**: name `<zone>_Lights`; method `Watts/Area`; watts per floor area = xlsx raw_data column L. Schedules:

| Schedule | Zones (zone name without number: count) |
|---|---|
| ltg_sch_stair | RearStairs (4), FrontStairs (4) |
| ltg_sch_corridor | Corridor (4) |
| ltg_sch_storage | RearStorage (4), FrontStorage (4) |
| ltg_sch_lobby | FrontLounge (1) |
| ltg_sch_restroom | Restroom (1) |
| ltg_sch_meeting | MeetingRoom (1) |
| ltg_sch_mechanical | MechanicalRoom (1) |
| ltg_sch_guestroom | GuestRoom (35) |
| ltg_sch_lounge | EmployeeLounge (1) |
| ltg_sch_laundry | LaundryRoom (1) |
| ltg_sch_exercise | ExerciseCenter (1) |
| ltg_sch_office | FrontOffice (1) |

* **`ElectricEquipment`**: name `<zone>_Equipment`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process). Schedules:

| Schedule | Zones (zone name without number: count) |
|---|---|
| Lobby_Eqp_Sch | FrontLounge (1) |
| MeetingRoom_Eqp_Sch | MeetingRoom (1) |
| GuestRoom_Eqp_Sch_Base | GuestRoom (35) |
| EmployeeLounge_Eqp_Sch | EmployeeLounge (1) |
| LaundryRoom_Eqp_Elec_Sch | LaundryRoom (1) |
| BLDG_ELEVATORS | ElevatorCore (1) |
| ExerciseCenter_Eqp_Sch | ExerciseCenter (1) |
| OFF_EQUIP_SCH | FrontOffice (1) |

* **`GasEquipment`**: name `<zone>_Gas_Equipment`; method `EquipmentLevel`; design level (W) = xlsx raw_data column O; zones: LaundryRoomFlr1 (schedule `LaundryRoom_Eqp_Gas_Sch`).

* **`ZoneInfiltration:DesignFlowRate`**: one object per zone and per non-zero value of the xlsx. `<zone>_Infiltration`: method `Flow/ExteriorWallArea`, flow per exterior surface area = raw_data column R. `<zone>_Zone_Infiltration`: method `Flow/Zone`, no schedule, design flow rate = column S. `<zone>_Door_Infiltration`: method `Flow/Zone`, no schedule, design flow rate = column T (entrances). Method and schedule of the objects:

| Method | Schedule | Zones |
|---|---|---|
| Flow/ExteriorWallArea | AlwaysOn | RearStairs (4), Corridor (4), RearStorage (4), ElevatorCore (4), FrontStairs (4), FrontStorage (4) |
| Flow/Zone | (none: always on) | Corridor (1) |
| Flow/ExteriorWallArea | CommonArea_Infil_Sch | FrontLounge (1), Restroom (1), EmployeeLounge (1), ExerciseCenter (1), FrontOffice (1) |
| Flow/ExteriorWallArea | GuestRoom_Infil_Sch | MeetingRoom (1), MechanicalRoom (1), GuestRoom (35), LaundryRoom (1) |

* **`HVACTemplate:Thermostat`**: `GuestRoomThermostat`: heating schedule `Base_S_OccGuestRoom_HtgSP_Sch`, cooling schedule `Base_S_OccGuestRoom_ClgSP_Sch`; `CommonAreaThermostat`: heating schedule `CommonArea_HtgSP_Sch`, cooling schedule `CommonArea_ClgSP_Sch` (xlsx Schedule Summary, Heating / Cooling Set Point). `GuestRoomThermostat` serves the guest rooms, `CommonAreaThermostat` all other zones.

* **`HVACTemplate:Zone:PTAC`** (39 objects, xlsx HVAC system type 1.1 PTAC with electric heating): zone name; thermostat `GuestRoomThermostat`; availability schedule `COMPACT HVAC-ALWAYS 1`; heating coil type `Electric`. One per guest room zone.

* **`HVACTemplate:System:Unitary`** (15 objects, named by xlsx raw_data column I, one per zone): availability schedule `COMPACT HVAC-ALWAYS 1`; control zone = the zone; economizer type `NoEconomizer` (written explicitly: without it ExpandObjects writes an economizer type that EnergyPlus rejects). 6 systems of xlsx type 3 (PSZ-AC): cooling coil type `SingleSpeedDX`, heating coil type `Gas`; 9 systems of xlsx type 10 (heating and ventilation): cooling coil type `None`, heating coil type `Electric`.

* **`HVACTemplate:Zone:Unitary`**: zone name; template system = the unit of the zone; thermostat `CommonAreaThermostat`; outdoor air method `Flow/Zone` with the outdoor air per zone of xlsx raw_data column P (m3/s) when the xlsx gives one.

* **Zones without HVAC**: 13 zones of the xlsx are not conditioned (system type `NA`): they have no HVAC template.

The wall and roof constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.084 Btu/h-ft2-F (Table 20, steel-frame wall) and roof U = 0.063 (Table 19, insulation entirely above deck), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25). Where the xlsx gives no schedule for the people, lights or equipment of a zone, the schedule `AlwaysOff` (value 0) is used, because EnergyPlus needs a schedule.
