# Mid-rise Apartment: what changes the simulation results compared with the original IDF

Two changes affect the results: the stucco thickness of all exterior walls and the U-factor of all windows. Everything else that differs from the original does not change the results (section 2).

## How the comparison was made

* **Original file**: the prototype IDF as downloaded (EnergyPlus version 22.1): `ASHRAE901_ApartmentMidRise_STD2004_Buffalo.idf`.
* **Benchmark file**: `reference_full.idf` (EnergyPlus version 23.1).
* The original was first converted from 22.1 to 23.1 with the EnergyPlus tool `IDFVersionUpdater` (on a copy), so that the field changes of the version transition do not show up as differences. Then every object of the two files was compared field by field (comments, spacing and number formats ignored). No simulation was run: this is a comparison of the files.
* After the version conversion, everything that is not listed below is identical in the two files: zones, surfaces and vertices, loads, schedules in use, HVAC, controls, sizing, and the output requests.

## 1. Changes that affect the simulation results

| # | Object(s) | Original | Benchmark | Reason / source |
|---|---|---|---|---|
| 1 | `Construction` `res_ext_wall_grd`, `res_ext_wall_mid`, `res_ext_wall_top`, `nonres_ext_wall_grd`, `nonres_ext_wall_mid`, `nonres_ext_wall_top` (6 constructions) | Outside layer `F07 25mm stucco`: 0.0254 m thick | Outside layer `F07 10mm stucco` (a new `Material`): 0.01016 m thick; other properties unchanged | xlsx Building Summary, Mid-rise Apartment exterior wall: "0.4 in. stucco" = 0.01016 m. The PNNL file had 25 mm (1 in.) |
| 2 | `WindowMaterial:SimpleGlazingSystem` `Res Window Glazing Layer` and `Nonres Window Glazing Layer`; the 39 `FenestrationSurface:Detailed` windows (34 residential, 5 non-residential) now use the constructions `ResWindow_U_0.5700_SHGC_0.39` and `NonresWindow_U_0.5700_SHGC_0.39` | U-factor 3.376293396 W/m2-K (0.5946 Btu/h-ft2-F), constructions named `..._U_0.5946_SHGC_0.39` | U-factor 3.236610 W/m2-K (0.5700 Btu/h-ft2-F); SHGC stays 0.39 | NREL PDF Table 24, p.38 (Chicago 5A, new construction): window overall U = 0.57 Btu/h-ft2-F |

**Expected effect**: (1) slightly lower resistance and thermal mass of the exterior walls (the stucco layer is 15.24 mm thinner); (2) a 4.1 percent lower window U-factor, so less conduction through all 39 windows.

## 2. Differences that do not affect the simulation results

* **Objects removed that nothing uses any more**: 18 `Schedule:Compact`, 23 `Construction` (two of them are the old window constructions that were replaced in change 2), 11 `Material`, 9 `Material:NoMass`, 1 `DesignSpecification:ZoneAirDistribution` and 1 `Controller:MechanicalVentilation`.
* **Prototype header and trailing comments** (the PNNL notice, the GPARM parameter list, the commented-out `Output:Variable` lines): comments only.
* **`Version`**: 22.1 changed to 23.1 (the result of the EnergyPlus version transition).
* **Visible transmittance of the simple glazing systems** left blank on purpose (the prototype had set it equal to the SHGC). EnergyPlus then calculates it. The visible transmittance is used only by daylighting calculations; the IDF has no daylighting objects, so the heat balance and the energy results do not change.

## 3. Limits of this check

* The check compares the files. It does not show how large the changes in the results are; that needs a simulation of the original (after the version conversion) and of the benchmark IDF with the same weather file.
* An object counts as "unused" when no other object of the original IDF names it in a field. Names that are only used inside the text of an EMS program are not found by this check; no such case occurs in the objects listed in section 2.
