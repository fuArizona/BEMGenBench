# Small Office: what changes the simulation results compared with the original IDF

Two changes affect the results: the U-factor of all windows and the occupancy schedule of one zone (`Perimeter_ZN_2`). Everything else that differs from the original does not change the results (section 2).

## How the comparison was made

* **Original file**: the prototype IDF as downloaded (EnergyPlus version 22.1): `ASHRAE901_OfficeSmall_STD2004_Buffalo.idf`.
* **Benchmark file**: `reference_full.idf` (EnergyPlus version 23.1).
* The original was first converted from 22.1 to 23.1 with the EnergyPlus tool `IDFVersionUpdater` (on a copy), so that the field changes of the version transition do not show up as differences. Then every object of the two files was compared field by field (comments, spacing and number formats ignored). No simulation was run: this is a comparison of the files.
* After the version conversion, everything that is not listed below is identical in the two files: zones, surfaces and vertices, loads, schedules in use, HVAC, controls, sizing, and the output requests.

## 1. Changes that affect the simulation results

| # | Object(s) | Original | Benchmark | Reason / source |
|---|---|---|---|---|
| 1 | `WindowMaterial:SimpleGlazingSystem` `Glazing Layer East`, `Glazing Layer South`, `Glazing Layer West` and `Glazing Layer North`; the 21 `FenestrationSurface:Detailed` (7 south, 4 east, 6 north, 4 west) now use the constructions `Window_U_0.5700_SHGC_East_0.39`, `..._South_...`, `..._West_...` and `..._North_...` | U-factor 3.254210806 W/m2-K (0.5731 Btu/h-ft2-F), constructions named `..._U_0.5731_SHGC_...` | U-factor 3.236610 W/m2-K (0.5700 Btu/h-ft2-F); SHGC stays 0.39 | NREL PDF Table 24, p.38 (Chicago 5A, new construction): window overall U = 0.57 Btu/h-ft2-F |
| 2 | `People` `Perimeter_ZN_2` (Number of People Schedule Name) | `BLDG_OCC_SCH_w_SB`. It differs from `BLDG_OCC_SCH_wo_SB` only in three weekday values: 0, 0 and 0 at 11:00, 13:00 and 15:00 | `BLDG_OCC_SCH_wo_SB`: 1, 0.6104 and 1 at those hours (the schedule of every other zone) | xlsx Schedule Summary, OfficeSmall, Occupants: "All (Except Perimeter_mid_ZN_2)", rows 2/3/4. The Small Office has no zone named `Perimeter_mid_ZN_2`, so the schedule applies to `Perimeter_ZN_2` too. `BLDG_OCC_SCH_w_SB` is not in the xlsx |

**Expected effect**: (1) a 0.54 percent lower window U-factor, so slightly less conduction through the 21 fenestration objects; (2) more occupant heat gain in `Perimeter_ZN_2` at 11:00, 13:00 and 15:00 on weekdays (the zone has one person per 18.58 m2).

## 2. Differences that do not affect the simulation results

* **Objects removed that nothing uses any more**: 34 `Schedule:Compact` (one of them is `BLDG_OCC_SCH_w_SB`, which change 2 left without a user), 33 `Construction` (four of them are the old window constructions that were replaced in change 1), 12 `Material`, 16 `Material:NoMass`, 5 `Controller:MechanicalVentilation`, 2 `ScheduleTypeLimits` and 1 `DesignSpecification:ZoneAirDistribution`.
* **Objects added**: the four window constructions of change 1.
* **Prototype header and trailing comments** (the PNNL notice, the GPARM parameter list, the commented-out `Output:Variable` lines): comments only.
* **`Version`**: 22.1 changed to 23.1 (the result of the EnergyPlus version transition).
* **Visible transmittance of the simple glazing systems** left blank on purpose (the prototype had set it equal to the SHGC). EnergyPlus then calculates it. The visible transmittance is used only by daylighting calculations; the IDF has no daylighting objects, so the heat balance and the energy results do not change.

## 3. Limits of this check

* The check compares the files. It does not show how large the changes in the results are; that needs a simulation of the original (after the version conversion) and of the benchmark IDF with the same weather file.
* An object counts as "unused" when no other object of the original IDF names it in a field. Names that are only used inside the text of an EMS program are not found by this check; no such case occurs in the objects listed in section 2.
