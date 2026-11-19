# Small Hotel: what changes the simulation results compared with the original IDF

Two changes affect the results: the U-factor of all windows and the schedules of the loads of 14 guest rooms. Everything else that differs from the original does not change the results (section 2).

## How the comparison was made

* **Original file**: the prototype IDF as downloaded (EnergyPlus version 22.1): `ASHRAE901_HotelSmall_STD2004_Buffalo.idf`.
* **Benchmark file**: `reference_full.idf` (EnergyPlus version 23.1).
* The original was first converted from 22.1 to 23.1 with the EnergyPlus tool `IDFVersionUpdater` (on a copy), so that the field changes of the version transition do not show up as differences. Then every object of the two files was compared field by field (comments, spacing and number formats ignored). No simulation was run: this is a comparison of the files.
* After the version conversion, everything that is not listed below is identical in the two files: zones, surfaces and vertices, loads, schedules in use, HVAC, controls, sizing, and the output requests.

## 1. Changes that affect the simulation results

| # | Object(s) | Original | Benchmark | Reason / source |
|---|---|---|---|---|
| 1 | `WindowMaterial:SimpleGlazingSystem` `Glazing Layer` and `Residential Window Glazing Layer`; the 103 `FenestrationSurface:Detailed` windows (26 non-residential, 77 residential) now use the constructions `NonresWindow_U_0.5700_SHGC_0.39` and `ResWindow_U_0.5700_SHGC_0.39` | U-factor 3.28203428 W/m2-K (0.578 Btu/h-ft2-F), constructions named `..._U_0.578_SHGC_...` | U-factor 3.236610 W/m2-K (0.5700 Btu/h-ft2-F); SHGC stays 0.39 | NREL PDF Table 24, p.38 (Chicago 5A, new construction): window overall U = 0.57 Btu/h-ft2-F |
| 2 | `People` (Number of People Schedule Name), `Lights` and `ElectricEquipment` (Schedule Name) of 14 guest rooms: `GuestRoom101`, `102`, `201`, `215_218`, `301`, `302_305`, `306_308`, `313`, `319`, `324`, `402_405`, `406_408`, `413` and `414` (42 objects) | `AlwaysOff`: the people, the lights and the plug loads of these guest rooms were switched off all year | `GuestRoom_Occ_Sch`, `ltg_sch_guestroom` and `Guestroom_Eqp_Sch_Base`: the schedules of the other 21 guest rooms | xlsx Schedule Summary, HotelSmall, Guest Rooms: one occupancy schedule (rows 422 to 424), one lighting schedule (rows 443 to 445) and one electric equipment schedule (rows 464 to 466) for all guest rooms; raw_data gives every guest room the same densities |

**Expected effect**: (1) a 1.38 percent lower window U-factor, so slightly less conduction through the 103 windows; (2) the 14 guest rooms (40 percent of the 35 guest-room zones) now have the occupant, lighting (11.84 W/m2) and plug load (11.89 W/m2) heat gains and the electricity use of the other guest rooms; before, these loads were zero in those rooms, so the cooling load rises and the heating load falls in them.

## 2. Differences that do not affect the simulation results

* **Objects removed that nothing uses any more**: 28 `Schedule:Compact`, 24 `Construction` (two of them are the old window constructions that were replaced in change 1), 12 `Material`, 9 `Material:NoMass`, 6 `Controller:MechanicalVentilation`, 1 `ScheduleTypeLimits`, 1 `DesignSpecification:ZoneAirDistribution` and 1 `EnergyManagementSystem:Sensor` (`OAT_F`, named by no other object).
* **Objects added**: the two window constructions of change 1.
* **Prototype header and trailing comments** (the PNNL notice, the GPARM parameter list, the commented-out `Output:Variable` lines): comments only.
* **`Version`**: 22.1 changed to 23.1 (the result of the EnergyPlus version transition).
* **Visible transmittance of the simple glazing systems** left blank on purpose (the prototype had set it equal to the SHGC). EnergyPlus then calculates it. The visible transmittance is used only by daylighting calculations; the IDF has no daylighting objects, so the heat balance and the energy results do not change.
* **Comment of the schedule of `Elevators_Lights_Fan`**: the comment that said the schedule came from the xlsx was replaced by a note that says what the schedule is (it has the values of those xlsx rows but the xlsx gives no schedule for the elevator lights and fan). Comment only; the schedule is unchanged.

## 3. Limits of this check

* The check compares the files. It does not show how large the changes in the results are; that needs a simulation of the original (after the version conversion) and of the benchmark IDF with the same weather file.
* An object counts as "unused" when no other object of the original IDF names it in a field. Names that are only used inside the text of an EMS program are not found by this check; the one `EnergyManagementSystem:Sensor` listed in section 2 (`OAT_F`) occurs in the original only in its own definition, so no EMS program uses it.
