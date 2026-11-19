# Stand-alone Retail: what changes the simulation results compared with the original IDF

Two changes affect the results: the SHGC of the windows and the removal of the skylights. Everything else that differs from the original does not change the results (section 2).

## How the comparison was made

* **Original file**: the prototype IDF as downloaded (EnergyPlus version 22.1): `ASHRAE901_RetailStandalone_STD2004_Buffalo.idf`.
* **Benchmark file**: `reference_full.idf` (EnergyPlus version 23.1).
* The original was first converted from 22.1 to 23.1 with the EnergyPlus tool `IDFVersionUpdater` (on a copy), so that the field changes of the version transition do not show up as differences. Then every object of the two files was compared field by field (comments, spacing and number formats ignored). No simulation was run: this is a comparison of the files.
* After the version conversion, everything that is not listed below is identical in the two files: zones, surfaces and vertices, loads, schedules in use, HVAC, controls, sizing, and the output requests.

## 1. Changes that affect the simulation results

| # | Object(s) | Original | Benchmark | Reason / source |
|---|---|---|---|---|
| 1 | `WindowMaterial:SimpleGlazingSystem` `Nonres Window Glazing Layer`; the 3 windows `Point_Of_Sale_Wall_South_Glazing`, `Front_Retail_Wall_South_Glazing`, `Front_Entry_Wall_South_Glazing` now use the construction `NonresWindow_U_0.5722_SHGC_0.39` | SHGC 0.49 (construction named `NonresWindow_U_0.5722_SHGC_0.49`); U-factor 3.249100372 W/m2-K unchanged | SHGC 0.39 | NREL PDF Table 25, p.39 (Chicago 5A, new construction): SHGC = 0.39 |
| 2 | 8 skylights (`FenestrationSurface:Detailed`), their glazing system (1 `WindowMaterial:SimpleGlazingSystem`), their frame and divider (1 `WindowProperty:FrameAndDivider`) and their construction | Skylights in the roof of the store | Removed | The xlsx Building Summary (row 5, building shape) shows the store without skylights, and neither the xlsx nor the NREL PDF gives a skylight (area, U-factor, SHGC or visible transmittance) |

**Expected effect**: (1) less solar heat gain through the 3 south windows (SHGC 0.49 to 0.39); (2) no solar gain and no extra conduction through the 8 roof skylights: the roof is opaque there, so the cooling load and the heating load of the sales zones change (the lighting is not controlled by daylight in this IDF, so the lighting energy does not change).

## 2. Differences that do not affect the simulation results

* **Objects removed that nothing uses any more**: 30 further `Construction` (31 in all, one of them is the old window construction replaced in change 1), 13 `Material`, 16 `Material:NoMass`, 28 `Schedule:Compact`, 2 `ScheduleTypeLimits`, 4 `Controller:MechanicalVentilation` and 1 `DesignSpecification:ZoneAirDistribution`.
* **Prototype header and trailing comments** (the PNNL notice, the GPARM parameter list, the commented-out `Output:Variable` lines): comments only.
* **`Version`**: 22.1 changed to 23.1 (the result of the EnergyPlus version transition).
* **Visible transmittance of the simple glazing systems** left blank on purpose (the prototype had set it equal to the SHGC). EnergyPlus then calculates it. The visible transmittance is used only by daylighting calculations; the IDF has no daylighting objects, so the heat balance and the energy results do not change.

## 3. Limits of this check

* The check compares the files. It does not show how large the changes in the results are; that needs a simulation of the original (after the version conversion) and of the benchmark IDF with the same weather file.
* An object counts as "unused" when no other object of the original IDF names it in a field. Names that are only used inside the text of an EMS program are not found by this check; no such case occurs in the objects listed in section 2.
