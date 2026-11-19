# Warehouse: what changes the simulation results compared with the original IDF

Two changes affect the results: the SHGC of the windows and the removal of the skylights. Everything else that differs from the original does not change the results (section 2).

## How the comparison was made

* **Original file**: the prototype IDF as downloaded (EnergyPlus version 22.1): `ASHRAE901_Warehouse_STD2004_Buffalo.idf`.
* **Benchmark file**: `reference_full.idf` (EnergyPlus version 23.1).
* The original was first converted from 22.1 to 23.1 with the EnergyPlus tool `IDFVersionUpdater` (on a copy), so that the field changes of the version transition do not show up as differences. Then every object of the two files was compared field by field (comments, spacing and number formats ignored). No simulation was run: this is a comparison of the files.
* After the version conversion, everything that is not listed below is identical in the two files: zones, surfaces and vertices, loads, schedules in use, HVAC, controls, sizing, and the output requests.

## 1. Changes that affect the simulation results

| # | Object(s) | Original | Benchmark | Reason / source |
|---|---|---|---|---|
| 1 | `WindowMaterial:SimpleGlazingSystem` `Nonres Window Glazing Layer North` and `... West`; the 4 office windows `Office Front Wall Window 1`, `Office Front Wall Window2`, `Office Left Wall Window1`, `Office Left Wall Window2` now use the constructions `NonresWindow_U_0.5726_SHGC_North_0.39` and `..._West_0.39` | SHGC 0.49 (constructions named `..._SHGC_North_0.49` and `..._SHGC_West_0.49`); U-factor 3.251371676 W/m2-K unchanged | SHGC 0.39 | NREL PDF Table 25, p.39 (Chicago 5A, new construction): SHGC = 0.39 |
| 2 | 10 skylights (`FenestrationSurface:Detailed` `skylight_r1c1` to `skylight_r2c5`, construction `SemiHtdSkylight_U_1.02_SHGC_0.55`), their frame and divider (`Skylight_Frame_Semiheated`) and the skylight glazing systems (`Semiheated Skylight Glazing Layer`, `Nonres Skylight Glazing Layer`) with their constructions | Skylights in the roof of the warehouse | Removed | The xlsx Building Summary (row 5, building shape) shows the warehouse without skylights, and neither the xlsx nor the NREL PDF gives a skylight (area, U-factor, SHGC or visible transmittance) |

**Expected effect**: (1) less solar heat gain through the office windows (SHGC 0.49 to 0.39); (2) no solar gain and no extra conduction through the 10 roof skylights: the roof is opaque there, so the cooling load and the heating load of the storage zones change (the lighting is not controlled by daylight in this IDF, so the lighting energy does not change).

## 2. Differences that do not affect the simulation results

* **Objects removed that nothing uses any more**: 37 `Construction` (the skylight constructions of change 2, the two old window constructions replaced in change 1 and unused library constructions), 15 `Material`, 15 `Material:NoMass`, 17 `Schedule:Compact`, 2 `Controller:MechanicalVentilation`, 1 `DesignSpecification:ZoneAirDistribution`, 1 `EnergyManagementSystem:Sensor`, and unused glazing objects of the prototype library: 2 `WindowProperty:FrameAndDivider` (one is `Skylight_Frame_Nonres`), 2 `WindowMaterial:SimpleGlazingSystem` (`Nonres Window Glazing Layer South` and `East`), 2 `WindowMaterial:Glazing` and 1 `WindowMaterial:Gas`.
* **Prototype header and trailing comments** (the PNNL notice, the GPARM parameter list, the commented-out `Output:Variable` lines): comments only.
* **`Version`**: 22.1 changed to 23.1 (the result of the EnergyPlus version transition).
* **Visible transmittance of the simple glazing systems** left blank on purpose (the prototype had set it equal to the SHGC). EnergyPlus then calculates it. The visible transmittance is used only by daylighting calculations; the IDF has no daylighting objects, so the heat balance and the energy results do not change.

## 3. Limits of this check

* The check compares the files. It does not show how large the changes in the results are; that needs a simulation of the original (after the version conversion) and of the benchmark IDF with the same weather file.
* An object counts as "unused" when no other object of the original IDF names it in a field. Names that are only used inside the text of an EMS program are not found by this check; no such case occurs in the objects listed in section 2.
