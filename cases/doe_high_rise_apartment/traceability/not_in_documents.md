# Values of the Short IDF that the documents do not give: DOE High-rise Apartment

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

No document gives design days: the day types SummerDesignDay and WinterDesignDay are not written; sizing uses the Monday-based sizing days of the weather file.

## 2. Constructions and ground constants

* **`GenericLayer`** (construction `GenericSurface`): thermal resistance 0.2 m2-K/W, **assumed**. EnergyPlus needs a construction for every surface; the documents describe only the exterior walls, the roof and the windows. Used by: 18 ceilings (boundary condition Surface); 18 floors (boundary condition Surface); 42 walls (boundary condition Zone).
* **`Construction:FfactorGroundFloor`** x 9: F-factor 1.26363 W/m-K. The PDF (Table 22) gives no slab insulation (NR); this is the 90.1-2004 value of an uninsulated slab, so it is derived, not given. The area is the area of the floor polygon of each zone and the exposed perimeter is the sum of the bottom edges of the exterior walls that stand on that floor; both are computed from the polygons of the IDF, and the comment of each field shows the calculation.
* **Windows:** only `WindowMaterial:SimpleGlazingSystem` (U and SHGC from the PDF); no frame, no divider.

## 3. Schedules

Not in the documents:

* `AlwaysOn` = 1 for all hours
* `ACTIVITY_SCH` = 95 for all hours; Not in the documents: the prototype value 95 (the PDF has no schedule table for the high-rise apartment); EnergyPlus needs an activity level for People.

## 4. HVACTemplate values written without a document source

| Object | Field | Value (count) | Note |
|---|---|---|---|
| `HVACTemplate:Zone:WaterToAirHeatPump` | Outdoor Air Method | Flow/Zone (24) | how the template reads the outdoor air value of the xlsx (per zone or per floor area) |
| `HVACTemplate:Plant:Boiler` | Boiler Type | HotWaterBoiler | a choice that the template needs |

Every other field of the HVACTemplate objects is blank: EnergyPlus uses its default or autosizes it (fan and coil capacities, flow rates, efficiencies, minimum flow fractions). The documents give the system type of each zone, the outdoor air, the availability and the set point schedules.

## 5. Geometry and other blanks

* **Vertex coordinates** (27 zones, 138 surfaces, 42 windows and doors; 27 zones have a non-zero origin): the documents give areas and building dimensions only. The polygons are kept from the prototype; the comments show how each coordinate follows from the dimensions.
* **Scale factor k = 0.9999610:** the coordinates are written as feet x 0.3048 x k. k is not a quantity of the prototype IDF either: the prototype has only the coordinates in metres, and k is a factor fitted here to describe them. k is not written in the documents; it is fitted: it makes 4 of the 5 distinct non-zero wall coordinates a whole number of feet within 0.5 mm. The check against the documents: with this k the horizontal area of each of the 27 zones agrees with the xlsx area of raw_data column F to within 0.0020 percent, mean 0.0015 percent; with k = 1 the largest difference would be 0.0063 percent.
* **Blank fields** of `Building`, `Zone`, `People`, `Lights`, `ElectricEquipment` and `ZoneInfiltration:DesignFlowRate` (radiant fractions, terrain, North axis, coefficients) use the EnergyPlus defaults and are not written.
* **No other prototype data** (curves, fans, coils, nodes, meters, outputs, service water heating, exterior lights, ground temperatures, Timestep).
