# Appendix (natural language): Residence test 10, NIST Net-Zero Energy Residential Test Facility (Gaithersburg, MD)

Target IDF: `Residence/test10/NZERTF.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that cannot be written in words, with the values of the documents replaced by markers). Documents: `orig/nzertf-inputs.xlsx`. Section 1 describes the geometry; the following sections give every field of the object classes that `Appendix_IDF.txt` leaves out, so that the IDF can be rebuilt from the documents and these two files.

## 1. Geometry in words

* **Shape and zoning.** One zone, `Conditioned Zone`, for the whole house: a basement and two floors above ground (the NIST net-zero-energy house is one air volume in the model) with a gable roof. Footprint a x b = 1454 ft2 = 135.081 m2 (xlsx C29) and perimeter 2 (a + b) = 165 ft (C31), so a = (P / 2 + sqrt((P / 2)^2 - 4 A)) / 2 = 17.369 m (long side, east-west) and b = P / 2 - a = 7.777 m (north-south).
* **Coordinates and orientation.** Origin at the south-west corner of the basement floor, X to the east, Y to the north, Z up; `Building` north axis 0, so the long walls face south and north (ASSUMED: the xlsx gives no orientation of the footprint); world coordinates, counter-clockwise seen from outside. Basement slab (0, 0, 0) (0, 7.777, 0) (17.369, 7.777, 0) (17.369, 0, 0).
* **Heights.** Basement 8 ft = 2.438 m (C42), first and second floor 9 ft each (C52, C63): the eave is at 26 ft = 7.925 m (the floor structure between the storeys is not modelled as a thickness). The roof slope is 2:12 (C244, 9.5 degrees); the ridge runs east-west over the middle at y = b / 2 = 3.889 m and z = 7.925 + 3.889 x 2 / 12 = 8.573 m.
* **Surfaces (11).** Basement slab (Ground, 135.1 m2); four foundation walls z = 0 to 2.438 m (Ground, `Foundation Wall`: South and North 42.4 m2, East and West 19.0 m2, 122.6 m2 in total); four exterior walls z = 2.438 to 7.925 m (Outdoors, `Exterior Wall`: South and North rectangles of 95.3 m2, East and West 45.2 m2 each as pentagons whose fifth vertex is the gable peak (17.369 or 0, 3.889, 8.573); 281.0 m2 in total); two roof planes `Roof South` and `Roof North` of 68.5 m2 each (136.9 m2) with the eave at z = 7.925 m and the ridge at z = 8.573 m. There is no separate floor between the storeys and no interior wall.
* **Openings (5).** One window per face, area = 0.13 x gross wall (C254 to C257) with the aspect ratio width / height = 1.333 (C258), centred in the wall height z = 2.438 to 7.925 m (centre z = 5.18 m; ASSUMED): west 2.798 x 2.099 m (5.87 m2) centred at y = 3.889 m, east the same, north 4.064 x 3.048 m (12.39 m2) centred at x = 8.685 m, south the same but starting at x = 9.653 m so that it does not overlap the door (ASSUMED). One door 1.83 x 2.03 m (3.71 m2; C268) in the south wall from x = 1.50 to 3.33 m, sill at z = 2.438 m (ASSUMED position: it is at the first-floor level, there is no stair or porch). Window area 36.52 m2 (13 % of the gross wall), door 3.71 m2. No shading object.
* **Build-up (no-mass layers from the xlsx).** Exterior wall R = 7.78 m2K/W, roof R = 12.54 m2K/W, foundation wall R = 4.1 m2K/W, slab R = 1.8 m2K/W, door R = 0.625 m2K/W, window U = 1.136 W/m2K with SHGC 0.25 and visible transmittance 0.40. The surfaces of the basement have the boundary condition Ground.

Computed from the IDF: 1 zone(s), 11 building surfaces (1 floor (ground), 2 roof (outdoors), 4 wall (ground), 4 wall (outdoors)) and 5 openings. Coordinates in metres; bounding box of all vertices: x = 0.00 to 17.37, y = 0.00 to 7.78, z = 0.00 to 8.57 m. The vertex coordinates, each with its formula, are in `Appendix_IDF.txt`.

| Zone | Multiplier | x range m | y range m | z range m | Floor polygon area m2 |
|---|---|---|---|---|---|
| Conditioned Zone | 1 | 0.00 to 17.37 | 0.00 to 7.78 | 0.00 to 8.57 | 135.1 |

| Surface type | Construction | Boundary condition | Count | Total area m2 |
|---|---|---|---|---|
| Floor | Slab | Ground | 1 | 135.1 |
| Wall | Foundation Wall | Ground | 4 | 122.6 |
| Wall | Exterior Wall | Outdoors | 4 | 281.0 |
| Roof | Roof | Outdoors | 2 | 136.9 |

| Opening type | Construction | Count | Total area m2 |
|---|---|---|---|
| Window | Window | 4 | 36.52 |
| Door | Door | 1 | 3.71 |

Building North Axis = 0 degrees; the directions below are the compass directions of the outward normals (y axis = north when the axis is 0).

Zone summary (volume = floor polygon area x height of the bounding box of the zone, an upper bound for a zone with a pitched roof):

| Zone | Floor area m2 | Height m | Volume m3 | Surfaces | Envelope area (outdoors + ground) m2 | Exterior wall area m2 | Opening area m2 | Opening / wall |
|---|---|---|---|---|---|---|---|---|
| Conditioned Zone | 135.1 | 8.57 | 1158.0 | 11 | 675.6 | 281.0 | 40.24 | 14.3 % |

Exterior walls and their openings by direction (gross wall area; an opening is counted in the wall it sits in):

| Direction | Wall surfaces | Gross wall area m2 | Window area m2 | Door / glass door area m2 | Window / gross wall |
|---|---|---|---|---|---|
| N | 1 | 95.3 | 12.39 | 0.00 | 13.0 % |
| E | 1 | 45.2 | 5.87 | 0.00 | 13.0 % |
| S | 1 | 95.3 | 12.39 | 3.71 | 13.0 % |
| W | 1 | 45.2 | 5.87 | 0.00 | 13.0 % |

| Roof surface | Zone | Area m2 | Tilt deg | Faces |
|---|---|---|---|---|
| Roof South | Conditioned Zone | 68.5 | 9.5 | S |
| Roof North | Conditioned Zone | 68.5 | 9.5 | N |

All building surfaces (tilt 0 = faces up, 90 = vertical, 180 = faces down):

| Surface | Type | Construction | Zone | Boundary | Vertices | Area m2 | Tilt deg | Direction |
|---|---|---|---|---|---|---|---|---|
| Basement Slab | Floor | Slab | Conditioned Zone | Ground | 4 | 135.08 | 180 | - |
| Foundation Wall South | Wall | Foundation Wall | Conditioned Zone | Ground | 4 | 42.35 | 90 | S |
| Foundation Wall East | Wall | Foundation Wall | Conditioned Zone | Ground | 4 | 18.96 | 90 | E |
| Foundation Wall North | Wall | Foundation Wall | Conditioned Zone | Ground | 4 | 42.35 | 90 | N |
| Foundation Wall West | Wall | Foundation Wall | Conditioned Zone | Ground | 4 | 18.96 | 90 | W |
| Wall South | Wall | Exterior Wall | Conditioned Zone | Outdoors | 4 | 95.29 | 90 | S |
| Wall East | Wall | Exterior Wall | Conditioned Zone | Outdoors | 5 | 45.19 | 90 | E |
| Wall North | Wall | Exterior Wall | Conditioned Zone | Outdoors | 4 | 95.29 | 90 | N |
| Wall West | Wall | Exterior Wall | Conditioned Zone | Outdoors | 5 | 45.19 | 90 | W |
| Roof South | Roof | Roof | Conditioned Zone | Outdoors | 4 | 68.47 | 9 | S |
| Roof North | Roof | Roof | Conditioned Zone | Outdoors | 4 | 68.47 | 9 | N |

Vertex coordinates in metres (as in the IDF; the formula of each coordinate is in `Appendix_IDF.txt`):

| Surface / opening | Vertices (x, y, z) |
|---|---|
| Basement Slab | (0, 0, 0); (0, 7.777, 0); (17.37, 7.777, 0); (17.37, 0, 0) |
| Foundation Wall South | (0, 0, 2.438); (0, 0, 0); (17.37, 0, 0); (17.37, 0, 2.438) |
| Foundation Wall East | (17.37, 0, 2.438); (17.37, 0, 0); (17.37, 7.777, 0); (17.37, 7.777, 2.438) |
| Foundation Wall North | (17.37, 7.777, 2.438); (17.37, 7.777, 0); (0, 7.777, 0); (0, 7.777, 2.438) |
| Foundation Wall West | (0, 7.777, 2.438); (0, 7.777, 0); (0, 0, 0); (0, 0, 2.438) |
| Wall South | (0, 0, 7.925); (0, 0, 2.438); (17.37, 0, 2.438); (17.37, 0, 7.925) |
| Wall East | (17.37, 0, 7.925); (17.37, 0, 2.438); (17.37, 7.777, 2.438); (17.37, 7.777, 7.925); (17.37, 3.889, 8.573) |
| Wall North | (17.37, 7.777, 7.925); (17.37, 7.777, 2.438); (0, 7.777, 2.438); (0, 7.777, 7.925) |
| Wall West | (0, 7.777, 7.925); (0, 7.777, 2.438); (0, 0, 2.438); (0, 0, 7.925); (0, 3.889, 8.573) |
| Roof South | (0, 3.889, 8.573); (0, 0, 7.925); (17.37, 0, 7.925); (17.37, 3.889, 8.573) |
| Roof North | (17.37, 3.889, 8.573); (17.37, 7.777, 7.925); (0, 7.777, 7.925); (0, 3.889, 8.573) |
| Window1 | (0, 5.288, 6.231); (0, 5.288, 4.132); (0, 2.489, 4.132); (0, 2.489, 6.231) |
| Window2 | (10.72, 7.777, 6.706); (10.72, 7.777, 3.657); (6.653, 7.777, 3.657); (6.653, 7.777, 6.706) |
| Window3 | (17.37, 2.489, 6.231); (17.37, 2.489, 4.132); (17.37, 5.288, 4.132); (17.37, 5.288, 6.231) |
| Window4 | (9.653, 0, 6.706); (9.653, 0, 3.657); (13.72, 0, 3.657); (13.72, 0, 6.706) |
| Door1 | (1.5, 0, 4.468); (1.5, 0, 2.438); (3.33, 0, 2.438); (3.33, 0, 4.468) |

Opening sizes (width = the longer horizontal extent of the polygon, height = z extent, sill = lowest z):

| Opening | Type | In surface | Direction | Width m | Height m | Sill m | Area m2 |
|---|---|---|---|---|---|---|---|
| Window1 | Window | Wall West | W | 2.798 | 2.099 | 4.132 | 5.87 |
| Window2 | Window | Wall North | N | 4.064 | 3.048 | 3.657 | 12.39 |
| Window3 | Window | Wall East | E | 2.798 | 2.099 | 4.132 | 5.87 |
| Window4 | Window | Wall South | S | 4.064 | 3.048 | 3.657 | 12.39 |
| Door1 | Door | Wall South | S | 1.830 | 2.030 | 2.438 | 3.71 |

## 2. Settings, sizing periods and constant schedules (not in the documents)

These objects are required by EnergyPlus or are modelling choices; the documents do not give them.

`Version` (1 object)

| Version Identifier |
|---|
| 23.1 |

`SimulationControl` (1 object)

| Do Zone Sizing Calculation | Do System Sizing Calculation | Do Plant Sizing Calculation | Run Simulation for Sizing Periods | Run Simulation for Weather File Run Periods |
|---|---|---|---|---|
| Yes | Yes | No | No | Yes |

`Timestep` (1 object)

| Number of Timesteps per Hour |
|---|
| 60 |

`RunPeriod` (1 object)

| Field | Annual |
|---|---|
| Name | Annual |
| Begin Month | 1 |
| Begin Day of Month | 1 |
| Begin Year | 2012 |
| End Month | 12 |
| End Day of Month | 31 |
| End Year | 2012 |
| Day of Week for Start Day | Sunday |
| Use Weather File Holidays and Special Days | Yes |
| Use Weather File Daylight Saving Period | No |
| Apply Weekend Holiday Rule | No |
| Use Weather File Rain Indicators | Yes |
| Use Weather File Snow Indicators | Yes |

`RunPeriodControl:DaylightSavingTime` (1 object)

| Start Date | End Date |
|---|---|
| 3/12 | 11/5 |

`GlobalGeometryRules` (1 object)

| Starting Vertex Position | Vertex Entry Direction | Coordinate System |
|---|---|---|
| UpperLeftCorner | Counterclockwise | World |

`Schedule:Constant` (7 objects)

| Name | Hourly Value |
|---|---|
| Always On | 1 |
| Occupancy Sched | 1 |
| Activity Level Sched | 120 |
| Appliance Sched | 1 |
| DHW Setpoint Sched | 57.5 |
| Dehumidifying RH Setpoint Sched | 60 |
| Humidifying RH Setpoint Sched | 0 |

`SizingPeriod:DesignDay` (2 objects)

| Field | Gaithersburg-Montgomery.Count Ann Htg 99.6% Condns DB | Gaithersburg-Montgomery.Count Ann Clg .4% Condns DB=>MWB |
|---|---|---|
| Name | Gaithersburg-Montgomery.Count Ann Htg 99.6% Condns DB | Gaithersburg-Montgomery.Count Ann Clg .4% Condns DB=>MWB |
| Month | 1 | 7 |
| Day of Month | 21 | 21 |
| Day Type | WinterDesignDay | SummerDesignDay |
| Maximum Dry-Bulb Temperature | -11.5 | 33.2 |
| Daily Dry-Bulb Temperature Range | 0.0 | 12.4 |
| Dry-Bulb Temperature Range Modifier Type | DefaultMultipliers | DefaultMultipliers |
| Humidity Condition Type | Wetbulb | Wetbulb |
| Wetbulb at Maximum Dry-Bulb | -11.5 | 24.3 |
| Barometric Pressure | 99367. | 99367. |
| Wind Speed | 2.7 | 2.9 |
| Wind Direction | 300 | 290 |
| Rain | No | No |
| Snow on ground | No | No |
| Daylight Savings Time Indicator | No | No |
| Solar Model Indicator | ASHRAEClearSky | ASHRAETau2017 |
| Clearness | 0.00 |  |
| Daily Wet-Bulb Temperature Range |  | 4.8 |
| ASHRAE Clear Sky Optical Depth for Beam Irradiance (taub) |  | 0.478 |
| ASHRAE Clear Sky Optical Depth for Diffuse Irradiance (taud) |  | 2.147 |

`Site:GroundTemperature:BuildingSurface` (1 object)

| Field | #1 |
|---|---|
| January Ground Temperature | 10.58 |
| February Ground Temperature | 7.22 |
| March Ground Temperature | 5.62 |
| April Ground Temperature | 5.56 |
| May Ground Temperature | 8.12 |
| June Ground Temperature | 11.83 |
| July Ground Temperature | 15.82 |
| August Ground Temperature | 19.24 |
| September Ground Temperature | 21.01 |
| October Ground Temperature | 20.68 |
| November Ground Temperature | 18.32 |
| December Ground Temperature | 14.7 |

`Site:WaterMainsTemperature` (1 object)

| Calculation Method |
|---|
| CorrelationFromWeatherFile |

## 3. Materials, constructions, glazing and internal mass

The layer thicknesses and the values that the documents give are marked in the comments of the IDF ("Source:"); the other values (conductivity, density, specific heat, absorptances, roughness) are assumptions that EnergyPlus needs.

`Material:NoMass` (5 objects)

| Name | Roughness | Thermal Resistance |
|---|---|---|
| Wall Layer | MediumSmooth | 7.7753 |
| Roof Layer | MediumSmooth | 12.5429 |
| Foundation Wall Layer | MediumSmooth | 4.1 |
| Slab Layer | MediumSmooth | 1.8 |
| Door Layer | MediumSmooth | 0.6252 |

`Construction` (6 objects)

| Name | Outside Layer |
|---|---|
| Exterior Wall | Wall Layer |
| Roof | Roof Layer |
| Foundation Wall | Foundation Wall Layer |
| Slab | Slab Layer |
| Door | Door Layer |
| Window | Window Glazing |

`WindowMaterial:SimpleGlazingSystem` (1 object)

| Name | U-Factor | Solar Heat Gain Coefficient | Visible Transmittance |
|---|---|---|---|
| Window Glazing | 1.1357 | 0.25 | 0.4 |

## 4. Performance curves (not in the documents)

EnergyPlus default curves of the HVAC objects.

`Curve:Quadratic` (6 objects)

| Name | Coefficient1 Constant | Coefficient2 x | Coefficient3 x**2 | Minimum Value of x | Maximum Value of x |
|---|---|---|---|---|---|
| Dehumidifier PLF | 0.95 | 0.05 | 0 | 0 | 1 |
| Heat Pump System HP Heating Coil EIR-FF | 1.3824 | -0.4336 | 0.0512 | 0.0 | 1.0 |
| Heat Pump System HP Heating Coil PLF | 0.75 | 0.25 | 0.0 | 0.0 | 1.0 |
| Heat Pump System Cool Coil Cap-FF | 0.8 | 0.2 | 0 | 0.5 | 1.5 |
| Heat Pump System Cool Coil EIR-FF | 1.1552 | -0.1808 | 0.0256 | 0.5 | 1.5 |
| Heat Pump System Cool Coil PLF | 0.85 | 0.15 | 0 | 0 | 1 |

`Curve:Biquadratic` (5 objects)

| Field | Dehumidifier Water Removal | Dehumidifier Energy Factor | Heat Pump System HP Heating Coil DefrEIR-FT | Heat Pump System Cool Coil Cap-FT | Heat Pump System Cool Coil EIR-FT |
|---|---|---|---|---|---|
| Name | Dehumidifier Water Removal | Dehumidifier Energy Factor | Heat Pump System HP Heating Coil DefrEIR-FT | Heat Pump System Cool Coil Cap-FT | Heat Pump System Cool Coil EIR-FT |
| Coefficient1 Constant | -2.724878664 | -2.388319069 | 1 | 0.942587793 | 0.342414409 |
| Coefficient2 x | 0.1007119836 | 0.09304773945 | 0 | 0.009543347 | 0.034885008 |
| Coefficient3 x**2 | -0.000990538285 | -0.001369700327 | 0 | 0.00068377 | -0.0006237 |
| Coefficient4 y | 0.05005304387 | 0.06653371676 | 0 | -0.011042676 | 0.004977216 |
| Coefficient5 y**2 | -0.000203629282 | -0.000343198063 | 0 | 0.000005249 | 0.000437951 |
| Coefficient6 x*y | -0.000341750531 | -0.000562490295 | 0 | -0.00000972 | -0.000728028 |
| Minimum Value of x | 21 | 21 | 0 | 12.77778 | 12.77778 |
| Maximum Value of x | 32.22 | 32.22 | 50 | 23.88889 | 23.88889 |
| Minimum Value of y | 40 | 40 | 0 | 18.0 | 18.0 |
| Maximum Value of y | 80 | 80 | 50 | 46.11111 | 46.11111 |

`Curve:Cubic` (3 objects)

| Name | Coefficient1 Constant | Coefficient2 x | Coefficient3 x**2 | Coefficient4 x**3 | Minimum Value of x | Maximum Value of x |
|---|---|---|---|---|---|---|
| Heat Pump System HP Heating Coil Cap-FT | 0.758746 | 0.027626 | 0.000148716 | 0.0000034992 | -20.0 | 20.0 |
| Heat Pump System HP Heating Coil Cap-FF | 0.84 | 0.16 | 0.0 | 0.0 | 0.5 | 1.5 |
| Heat Pump System HP Heating Coil EIR-FT | 1.19248 | -0.0300438 | 0.00103745 | -0.000023328 | -20.0 | 20.0 |

## 5. Output requests (not in the documents)

`Output:Meter` (1 object)

| Key Name | Reporting Frequency |
|---|---|
| Electricity:Facility | Monthly |

`Output:Table:SummaryReports` (1 object)

| Report 1 Name |
|---|
| AllSummary |
