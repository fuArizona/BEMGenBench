# Values of the Short IDF that the documents do not give: DOE Warehouse

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

The PDF (Appendix B, Table B-16, hourly operation schedules) has SummerDesign and WinterDesign rows for this building. They are **not used**: the schedules of the PDF are not the schedules of the xlsx. Compared for the Small Office and the Medium Office, the Monday-Friday values of the PDF differ from the xlsx in 14 of the 15 schedules, and only 4 of 14 (Small Office) and 8 of 16 (Medium Office) design-day clauses of the prototype equal the PDF rows. Taking some design days from the PDF would put two versions of a schedule into one object, and the xlsx is the primary document.

## 2. Constructions and ground constants

* **`GenericLayer`** (construction `GenericSurface`): thermal resistance 0.2 m2-K/W, **assumed**. EnergyPlus needs a construction for every surface; the documents describe only the exterior walls, the roof and the windows. Used by: 2 roofs (boundary condition Outdoors); 1 roofs (boundary condition Zone); 10 walls (boundary condition Outdoors); 3 walls (boundary condition Zone).
* **`Construction:FfactorGroundFloor`** x 3: F-factor 1.26363 W/m-K. The PDF (Table 22) gives no slab insulation (NR); this is the 90.1-2004 value of an uninsulated slab, so it is derived, not given. The area is the area of the floor polygon of each zone and the exposed perimeter is the sum of the bottom edges of the exterior walls that stand on that floor; both are computed from the polygons of the IDF, and the comment of each field shows the calculation.
* **Windows:** only `WindowMaterial:SimpleGlazingSystem` (U and SHGC from the PDF); no frame, no divider.

## 3. Schedules

Given by the PDF but not by the xlsx:

* `ACTIVITY_SCH` = 131.85 for all 24 hours (NREL PDF Table B-16, p.107 (page 118 of the file): ACTIVITY_SCH, All, 120 for all 24 hours.)

## 4. HVACTemplate values written without a document source

| Object | Field | Value (count) | Note |
|---|---|---|---|
| `HVACTemplate:System:Unitary` | Economizer Type | NoEconomizer (3) | same as the EnergyPlus default |
| `HVACTemplate:Zone:Unitary` | Outdoor Air Method | Flow/Zone (2) | how the template reads the outdoor air value of the xlsx (per zone or per floor area) |

Every other field of the HVACTemplate objects is blank: EnergyPlus uses its default or autosizes it (fan and coil capacities, flow rates, efficiencies, minimum flow fractions). The documents give the system type of each zone, the outdoor air, the availability and the set point schedules.

## 5. Geometry and other blanks

* **Vertex coordinates** (3 zones, 19 surfaces, 4 windows and doors; 3 zones have a non-zero origin): the documents give areas and building dimensions only. The polygons are kept from the prototype; the comments show how each coordinate follows from the dimensions.
* **Scale factor k = 0.9999512332:** the coordinates are written as feet x 0.3048 x k. k is not a quantity of the prototype IDF either: the prototype has only the coordinates in metres, and k is a factor fitted here to describe them. k is not written in the documents; it is derived from the xlsx total area (the geometry is scaled so that the zone areas add up to the xlsx total). The check against the documents: with this k the horizontal area of each of the 3 zones agrees with the xlsx area of raw_data column F to within 0.0001 percent, mean 0.0001 percent; with k = 1 the largest difference would be 0.0098 percent.
* **Blank fields** of `Building`, `Zone`, `People`, `Lights`, `ElectricEquipment` and `ZoneInfiltration:DesignFlowRate` (radiant fractions, terrain, North axis, coefficients) use the EnergyPlus defaults and are not written.
* **No other prototype data** (curves, fans, coils, nodes, meters, outputs, service water heating, exterior lights, ground temperatures, Timestep).

## 6. Notes

**The walls and the roofs of this Short IDF do not represent the real building.**

* Neither the xlsx nor the PDF gives a U-value for the metal building wall and roof. The xlsx names the construction type only (Metal Building Wall, Metal Building Roof); the PDF tables for the roof (Table 19, insulation above deck or attic), the steel frame wall (Table 20) and the mass wall (Table 21) have no metal building column.
* EnergyPlus needs a construction, so every wall and roof uses the one layer of 0.2 m2-K/W. The prototype constructions of the same surfaces have 1.17 to 1.29 m2-K/W (walls) and 1.68 to 2.57 m2-K/W (roofs), so the walls and roofs here are about 6 to 13 times less resistant than the prototype, and without thermal mass.
* **Do not compare the energy results of this Short IDF with the full IDF or with a measured or published value.** The run only has to complete with 0 Severe and 0 Fatal. For results use the full IDF of this building, which keeps the prototype constructions.
* If the results of the Short IDF are ever to be compared, the walls and the roofs must first be given the prototype constructions, each marked as a prototype value that is not in the documents.
