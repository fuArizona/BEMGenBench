# Values of the Short IDF that the documents do not give: DOE Small Hotel

The Short IDF keeps what the input documents give (the xlsx and the NREL PDF) plus what EnergyPlus needs to run. This list names everything in it that is **not** taken from a document. Every entry also has a comment in the IDF. It is made by a script from the IDF, so it is rebuilt whenever the IDF is rebuilt.

## 1. Needed by EnergyPlus

| Object | Value | Why |
|---|---|---|
| `Version` | 23.1 | the EnergyPlus version of the file |
| `GlobalGeometryRules` | LowerLeftCorner, Counterclockwise, Relative | required object; the vertex convention of the polygons |
| `SimulationControl` | Yes, Yes | the autosized HVACTemplate equipment needs zone and system sizing |
| `SizingPeriod:WeatherFileConditionType` | Summer, SummerExtreme | sizing days from the weather file, so the IDF needs no design-day objects |
| `SizingPeriod:WeatherFileConditionType` | Winter, WinterExtreme | sizing days from the weather file, so the IDF needs no design-day objects |
| `RunPeriod` | Annual, 1, 1, 12, 31 | the documents give only the city: one full year |

A schedule needs a value for every day type. The day types SummerDesignDay and WinterDesignDay (used by sizing) are listed with the first weekday clause of each schedule, so sizing uses the Monday-Friday values of the documents.

The PDF (Appendix B, Table B-12, hourly operation schedules) has SummerDesign and WinterDesign rows for this building. They are **not used**: the schedules of the PDF are not the schedules of the xlsx. Compared for the Small Office and the Medium Office, the Monday-Friday values of the PDF differ from the xlsx in 14 of the 15 schedules, and only 4 of 14 (Small Office) and 8 of 16 (Medium Office) design-day clauses of the prototype equal the PDF rows. Taking some design days from the PDF would put two versions of a schedule into one object, and the xlsx is the primary document.

## 2. Constructions and ground constants

* **`GenericLayer`** (construction `GenericSurface`): thermal resistance 0.2 m2-K/W, **assumed**. EnergyPlus needs a construction for every surface; the documents describe only the exterior walls, the roof and the windows. Used by: 56 ceilings (boundary condition Surface); 56 floors (boundary condition Surface); 246 walls (boundary condition Surface).
* **`Construction:FfactorGroundFloor`** x 19: F-factor 1.26363 W/m-K. The PDF (Table 22) gives no slab insulation (NR); this is the 90.1-2004 value of an uninsulated slab, so it is derived, not given. The area is the area of the floor polygon of each zone and the exposed perimeter is the sum of the bottom edges of the exterior walls that stand on that floor; both are computed from the polygons of the IDF, and the comment of each field shows the calculation.
* **Windows:** only `WindowMaterial:SimpleGlazingSystem` (U and SHGC from the PDF); no frame, no divider.

## 3. Schedules

Given by the PDF but not by the xlsx:

* `Activity_Sch` = 132 for all 24 hours (NREL PDF Table B-12, p.97 (page 108 of the file): ACTIVITY_SCH, All, 120 for all 24 hours.)

Not in the documents:

* `AlwaysOff` = 0 for all hours

## 4. HVACTemplate values written without a document source

| Object | Field | Value (count) | Note |
|---|---|---|---|
| `HVACTemplate:System:Unitary` | Economizer Type | NoEconomizer (15) | same as the EnergyPlus default |
| `HVACTemplate:Zone:Unitary` | Outdoor Air Method | Flow/Zone (5) | how the template reads the outdoor air value of the xlsx (per zone or per floor area) |

Every other field of the HVACTemplate objects is blank: EnergyPlus uses its default or autosizes it (fan and coil capacities, flow rates, efficiencies, minimum flow fractions). The documents give the system type of each zone, the outdoor air, the availability and the set point schedules.

## 5. Geometry and other blanks

* **Vertex coordinates** (67 zones, 485 surfaces, 103 windows and doors; 67 zones have a non-zero origin): the documents give areas and building dimensions only. The polygons are kept from the prototype; the comments show how each coordinate follows from the dimensions.
* **Blank fields** of `Building`, `Zone`, `People`, `Lights`, `ElectricEquipment` and `ZoneInfiltration:DesignFlowRate` (radiant fractions, terrain, North axis, coefficients) use the EnergyPlus defaults and are not written.
* **No other prototype data** (curves, fans, coils, nodes, meters, outputs, service water heating, exterior lights, ground temperatures, Timestep).

## 6. Notes

**The coordinates of this Short IDF are the prototype's, moved by (-x0, -y0) and snapped to whole feet.**

* The prototype writes every X and Y with an offset x0 = 0.048684 m (0.1597 ft), y0 = 0.048845 m (0.1603 ft) and, on some far edges (x = 180 ft, y = 27, 33 and 60 ft), a further 0.000584 m. None of this is in the documents (it comes from the program that generated the prototype).
* Here the whole building is moved by (-x0, -y0) and those edges are set to whole feet, so the coordinates are n ft x 0.3048. The shape and the relative positions do not change; areas change by at most 0.03 percent (for example a stair zone of 8 ft x 27 ft is exactly 216.000 ft2). Positions that are not a whole number of feet (windows, doors) are only moved.
* The area and the exposed perimeter of the ground floors (`Construction:FfactorGroundFloor`) are written again from the moved polygons, and their comments say what the prototype had.
