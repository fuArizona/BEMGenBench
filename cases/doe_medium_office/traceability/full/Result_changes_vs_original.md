# Medium Office: what changes the simulation results compared with the original IDF

Two changes affect the results: the stucco thickness of the exterior walls of the non-residential constructions and the removal of the optimum-start energy management system (EMS). Everything else that differs from the original does not change the results (section 2).

## How the comparison was made

* **Original file**: the prototype IDF as downloaded (EnergyPlus version 22.1): `ASHRAE901_OfficeMedium_STD2004_Buffalo.idf`.
* **Benchmark file**: `reference_full.idf` (EnergyPlus version 23.1).
* The original was first converted from 22.1 to 23.1 with the EnergyPlus tool `IDFVersionUpdater` (on a copy), so that the field changes of the version transition do not show up as differences. Then every object of the two files was compared field by field (comments, spacing and number formats ignored). No simulation was run: this is a comparison of the files.
* After the version conversion, everything that is not listed below is identical in the two files: zones, surfaces and vertices, loads, schedules in use, HVAC, controls, sizing, and the output requests.

## 1. Changes that affect the simulation results

| # | Object(s) | Original | Benchmark | Reason / source |
|---|---|---|---|---|
| 1 | `Construction` `nonres_ext_wall_grd`, `nonres_ext_wall_mid`, `nonres_ext_wall_top` (3 constructions; every exterior wall surface uses one of them) | Outside layer `F07 25mm stucco`: 0.0254 m thick | Outside layer `F07 10mm stucco` (a new `Material`): 0.01016 m thick; other properties unchanged | xlsx Building Summary, Medium Office exterior wall: "0.4 in. stucco" = 0.01016 m. The PNNL file had 25 mm (1 in.) |
| 2 | The optimum-start EMS of the prototype: 3 `EnergyManagementSystem:Program`, 3 `EnergyManagementSystem:ProgramCallingManager`, 6 `EnergyManagementSystem:Actuator`, 3 `EnergyManagementSystem:InternalVariable`, 2 `EnergyManagementSystem:Sensor` (17 objects), and the schedules that only they used | In all three air loops the supply fan is larger than 4.719474 m3/s (10000 cfm), so the EMS replaced the heating set point schedule `HTGSETP_SCH_PACU_VAV_*` of the 15 thermostats by the prototype schedule `HTGSETP_SCH_YES_OPTIMUM_ORIGINAL`: on weekdays and Saturdays 17.8 C from 05:00 to 06:00 and 20.0 C from 06:00 to 07:00, then 21.0 C | Removed. The thermostats use the xlsx heating schedules `HTGSETP_SCH_PACU_VAV_bot`, `_mid`, `_top` as they are: 21.0 C from 05:00 on weekdays and Saturdays | Decision of the user: the optimum-start programs are not in the xlsx or the PDF and were removed; the xlsx "Heating Set Point" rows (Schedule Summary, rows 50 to 52) give 21.0 C from 06:00. The EMS objects of the transformer load program are kept |

**Expected effect**: (1) slightly lower resistance and thermal mass of the exterior walls; (2) between 05:00 and 07:00 on weekdays and Saturdays the heating set point is higher than in the original (21.0 C instead of 17.8 C and 20.0 C), so the morning heating energy and the peak heating load can change slightly. The winter design day, the cooling set points and all other hours are the same.

## 2. Differences that do not affect the simulation results

* **Objects removed that nothing uses any more**: 25 `Construction`, 11 `Material`, 13 `Material:NoMass`, 2 `ScheduleTypeLimits` and 37 `Schedule:Compact` (several of the schedules were used only by the removed EMS objects, change 2).
* **Prototype header and trailing comments** (the PNNL notice, the GPARM parameter list, the commented-out `Output:Variable` lines): comments only.
* **`Version`**: 22.1 changed to 23.1 (the result of the EnergyPlus version transition).
* **Visible transmittance of the simple glazing systems** left blank on purpose (the prototype had set it equal to the SHGC). EnergyPlus then calculates it. The visible transmittance is used only by daylighting calculations; the IDF has no daylighting objects, so the heat balance and the energy results do not change.

## 3. Limits of this check

* The check compares the files. It does not show how large the changes in the results are; that needs a simulation of the original (after the version conversion) and of the benchmark IDF with the same weather file.
* An object counts as "unused" when no other object of the original IDF names it in a field. Names that are only used inside the text of an EMS program are not found by this check; no such case occurs in the objects listed in section 2.
