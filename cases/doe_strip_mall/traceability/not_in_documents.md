# Values of the Short IDF that the documents do not give: DOE Strip Mall

The Short IDF keeps what the input documents give (the xlsx and the NREL PDF) plus what EnergyPlus needs to run. This list names everything in it that is **not** taken from a document. Every entry also has a comment in the IDF. It is made by a script from the IDF, so it is rebuilt whenever the IDF is rebuilt.

## 1. Needed by EnergyPlus

| Object | Value | Why |
|---|---|---|
| `Version` | 23.1 | the EnergyPlus version of the file |
| `GlobalGeometryRules` | UpperLeftCorner, Counterclockwise, Relative | required object; the vertex convention of the polygons |
| `SimulationControl` | Yes, Yes | the autosized HVACTemplate equipment needs zone and system sizing |
| `SizingPeriod:WeatherFileConditionType` | Summer, SummerExtreme | sizing days from the weather file, so the IDF needs no design-day objects |
| `SizingPeriod:WeatherFileConditionType` | Winter, WinterExtreme | sizing days from the weather file, so the IDF needs no design-day objects |
| `RunPeriod` | Annual, 1, 1, 12, 31 | the documents give only the city: one full year |

A schedule needs a value for every day type. The day types SummerDesignDay and WinterDesignDay (used by sizing) are listed with the first weekday clause of each schedule, so sizing uses the Monday-Friday values of the documents.

The PDF (Appendix B, Table B-14, hourly operation schedules) has SummerDesign and WinterDesign rows for this building. They are **not used**: the schedules of the PDF are not the schedules of the xlsx. Compared for the Small Office and the Medium Office, the Monday-Friday values of the PDF differ from the xlsx in 14 of the 15 schedules, and only 4 of 14 (Small Office) and 8 of 16 (Medium Office) design-day clauses of the prototype equal the PDF rows. Taking some design days from the PDF would put two versions of a schedule into one object, and the xlsx is the primary document.

## 2. Constructions and ground constants

* **`GenericLayer`** (construction `GenericSurface`): thermal resistance 0.2 m2-K/W, **assumed**. EnergyPlus needs a construction for every surface; the documents describe only the exterior walls, the roof and the windows. Used by: 18 walls (boundary condition Surface).
* **`Construction:FfactorGroundFloor`** x 10: F-factor 1.26363 W/m-K. The PDF (Table 22) gives no slab insulation (NR); this is the 90.1-2004 value of an uninsulated slab, so it is derived, not given. The area is the area of the floor polygon of each zone and the exposed perimeter is the sum of the bottom edges of the exterior walls that stand on that floor; both are computed from the polygons of the IDF, and the comment of each field shows the calculation.
* **Windows:** only `WindowMaterial:SimpleGlazingSystem` (U and SHGC from the PDF); no frame, no divider.

## 3. Schedules

Given by the PDF but not by the xlsx:

* `ACTIVITY_SCH` = 120 for all 24 hours (NREL PDF Table B-14, p.102 (page 113 of the file): ACTIVITY_SCH, All, 120 for all 24 hours.)

## 4. HVACTemplate values written without a document source

| Object | Field | Value (count) | Note |
|---|---|---|---|
| `HVACTemplate:System:Unitary` | Economizer Type | NoEconomizer (10) | same as the EnergyPlus default |
| `HVACTemplate:Zone:Unitary` | Outdoor Air Method | Flow/Zone (10) | how the template reads the outdoor air value of the xlsx (per zone or per floor area) |

Every other field of the HVACTemplate objects is blank: EnergyPlus uses its default or autosizes it (fan and coil capacities, flow rates, efficiencies, minimum flow fractions). The documents give the system type of each zone, the outdoor air, the availability and the set point schedules.

## 5. Geometry and other blanks

* **Vertex coordinates** (10 zones, 60 surfaces, 36 windows and doors; 10 zones have a non-zero origin): the documents give areas and building dimensions only. The polygons are kept from the prototype; the comments show how each coordinate follows from the dimensions.
* **Blank fields** of `Building`, `Zone`, `People`, `Lights`, `ElectricEquipment` and `ZoneInfiltration:DesignFlowRate` (radiant fractions, terrain, North axis, coefficients) use the EnergyPlus defaults and are not written.
* **No other prototype data** (curves, fans, coils, nodes, meters, outputs, service water heating, exterior lights, ground temperatures, Timestep).
