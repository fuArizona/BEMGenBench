# Appendix (natural language): Residence test 6, iUnit (Denver, CO)

Target IDF: `Residence/test6/iUnit.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that cannot be written in words, with the values of the documents replaced by markers). Documents: `orig/iunit_epc_inputs.xlsx` (the only document). Section 1 describes the geometry; the following sections give every field of the object classes that `Appendix_IDF.txt` leaves out, so that the IDF can be rebuilt from the documents and these two files.

## 1. Geometry in words

* **Shape and zoning.** One thermal zone, `Zone1`, a rectangular box with a flat roof: floor area 35.113 m2 (roof area of xlsx G52), ceiling height H = 2.743 m (xlsx C9, 9 ft), volume 96.3 m3. No attic, no basement, no second storey.
* **Dimensions.** The east and west walls are L = wall area / H = 22.57 m2 / 2.743 m = 8.228 m long (xlsx G46, G50); the south and north walls are W = roof area / L = 35.113 m2 / 8.228 m = 4.267 m wide (xlsx G52). The walls therefore have the areas 11.71 m2 (south, north) and 22.57 m2 (east, west), 68.6 m2 in total. Origin at the south-west corner of the floor, X to the east, Y to the north, Z up, `Building` north axis 0, world coordinates; the vertices are listed counter-clockwise seen from outside: floor (0, 0, 0) (0, 8.228, 0) (4.267, 8.228, 0) (4.267, 0, 0), roof at z = 2.743 m.
* **Surfaces.** 6 building surfaces: 1 floor (boundary Ground, `Floor`), 1 roof (Outdoors, `Roof`), 4 exterior walls (Outdoors, `Exterior Wall`: South, East, North, West). The documents give no orientation other than the window on the south wall, so the box is aligned with the compass (ASSUMED). The roof and floor areas are equal (35.1 m2).
* **Window.** One window of 4.2 m2 (xlsx I44) in the south wall, 3.0 m wide x 1.4 m high, centred in the wall (x = 0.634 to 3.634 m), sill 0.6 m (z = 0.6 to 2.0 m); the shape and the position are ASSUMED (the xlsx gives only the area). The window / south wall ratio is 35.9 %, window / all exterior walls 6.1 %. No door, no shading object.
* **Build-up and internal mass.** Walls and floor: `Wall Insulation` (no-mass layer, R = 3.93 m2K/W); roof: `Roof Insulation` (R = 16.20 m2K/W); window: simple glazing (U = 1.265 W/m2K, SHGC = 0.40). The zone has one internal mass of 62.1555 m2 (100 mm layer, `Mass Construction`) that is not drawn as surfaces. Tables of all values are in section 3.

Computed from the IDF: 1 zone(s), 6 building surfaces (1 floor (ground), 1 roof (outdoors), 4 wall (outdoors)) and 1 openings. Coordinates in metres; bounding box of all vertices: x = 0.00 to 4.27, y = 0.00 to 8.23, z = 0.00 to 2.74 m. The vertex coordinates, each with its formula, are in `Appendix_IDF.txt`.

| Zone | Multiplier | x range m | y range m | z range m | Floor polygon area m2 |
|---|---|---|---|---|---|
| Zone1 | 1 | 0.00 to 4.27 | 0.00 to 8.23 | 0.00 to 2.74 | 35.1 |

| Surface type | Construction | Boundary condition | Count | Total area m2 |
|---|---|---|---|---|
| Floor | Floor | Ground | 1 | 35.1 |
| Roof | Roof | Outdoors | 1 | 35.1 |
| Wall | Exterior Wall | Outdoors | 4 | 68.6 |

| Opening type | Construction | Count | Total area m2 |
|---|---|---|---|
| Window | South Window | 1 | 4.20 |

Building North Axis = 0 degrees; the directions below are the compass directions of the outward normals (y axis = north when the axis is 0).

Zone summary (volume = floor polygon area x height of the bounding box of the zone, an upper bound for a zone with a pitched roof):

| Zone | Floor area m2 | Height m | Volume m3 | Surfaces | Envelope area (outdoors + ground) m2 | Exterior wall area m2 | Opening area m2 | Opening / wall |
|---|---|---|---|---|---|---|---|---|
| Zone1 | 35.1 | 2.74 | 96.3 | 6 | 138.8 | 68.6 | 4.20 | 6.1 % |

Exterior walls and their openings by direction (gross wall area; an opening is counted in the wall it sits in):

| Direction | Wall surfaces | Gross wall area m2 | Window area m2 | Door / glass door area m2 | Window / gross wall |
|---|---|---|---|---|---|
| N | 1 | 11.7 | 0.00 | 0.00 | 0.0 % |
| E | 1 | 22.6 | 0.00 | 0.00 | 0.0 % |
| S | 1 | 11.7 | 4.20 | 0.00 | 35.9 % |
| W | 1 | 22.6 | 0.00 | 0.00 | 0.0 % |

| Roof surface | Zone | Area m2 | Tilt deg | Faces |
|---|---|---|---|---|
| Roof | Zone1 | 35.1 | 0.0 | flat |

All building surfaces (tilt 0 = faces up, 90 = vertical, 180 = faces down):

| Surface | Type | Construction | Zone | Boundary | Vertices | Area m2 | Tilt deg | Direction |
|---|---|---|---|---|---|---|---|---|
| Floor | Floor | Floor | Zone1 | Ground | 4 | 35.11 | 180 | - |
| Roof | Roof | Roof | Zone1 | Outdoors | 4 | 35.11 | 0 | - |
| South Wall | Wall | Exterior Wall | Zone1 | Outdoors | 4 | 11.71 | 90 | S |
| East Wall | Wall | Exterior Wall | Zone1 | Outdoors | 4 | 22.57 | 90 | E |
| North Wall | Wall | Exterior Wall | Zone1 | Outdoors | 4 | 11.71 | 90 | N |
| West Wall | Wall | Exterior Wall | Zone1 | Outdoors | 4 | 22.57 | 90 | W |

Vertex coordinates in metres (as in the IDF; the formula of each coordinate is in `Appendix_IDF.txt`):

| Surface / opening | Vertices (x, y, z) |
|---|---|
| Floor | (0, 0, 0); (0, 8.228, 0); (4.267, 8.228, 0); (4.267, 0, 0) |
| Roof | (0, 0, 2.743); (4.267, 0, 2.743); (4.267, 8.228, 2.743); (0, 8.228, 2.743) |
| South Wall | (0, 0, 2.743); (0, 0, 0); (4.267, 0, 0); (4.267, 0, 2.743) |
| East Wall | (4.267, 0, 2.743); (4.267, 0, 0); (4.267, 8.228, 0); (4.267, 8.228, 2.743) |
| North Wall | (4.267, 8.228, 2.743); (4.267, 8.228, 0); (0, 8.228, 0); (0, 8.228, 2.743) |
| West Wall | (0, 8.228, 2.743); (0, 8.228, 0); (0, 0, 0); (0, 0, 2.743) |
| South Window | (0.6337, 0, 2); (0.6337, 0, 0.6); (3.634, 0, 0.6); (3.634, 0, 2) |

Opening sizes (width = the longer horizontal extent of the polygon, height = z extent, sill = lowest z):

| Opening | Type | In surface | Direction | Width m | Height m | Sill m | Area m2 |
|---|---|---|---|---|---|---|---|
| South Window | Window | South Wall | S | 3.000 | 1.400 | 0.600 | 4.20 |

## 2. Settings, sizing periods and constant schedules (not in the documents)

These objects are required by EnergyPlus or are modelling choices; the documents do not give them.

`Version` (1 object)

| Version Identifier |
|---|
| 23.1 |

`SimulationControl` (1 object)

| Do Zone Sizing Calculation | Do System Sizing Calculation | Run Simulation for Sizing Periods |
|---|---|---|
| Yes | Yes | No |

`Timestep` (1 object)

| Number of Timesteps per Hour |
|---|
| 6 |

`RunPeriod` (1 object)

| Name | Begin Month | Begin Day of Month | End Month | End Day of Month |
|---|---|---|---|---|
| Run Period Annual | 1 | 1 | 12 | 31 |

`GlobalGeometryRules` (1 object)

| Starting Vertex Position | Vertex Entry Direction | Coordinate System |
|---|---|---|
| UpperLeftCorner | Counterclockwise | World |

`Schedule:Constant` (3 objects)

| Name | Hourly Value |
|---|---|
| Always On | 1 |
| Activity Level Sched | 70 |
| DHW Setpoint Sched | 55 |

`SizingPeriod:DesignDay` (2 objects)

| Field | Denver Intl Ap Ann Htg 99.6% Condns DB | Denver Intl Ap Ann Clg .4% Condns DB=>MWB |
|---|---|---|
| Name | Denver Intl Ap Ann Htg 99.6% Condns DB | Denver Intl Ap Ann Clg .4% Condns DB=>MWB |
| Month | 12 | 7 |
| Day of Month | 21 | 21 |
| Day Type | WinterDesignDay | SummerDesignDay |
| Maximum Dry-Bulb Temperature | -17.4 | 34.6 |
| Daily Dry-Bulb Temperature Range | 0.0 | 15.2 |
| Dry-Bulb Temperature Range Modifier Type | DefaultMultipliers | DefaultMultipliers |
| Humidity Condition Type | Wetbulb | Wetbulb |
| Wetbulb at Maximum Dry-Bulb | -17.4 | 15.7 |
| Barometric Pressure | 83011. | 83011. |
| Wind Speed | 3.3 | 4.2 |
| Wind Direction | 160 | 80 |
| Rain | No | No |
| Snow on ground | No | No |
| Daylight Savings Time Indicator | No | No |
| Solar Model Indicator | ASHRAEClearSky | ASHRAETau |
| Clearness | 0.00 |  |
| ASHRAE Clear Sky Optical Depth for Beam Irradiance (taub) |  | 0.424 |
| ASHRAE Clear Sky Optical Depth for Diffuse Irradiance (taud) |  | 2.012 |

`Site:GroundTemperature:BuildingSurface` (1 object)

| Field | #1 |
|---|---|
| January Ground Temperature | 3.08 |
| February Ground Temperature | 3.56 |
| March Ground Temperature | 5.74 |
| April Ground Temperature | 8.18 |
| May Ground Temperature | 13.45 |
| June Ground Temperature | 16.83 |
| July Ground Temperature | 18.51 |
| August Ground Temperature | 18.13 |
| September Ground Temperature | 15.72 |
| October Ground Temperature | 12.07 |
| November Ground Temperature | 7.97 |
| December Ground Temperature | 4.74 |

`FuelFactors` (3 objects)

| Existing Fuel Resource Name | Source Energy Factor | CO2 Emission Factor |
|---|---|---|
| Electricity | 2.5 | 111.1111 |
| NaturalGas | 1.1 | 55.5556 |
| FuelOilNo1 | 1.2 | 69.4444 |

`UtilityCost:Tariff` (1 object)

| Name | Output Meter Name | Conversion Factor Choice |
|---|---|---|
| Electricity Flat | Electricity:Facility | kWh |

`UtilityCost:Charge:Simple` (1 object)

| Name | Tariff Name | Source Variable | Season | Category Variable Name | Cost per Unit |
|---|---|---|---|---|---|
| FlatEnergyCharge | Electricity Flat | totalEnergy | Annual | EnergyCharges | 0.12 |

## 3. Materials, constructions, glazing and internal mass

The layer thicknesses and the values that the documents give are marked in the comments of the IDF ("Source:"); the other values (conductivity, density, specific heat, absorptances, roughness) are assumptions that EnergyPlus needs.

`Material` (1 object)

| Name | Roughness | Thickness | Conductivity | Density | Specific Heat |
|---|---|---|---|---|---|
| Mass Layer | Rough | 0.1 | 1.0 | 1000 | 1000 |

`Material:NoMass` (2 objects)

| Name | Roughness | Thermal Resistance | Thermal Absorptance | Solar Absorptance |
|---|---|---|---|---|
| Wall Insulation | MediumSmooth | 3.9284 | 0.9 | 0.5 |
| Roof Insulation | MediumSmooth | 16.1966 | 0.9 | 0.5 |

`Construction` (5 objects)

| Name | Outside Layer |
|---|---|
| Exterior Wall | Wall Insulation |
| Roof | Roof Insulation |
| Floor | Wall Insulation |
| South Window | Window1 Glazing |
| Mass Construction | Mass Layer |

`WindowMaterial:SimpleGlazingSystem` (1 object)

| Name | U-Factor | Solar Heat Gain Coefficient |
|---|---|---|
| Window1 Glazing | 1.265 | 0.4 |

`InternalMass` (1 object)

| Name | Construction Name | Zone or ZoneList Name | Surface Area |
|---|---|---|---|
| Zone1 Internal Mass | Mass Construction | Zone1 | 62.1555 |

## 4. Performance curves (not in the documents)

EnergyPlus default curves of the HVAC objects.

`Curve:Quadratic` (5 objects)

| Name | Coefficient1 Constant | Coefficient2 x | Coefficient3 x**2 | Minimum Value of x | Maximum Value of x |
|---|---|---|---|---|---|
| Zone1 PTHP Cooling Coil Cap-FF | 0.8 | 0.2 | 0 | 0.5 | 1.5 |
| Zone1 PTHP Cooling Coil EIR-FF | 1.1552 | -0.1808 | 0.0256 | 0.5 | 1.5 |
| Zone1 PTHP Cooling Coil Coil PLF | 0.678947 | 0.3 | 0.0210526 | 0.1 | 1 |
| Zone1 PTHP Heating Coil EIR-FF | 1.3824 | -0.4336 | 0.0512 | 0.0 | 1.0 |
| Zone1 PTHP Heating Coil PLF | 0.75 | 0.25 | 0.0 | 0.0 | 1.0 |

`Curve:Biquadratic` (3 objects)

| Field | Zone1 PTHP Cooling Coil Cap-FT | Zone1 PTHP Cooling Coil EIR-FT | Zone1 PTHP Heating Coil DefrEIR-FT |
|---|---|---|---|
| Name | Zone1 PTHP Cooling Coil Cap-FT | Zone1 PTHP Cooling Coil EIR-FT | Zone1 PTHP Heating Coil DefrEIR-FT |
| Coefficient1 Constant | 0.942587793 | 0.342414409 | 1 |
| Coefficient2 x | 0.009543347 | 0.034885008 | 0 |
| Coefficient3 x**2 | 0.00068377 | -0.0006237 | 0 |
| Coefficient4 y | -0.011042676 | 0.004977216 | 0 |
| Coefficient5 y**2 | 0.000005249 | 0.000437951 | 0 |
| Coefficient6 x*y | -0.00000972 | -0.000728028 | 0 |
| Minimum Value of x | 12.77778 | 12.77778 | 0 |
| Maximum Value of x | 23.88889 | 23.88889 | 50 |
| Minimum Value of y | 18.0 | 18.0 | 0 |
| Maximum Value of y | 46.11111 | 46.11111 | 50 |

`Curve:Cubic` (3 objects)

| Name | Coefficient1 Constant | Coefficient2 x | Coefficient3 x**2 | Coefficient4 x**3 | Minimum Value of x | Maximum Value of x |
|---|---|---|---|---|---|---|
| Zone1 PTHP Heating Coil Cap-FT | 0.758746 | 0.027626 | 0.000148716 | 0.0000034992 | -20.0 | 20.0 |
| Zone1 PTHP Heating Coil Cap-FF | 0.84 | 0.16 | 0.0 | 0.0 | 0.5 | 1.5 |
| Zone1 PTHP Heating Coil EIR-FT | 1.19248 | -0.0300438 | 0.00103745 | -0.000023328 | -20.0 | 20.0 |

## 5. Output requests (not in the documents)

`Output:Variable` (3 objects)

| Key Value | Variable Name | Reporting Frequency |
|---|---|---|
| * | Zone Mean Air Temperature | Hourly |
| * | Zone Air System Sensible Heating Energy | Hourly |
| * | Zone Air System Sensible Cooling Energy | Hourly |

`Output:Meter` (1 object)

| Key Name | Reporting Frequency |
|---|---|
| Electricity:Facility | Monthly |

`Output:Table:SummaryReports` (1 object)

| Report 1 Name |
|---|
| AllSummary |
