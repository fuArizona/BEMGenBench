# Large Office: what changes the simulation results compared with the original IDF

One change affects the results: the U-factor of all windows. Everything else that differs from the original does not change the results (section 2).

## How the comparison was made

* **Original file**: the prototype IDF as downloaded (EnergyPlus version 22.1): `ASHRAE901_OfficeLarge_STD2004_Buffalo.idf`.
* **Benchmark file**: `reference_full.idf` (EnergyPlus version 23.1).
* The original was first converted from 22.1 to 23.1 with the EnergyPlus tool `IDFVersionUpdater` (on a copy), so that the field changes of the version transition do not show up as differences. Then every object of the two files was compared field by field (comments, spacing and number formats ignored). No simulation was run: this is a comparison of the files.
* After the version conversion, everything that is not listed below is identical in the two files: zones, surfaces and vertices, loads, schedules in use, HVAC, controls, sizing, and the output requests.

## 1. Changes that affect the simulation results

| # | Object(s) | Original | Benchmark | Reason / source |
|---|---|---|---|---|
| 1 | `WindowMaterial:SimpleGlazingSystem` `Glazing Layer East`, `Glazing Layer South`, `Glazing Layer West` and `Glazing Layer North`; the 24 `FenestrationSurface:Detailed` windows (7 north, 5 east, 7 south, 5 west) now use the constructions `Window_U_0.5700_SHGC_East_0.39`, `..._South_...`, `..._West_...` and `..._North_...` | U-factor 3.254210806 W/m2-K (0.5731 Btu/h-ft2-F), constructions named `..._U_0.5731_SHGC_...` | U-factor 3.236610 W/m2-K (0.5700 Btu/h-ft2-F); SHGC stays 0.39 | NREL PDF Table 24, p.38 (Chicago 5A, new construction): window overall U = 0.57 Btu/h-ft2-F |

**Expected effect**: a 0.54 percent lower window U-factor, so slightly less conduction through the 24 windows.

## 2. Differences that do not affect the simulation results

* **Objects removed that nothing uses any more**: 29 `Schedule:Compact`, 27 `Construction` (four of them are the old window constructions that were replaced in change 1), 10 `Material`, 13 `Material:NoMass`, 5 `Controller:MechanicalVentilation` and 1 `ScheduleTypeLimits`.
* **Objects added**: the four window constructions of change 1.
* **Prototype header and trailing comments** (the PNNL notice, the GPARM parameter list, the commented-out `Output:Variable` lines): comments only.
* **`Version`**: 22.1 changed to 23.1 (the result of the EnergyPlus version transition).
* **Visible transmittance of the simple glazing systems** left blank on purpose (the prototype had set it equal to the SHGC). EnergyPlus then calculates it. The visible transmittance is used only by daylighting calculations; the IDF has no daylighting objects, so the heat balance and the energy results do not change.

## 3. Limits of this check

* The check compares the files. It does not show how large the changes in the results are; that needs a simulation of the original (after the version conversion) and of the benchmark IDF with the same weather file.
* An object counts as "unused" when no other object of the original IDF names it in a field. Names that are only used inside the text of an EMS program are not found by this check; no such case occurs in the objects listed in section 2.
