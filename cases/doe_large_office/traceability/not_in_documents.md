# Values of the Short IDF that the documents do not give: DOE Large Office

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

The PDF (Appendix B, Table B-4, hourly operation schedules) has SummerDesign and WinterDesign rows for this building. They are **not used**: the schedules of the PDF are not the schedules of the xlsx. Compared for the Small Office and the Medium Office, the Monday-Friday values of the PDF differ from the xlsx in 14 of the 15 schedules, and only 4 of 14 (Small Office) and 8 of 16 (Medium Office) design-day clauses of the prototype equal the PDF rows. Taking some design days from the PDF would put two versions of a schedule into one object, and the xlsx is the primary document.

## 2. Constructions and ground constants

* **`GenericLayer`** (construction `GenericSurface`): thermal resistance 0.2 m2-K/W, **assumed**. EnergyPlus needs a construction for every surface; the documents describe only the exterior walls, the roof and the windows. Used by: 11 ceilings (boundary condition Surface); 18 ceilings (boundary condition Zone); 2 floors (boundary condition Adiabatic); 21 floors (boundary condition Surface); 68 walls (boundary condition Surface).
* **`Construction:CfactorUndergroundWall`** x 6: C-factor 6.47292 W/m2-K, height 2.439 m. Derived like the F-factor (uninsulated basement wall of 90.1-2004); the documents give no basement wall construction. The height is the vertical extent of the wall polygons (see the comment of the field).
* **Windows:** only `WindowMaterial:SimpleGlazingSystem` (U and SHGC from the PDF); no frame, no divider.

## 3. Schedules

Given by the PDF but not by the xlsx:

* `ACTIVITY_SCH` = 120 for all 24 hours (NREL PDF Table B-4, p.78 (page 89 of the file): ACTIVITY_SCH, All, 120 for all 24 hours.)

Not in the documents:

* `AlwaysOn` = 1 for all hours
* `AlwaysOff` = 0 for all hours

## 4. HVACTemplate values written without a document source

| Object | Field | Value (count) | Note |
|---|---|---|---|
| `HVACTemplate:System:VAV` | Economizer Type | NoEconomizer (3) | same as the EnergyPlus default |
| `HVACTemplate:System:ConstantVolume` | Economizer Type | NoEconomizer | same as the EnergyPlus default |
| `HVACTemplate:Zone:ConstantVolume` | Outdoor Air Method | Flow/Zone | how the template reads the outdoor air value of the xlsx (per zone or per floor area) |
| `HVACTemplate:Zone:VAV` | Outdoor Air Method | Flow/Area (15) | how the template reads the outdoor air value of the xlsx (per zone or per floor area) |
| `HVACTemplate:Zone:WaterToAirHeatPump` | Outdoor Air Method | Flow/Zone (4) | how the template reads the outdoor air value of the xlsx (per zone or per floor area) |
| `HVACTemplate:Plant:ChilledWaterLoop` | Condenser Water Temperature Control Type | OutdoorWetBulbTemperature | a choice that the template needs |
| `HVACTemplate:Plant:Chiller` | Chiller Type | ElectricCentrifugalChiller | a choice that the template needs |
| `HVACTemplate:Plant:Chiller` | Nominal COP | 5.5 | a choice that the template needs |
| `HVACTemplate:Plant:Tower` | Tower Type | SingleSpeed | a choice that the template needs |
| `HVACTemplate:Plant:Tower` | Template Plant Loop Type | ChilledWater, MixedWater | a choice that the template needs |
| `HVACTemplate:Plant:Boiler` | Boiler Type | HotWaterBoiler (2) | a choice that the template needs |
| `HVACTemplate:Plant:Boiler` | Template Plant Loop Type | HotWater, MixedWater | a choice that the template needs |

Every other field of the HVACTemplate objects is blank: EnergyPlus uses its default or autosizes it (fan and coil capacities, flow rates, efficiencies, minimum flow fractions). The documents give the system type of each zone, the outdoor air, the availability and the set point schedules.

## 5. Geometry and other blanks

* **Vertex coordinates** (23 zones, 151 surfaces, 24 windows and doors; 23 zones have a non-zero origin): the documents give areas and building dimensions only. The polygons are kept from the prototype; the comments show how each coordinate follows from the dimensions.
* **Scale factor k = 1.0002455:** the coordinates are written as feet x 0.3048 x k. k is not a quantity of the prototype IDF either: the prototype has only the coordinates in metres, and k is a factor fitted here to describe them. k is not written in the documents; it is fitted: it makes 12 of the 22 distinct non-zero wall coordinates a whole number of feet within 0.5 mm. The check against the documents: with this k the horizontal area of each of the 23 zones agrees with the xlsx area of raw_data column F to within 0.0076 percent, mean 0.0018 percent; with k = 1 the largest difference would be 0.0515 percent.
* **Blank fields** of `Building`, `Zone`, `People`, `Lights`, `ElectricEquipment` and `ZoneInfiltration:DesignFlowRate` (radiant fractions, terrain, North axis, coefficients) use the EnergyPlus defaults and are not written.
* **No other prototype data** (curves, fans, coils, nodes, meters, outputs, service water heating, exterior lights, ground temperatures, Timestep).
