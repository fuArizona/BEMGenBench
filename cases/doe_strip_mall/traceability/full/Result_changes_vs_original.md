# Strip Mall: what changes the simulation results compared with the original IDF

One change affects the results: the hourly levels of the lighting schedules of the stores (6 schedules, 81 values). Everything else that differs from the original does not change the results (section 2).

## How the comparison was made

* **Original file**: the prototype IDF as downloaded (EnergyPlus version 22.1): `ASHRAE901_RetailStripmall_STD2004_Buffalo.idf`.
* **Benchmark file**: `reference_full.idf` (EnergyPlus version 23.1).
* The original was first converted from 22.1 to 23.1 with the EnergyPlus tool `IDFVersionUpdater` (on a copy), so that the field changes of the version transition do not show up as differences. Then every object of the two files was compared field by field (comments, spacing and number formats ignored). No simulation was run: this is a comparison of the files.
* After the version conversion, everything that is not listed below is identical in the two files: zones, surfaces and vertices, loads, schedules in use, HVAC, controls, sizing, and the output requests.

## 1. Changes that affect the simulation results

| # | Object(s) | Original | Benchmark | Reason / source |
|---|---|---|---|---|
| 1 | 6 `Schedule:Compact` of the store lighting: `ltg_sch_base_lpd1`, `ltg_sch_display_lpd_type3_smstore`, `ltg_sch_display_lpd_type3_lgstore` (xlsx Schedule Summary rows 113 to 115, Type 1 Small Store) and `ltg_sch_base_small_lpd2_type3`, `ltg_sch_display_lpd_type1_smstore`, `ltg_sch_display_lpd_type1_lgstore` (rows 122 to 124, Type 2 Large Store) | The levels 0.05008, 0.50075 and 0.95142 (`ltg_sch_base_lpd1`) and 0.05, 0.5 and 0.95 (the other five) | The levels of the xlsx: 0.0502, 0.502 and 0.9538 (rows 113 to 115) and 0.04988, 0.49875 and 0.94763 (rows 122 to 124); the levels 0 and 1 are unchanged | The xlsx is the primary document and the prototype values differ slightly from it. Largest change 0.0038 (0.4 percent of the lighting level at that hour). |

**Expected effect**: the lighting heat gain and the lighting electricity use of the stores change by at most 0.4 percent of the lighting level at the hours with the levels 0.05, 0.5 and 0.95 (about 0.24 percent lower for the Type 2 Large Store levels at 0.95, 0.4 percent higher for the Type 1 Small Store levels at 0.95); the effect on the annual results is very small.

## 2. Differences that do not affect the simulation results

* **Objects removed that nothing uses any more**: 29 `Construction`, 12 `Material`, 16 `Material:NoMass`, 23 `Schedule:Compact`, 2 `ScheduleTypeLimits`, 10 `Controller:MechanicalVentilation`, 1 `DesignSpecification:ZoneAirDistribution` and 1 `EnergyManagementSystem:Sensor` of the prototype library (none is named by an object that remains in the original).
* **Prototype header and trailing comments** (the PNNL notice, the GPARM parameter list, the commented-out `Output:Variable` lines): comments only.
* **`Version`**: 22.1 changed to 23.1 (the result of the EnergyPlus version transition).
* **Visible transmittance of the simple glazing systems** left blank on purpose (the prototype had set it equal to the SHGC). EnergyPlus then calculates it. The visible transmittance is used only by daylighting calculations; the IDF has no daylighting objects, so the heat balance and the energy results do not change.

## 3. Limits of this check

* The check compares the files. It does not show how large the changes in the results are; that needs a simulation of the original (after the version conversion) and of the benchmark IDF with the same weather file.
* An object counts as "unused" when no other object of the original IDF names it in a field. Names that are only used inside the text of an EMS program are not found by this check; no such case occurs in the objects listed in section 2.
