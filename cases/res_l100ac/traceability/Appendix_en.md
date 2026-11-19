# Appendix (natural language): Residence test 8, ASHRAE Standard 140 / HERS BESTEST case L100AC (Colorado Springs)

Target IDF: `Residence/test8/L100AC.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that cannot be written in words, with the values of the documents replaced by markers). Documents: `orig/L100A.pdf` (scan), `orig/L100A_Text.txt` and `orig/L100A_Figures.txt` (OCR of the scan). Section 1 describes the geometry; the following sections give every field of the object classes that `Appendix_IDF.txt` leaves out, so that the IDF can be rebuilt from the documents and these two files.

## 1. Geometry in words

* **Shape and zoning.** A rectangular single-storey building of 57 ft x 27 ft (17.374 m x 8.230 m, outside dimensions of Figure 2-2 of L100A.pdf; the PDF wins over the OCR text) with a pitched roof (4:12). Two zones: `Conditioned Zone` (floor 143.0 m2, ceiling height 8 ft = 2.438 m, volume about 348 m3) and `Attic` (unconditioned, the space under the roof: floor 143.0 m2, ridge height 4.5 ft = 1.372 m above the attic floor, total height 3.810 m). There is no crawl space zone: the floor over the vented crawl space has the outdoor boundary condition, as HERS BESTEST requires (the crawl space air is the outdoor air).
* **Coordinates and orientation.** Origin at the south-west corner of the floor, X to the east (57 ft side), Y to the north (27 ft side), Z up; `Building` north axis 0, so the long walls face south and north and the short walls east and west (the compass arrow of the figure points up). World coordinates, vertices counter-clockwise seen from outside. Floor (0, 0, 0) (0, 8.230, 0) (17.374, 8.230, 0) (17.374, 0, 0).
* **Surfaces (11).** Conditioned zone: floor over the crawl space (Outdoors, 143.0 m2, normal facing down), four exterior walls (South and North 17.374 x 2.438 m = 42.4 m2, East and West 8.230 x 2.438 m = 20.1 m2; 124.9 m2 in total), and the ceiling (143.0 m2, boundary Surface, partner `Attic Floor`). Attic: the attic floor (the same rectangle at z = 2.438 m, opposite winding), two roof planes and two gables. The ridge runs east-west at y = 4.115 m (half of 8.230 m), z = 3.810 m: `Roof South` (0, 0, 2.438) (17.374, 0, 2.438) (17.374, 4.115, 3.810) (0, 4.115, 3.810) and `Roof North` on the other side, each 75.4 m2 (total 150.7 m2) with a tilt of 18.4 degrees (4:12 pitch); `Gable East` and `Gable West` are triangles of base 8.230 m and height 1.372 m (4.5 ft x 27 ft of the table), 5.64 m2 each.
* **Windows and doors (20 openings).** 6 windows on the south wall, 6 on the north wall, 3 on the east wall and 3 on the west wall, and one door on the south and one on the north wall (3 ft x 6 ft 8 in = 0.914 x 2.032 m, 1.86 m2 each, the door of the north wall at x = 9.449 to 10.363 m, that of the south wall at x = 10.363 to 11.277 m). A window unit is 3 ft x 5 ft gross (0.914 x 1.524 m) with a sill at 2 ft (0.610 m). EnergyPlus puts the frame outside the vertices, so the vertices of a window are the gross window set in by 2.75 in (0.0699 m) on every side: 0.775 m wide x 1.384 m high, sill at z = 0.679 m, top at z = 2.064 m, area 1.07 m2; the frame of 2.75 in and one horizontal divider of 2.75 in give the frame area 4.04 ft2 and the glass area 10.96 ft2 of the document. The positions along the wall (feet and inches from the corner, window to window and window to door) are in the comments after the vertices in `Appendix_IDF.txt`. Total window area 19.30 m2 (18 windows), doors 3.72 m2; window / exterior wall 18.4 % including the doors.
* **Build-up.** Walls: hardboard siding, fiberboard sheathing, insulation with framing, plasterboard (`Exterior Wall`); floor over the crawl space: insulation with joists, 3/4 in plywood, carpet and pad; ceiling and attic floor: ceiling insulation with joists and plasterboard; roof: asphalt shingle on 1/2 in plywood; gables: siding on plywood; doors: 1.75 in solid core; windows: one 3 mm clear glass with a frame and divider (`Window Frame`). All in section 3.
* **Case L100AC.** Colorado Springs, Colorado (6145 ft). The case has a heating thermostat only (ideal loads air system, `Conditioned Zone` only; the attic has no loads).

Computed from the IDF: 2 zone(s), 11 building surfaces (1 ceiling (surface), 1 floor (outdoors), 1 floor (surface), 2 roof (outdoors), 6 wall (outdoors)) and 20 openings. Coordinates in metres; bounding box of all vertices: x = 0.00 to 17.37, y = 0.00 to 8.23, z = 0.00 to 3.81 m. The vertex coordinates, each with its formula, are in `Appendix_IDF.txt`.

| Zone | Multiplier | x range m | y range m | z range m | Floor polygon area m2 |
|---|---|---|---|---|---|
| Conditioned Zone | 1 | 0.00 to 17.37 | 0.00 to 8.23 | 0.00 to 2.44 | 143.0 |
| Attic | 1 | 0.00 to 17.37 | 0.00 to 8.23 | 2.44 to 3.81 | 143.0 |

| Surface type | Construction | Boundary condition | Count | Total area m2 |
|---|---|---|---|---|
| Floor | Floor Over Crawl Space | Outdoors | 1 | 143.0 |
| Wall | Exterior Wall | Outdoors | 4 | 124.9 |
| Ceiling | Ceiling | Surface | 1 | 143.0 |
| Floor | Attic Floor | Surface | 1 | 143.0 |
| Roof | Roof | Outdoors | 2 | 150.7 |
| Wall | Gable | Outdoors | 2 | 11.3 |

| Opening type | Construction | Count | Total area m2 |
|---|---|---|---|
| Window | Window | 18 | 19.30 |
| Door | Door | 2 | 3.72 |

Building North Axis = 0 degrees; the directions below are the compass directions of the outward normals (y axis = north when the axis is 0).

Zone summary (volume = floor polygon area x height of the bounding box of the zone, an upper bound for a zone with a pitched roof):

| Zone | Floor area m2 | Height m | Volume m3 | Surfaces | Envelope area (outdoors + ground) m2 | Exterior wall area m2 | Opening area m2 | Opening / wall |
|---|---|---|---|---|---|---|---|---|
| Conditioned Zone | 143.0 | 2.44 | 348.6 | 6 | 267.8 | 124.9 | 23.02 | 18.4 % |
| Attic | 143.0 | 1.37 | 196.1 | 5 | 162.0 | 11.3 | 0.00 | 0.0 % |

Exterior walls and their openings by direction (gross wall area; an opening is counted in the wall it sits in):

| Direction | Wall surfaces | Gross wall area m2 | Window area m2 | Door / glass door area m2 | Window / gross wall |
|---|---|---|---|---|---|
| N | 1 | 42.4 | 6.43 | 1.86 | 15.2 % |
| E | 2 | 25.7 | 3.22 | 0.00 | 12.5 % |
| S | 1 | 42.4 | 6.43 | 1.86 | 15.2 % |
| W | 2 | 25.7 | 3.22 | 0.00 | 12.5 % |

| Roof surface | Zone | Area m2 | Tilt deg | Faces |
|---|---|---|---|---|
| Roof South | Attic | 75.4 | 18.4 | S |
| Roof North | Attic | 75.4 | 18.4 | N |

All building surfaces (tilt 0 = faces up, 90 = vertical, 180 = faces down):

| Surface | Type | Construction | Zone | Boundary | Vertices | Area m2 | Tilt deg | Direction |
|---|---|---|---|---|---|---|---|---|
| Floor | Floor | Floor Over Crawl Space | Conditioned Zone | Outdoors | 4 | 142.98 | 180 | - |
| Wall South | Wall | Exterior Wall | Conditioned Zone | Outdoors | 4 | 42.36 | 90 | S |
| Wall East | Wall | Exterior Wall | Conditioned Zone | Outdoors | 4 | 20.07 | 90 | E |
| Wall North | Wall | Exterior Wall | Conditioned Zone | Outdoors | 4 | 42.36 | 90 | N |
| Wall West | Wall | Exterior Wall | Conditioned Zone | Outdoors | 4 | 20.07 | 90 | W |
| Ceiling | Ceiling | Ceiling | Conditioned Zone | Surface | 4 | 142.98 | 0 | - |
| Attic Floor | Floor | Attic Floor | Attic | Surface | 4 | 142.98 | 180 | - |
| Roof South | Roof | Roof | Attic | Outdoors | 4 | 75.36 | 18 | S |
| Roof North | Roof | Roof | Attic | Outdoors | 4 | 75.36 | 18 | N |
| Gable East | Wall | Gable | Attic | Outdoors | 3 | 5.64 | 90 | E |
| Gable West | Wall | Gable | Attic | Outdoors | 3 | 5.64 | 90 | W |

Vertex coordinates in metres (as in the IDF; the formula of each coordinate is in `Appendix_IDF.txt`):

| Surface / opening | Vertices (x, y, z) |
|---|---|
| Floor | (0, 0, 0); (0, 8.23, 0); (17.37, 8.23, 0); (17.37, 0, 0) |
| Wall South | (0, 0, 2.438); (0, 0, 0); (17.37, 0, 0); (17.37, 0, 2.438) |
| Wall East | (17.37, 0, 2.438); (17.37, 0, 0); (17.37, 8.23, 0); (17.37, 8.23, 2.438) |
| Wall North | (17.37, 8.23, 2.438); (17.37, 8.23, 0); (0, 8.23, 0); (0, 8.23, 2.438) |
| Wall West | (0, 8.23, 2.438); (0, 8.23, 0); (0, 0, 0); (0, 0, 2.438) |
| Ceiling | (0, 0, 2.438); (17.37, 0, 2.438); (17.37, 8.23, 2.438); (0, 8.23, 2.438) |
| Attic Floor | (0, 0, 2.438); (0, 8.23, 2.438); (17.37, 8.23, 2.438); (17.37, 0, 2.438) |
| Roof South | (0, 0, 2.438); (17.37, 0, 2.438); (17.37, 4.115, 3.81); (0, 4.115, 3.81) |
| Roof North | (17.37, 8.23, 2.438); (0, 8.23, 2.438); (0, 4.115, 3.81); (17.37, 4.115, 3.81) |
| Gable East | (17.37, 0, 2.438); (17.37, 8.23, 2.438); (17.37, 4.115, 3.81) |
| Gable West | (0, 8.23, 2.438); (0, 0, 2.438); (0, 4.115, 3.81) |
| Window S1 | (1.594, 0, 2.064); (1.594, 0, 0.6794); (2.369, 0, 0.6794); (2.369, 0, 2.064) |
| Window S2 | (4.337, 0, 2.064); (4.337, 0, 0.6794); (5.112, 0, 0.6794); (5.112, 0, 2.064) |
| Window S3 | (5.861, 0, 2.064); (5.861, 0, 0.6794); (6.636, 0, 0.6794); (6.636, 0, 2.064) |
| Window S4 | (7.385, 0, 2.064); (7.385, 0, 0.6794); (8.16, 0, 0.6794); (8.16, 0, 2.064) |
| Window S5 | (8.909, 0, 2.064); (8.909, 0, 0.6794); (9.684, 0, 0.6794); (9.684, 0, 2.064) |
| Window S6 | (13.48, 0, 2.064); (13.48, 0, 0.6794); (14.26, 0, 0.6794); (14.26, 0, 2.064) |
| Door S | (10.36, 0, 2.032); (10.36, 0, 0); (11.28, 0, 0); (11.28, 0, 2.032) |
| Door N | (10.36, 8.23, 2.032); (10.36, 8.23, 0); (9.449, 8.23, 0); (9.449, 8.23, 2.032) |
| Window N1 | (3.283, 8.23, 2.064); (3.283, 8.23, 0.6794); (2.508, 8.23, 0.6794); (2.508, 8.23, 2.064) |
| Window N2 | (4.807, 8.23, 2.064); (4.807, 8.23, 0.6794); (4.032, 8.23, 0.6794); (4.032, 8.23, 2.064) |
| Window N3 | (6.941, 8.23, 2.064); (6.941, 8.23, 0.6794); (6.166, 8.23, 0.6794); (6.166, 8.23, 2.064) |
| Window N4 | (8.769, 8.23, 2.064); (8.769, 8.23, 0.6794); (7.995, 8.23, 0.6794); (7.995, 8.23, 2.064) |
| Window N5 | (13.04, 8.23, 2.064); (13.04, 8.23, 0.6794); (12.26, 8.23, 0.6794); (12.26, 8.23, 2.064) |
| Window N6 | (15.78, 8.23, 2.064); (15.78, 8.23, 0.6794); (15.01, 8.23, 0.6794); (15.01, 8.23, 2.064) |
| Window E1 | (17.37, 1.594, 2.064); (17.37, 1.594, 0.6794); (17.37, 2.369, 0.6794); (17.37, 2.369, 2.064) |
| Window E2 | (17.37, 3.728, 2.064); (17.37, 3.728, 0.6794); (17.37, 4.502, 0.6794); (17.37, 4.502, 2.064) |
| Window E3 | (17.37, 5.861, 2.064); (17.37, 5.861, 0.6794); (17.37, 6.636, 0.6794); (17.37, 6.636, 2.064) |
| Window W1 | (0, 2.064, 2.064); (0, 2.064, 0.6794); (0, 1.289, 0.6794); (0, 1.289, 2.064) |
| Window W2 | (0, 4.197, 2.064); (0, 4.197, 0.6794); (0, 3.423, 0.6794); (0, 3.423, 2.064) |
| Window W3 | (0, 6.636, 2.064); (0, 6.636, 0.6794); (0, 5.861, 0.6794); (0, 5.861, 2.064) |

Opening sizes (width = the longer horizontal extent of the polygon, height = z extent, sill = lowest z):

| Opening | Type | In surface | Direction | Width m | Height m | Sill m | Area m2 |
|---|---|---|---|---|---|---|---|
| Window S1 | Window | Wall South | S | 0.775 | 1.384 | 0.679 | 1.07 |
| Window S2 | Window | Wall South | S | 0.775 | 1.384 | 0.679 | 1.07 |
| Window S3 | Window | Wall South | S | 0.775 | 1.384 | 0.679 | 1.07 |
| Window S4 | Window | Wall South | S | 0.775 | 1.384 | 0.679 | 1.07 |
| Window S5 | Window | Wall South | S | 0.775 | 1.384 | 0.679 | 1.07 |
| Window S6 | Window | Wall South | S | 0.775 | 1.384 | 0.679 | 1.07 |
| Door S | Door | Wall South | S | 0.914 | 2.032 | 0.000 | 1.86 |
| Door N | Door | Wall North | N | 0.914 | 2.032 | 0.000 | 1.86 |
| Window N1 | Window | Wall North | N | 0.775 | 1.384 | 0.679 | 1.07 |
| Window N2 | Window | Wall North | N | 0.775 | 1.384 | 0.679 | 1.07 |
| Window N3 | Window | Wall North | N | 0.775 | 1.384 | 0.679 | 1.07 |
| Window N4 | Window | Wall North | N | 0.775 | 1.384 | 0.679 | 1.07 |
| Window N5 | Window | Wall North | N | 0.775 | 1.384 | 0.679 | 1.07 |
| Window N6 | Window | Wall North | N | 0.775 | 1.384 | 0.679 | 1.07 |
| Window E1 | Window | Wall East | E | 0.775 | 1.384 | 0.679 | 1.07 |
| Window E2 | Window | Wall East | E | 0.775 | 1.384 | 0.679 | 1.07 |
| Window E3 | Window | Wall East | E | 0.775 | 1.384 | 0.679 | 1.07 |
| Window W1 | Window | Wall West | W | 0.775 | 1.384 | 0.679 | 1.07 |
| Window W2 | Window | Wall West | W | 0.775 | 1.384 | 0.679 | 1.07 |
| Window W3 | Window | Wall West | W | 0.775 | 1.384 | 0.679 | 1.07 |

## 2. Settings, sizing periods and constant schedules (not in the documents)

These objects are required by EnergyPlus or are modelling choices; the documents do not give them.

`Version` (1 object)

| Version Identifier |
|---|
| 23.1 |

`Timestep` (1 object)

| Number of Timesteps per Hour |
|---|
| 6 |

`RunPeriod` (1 object)

| Name | Begin Month | Begin Day of Month | End Month | End Day of Month |
|---|---|---|---|---|
| Annual | 1 | 1 | 12 | 31 |

`GlobalGeometryRules` (1 object)

| Starting Vertex Position | Vertex Entry Direction | Coordinate System |
|---|---|---|
| UpperLeftCorner | Counterclockwise | World |

`Schedule:Constant` (3 objects)

| Name | Hourly Value EnergyPlus needs a schedule in the infiltration objects; the documents give constant infiltration (Section 2.2.5) | Hourly Value |
|---|---|---|
| Always On | 1 |  |
| Heating Setpoint |  | 20 |
| Heating Only Control |  | 1 |

## 3. Materials, constructions, glazing and internal mass

The layer thicknesses and the values that the documents give are marked in the comments of the IDF ("Source:"); the other values (conductivity, density, specific heat, absorptances, roughness) are assumptions that EnergyPlus needs.

`Material` (11 objects)

| Name | Roughness | Thickness | Conductivity | Density | Specific Heat | Thermal Absorptance | Solar Absorptance | Visible Absorptance |
|---|---|---|---|---|---|---|---|---|
| Plasterboard | MediumSmooth | 0.0127 | 0.16027 | 800.923 | 1088.57 | 0.9 | 0.6 | 0.6 |
| Fiberboard Sheathing | Rough | 0.0127 | 0.05469 | 288.332 | 1297.91 | 0.9 | 0.6 | 0.6 |
| Hardboard Siding | Rough | 0.01118 | 0.09415 | 640.739 | 1172.3 | 0.9 | 0.6 | 0.6 |
| Wall Insulation and Framing | MediumSmooth | 0.0889 | 0.05966 | 135.356 | 1352.66 | 0.9 | 0.6 | 0.6 |
| Ceiling Insulation and Joists | MediumSmooth | 0.15875 | 0.05472 | 53.382 | 1303.06 | 0.9 | 0.6 | 0.6 |
| Floor Insulation and Joists | Rough | 0.0889 | 0.05093 | 59.909 | 1303.06 | 0.9 | 0.6 | 0.6 |
| Plywood Half Inch | MediumSmooth | 0.0127 | 0.11544 | 544.628 | 1214.17 | 0.9 | 0.6 | 0.6 |
| Plywood Three Quarter Inch | MediumSmooth | 0.01905 | 0.11544 | 544.628 | 1214.17 | 0.9 | 0.6 | 0.6 |
| Asphalt Shingle | Rough | 0.00635 | 0.08186 | 1121.292 | 1256.04 | 0.9 | 0.6 | 0.6 |
| Solid Core Door | Rough | 0.04445 | 0.11579 | 512.591 | 1381.64 | 0.9 | 0.6 | 0.6 |
| Interior Wall Frame | MediumSmooth | 0.04445 | 0.11544 | 51.259 | 1381.64 | 0.9 | 0.6 | 0.6 |

`Material:NoMass` (1 object)

| Name | Roughness | Thermal Resistance | Thermal Absorptance | Solar Absorptance | Visible Absorptance |
|---|---|---|---|---|---|
| Carpet and Pad | MediumSmooth | 0.3663 | 0.9 | 0.6 | 0.6 |

`Construction` (9 objects)

| Name | Outside Layer | Layer 2 | Layer 3 | Layer 4 |
|---|---|---|---|---|
| Exterior Wall | Hardboard Siding | Fiberboard Sheathing | Wall Insulation and Framing | Plasterboard |
| Ceiling | Ceiling Insulation and Joists | Plasterboard |  |  |
| Attic Floor | Plasterboard | Ceiling Insulation and Joists |  |  |
| Floor Over Crawl Space | Floor Insulation and Joists | Plywood Three Quarter Inch | Carpet and Pad |  |
| Roof | Asphalt Shingle | Plywood Half Inch |  |  |
| Gable | Hardboard Siding | Plywood Half Inch |  |  |
| Door | Solid Core Door |  |  |  |
| Interior Wall | Plasterboard | Interior Wall Frame |  |  |
| Window | Window Glass |  |  |  |

`WindowMaterial:Glazing` (1 object)

| Field | Window Glass |
|---|---|
| Name | Window Glass |
| Optical Data Type | SpectralAverage |
| Thickness | 0.0030 |
| Solar Transmittance at Normal Incidence | 0.837 |
| Front Side Solar Reflectance at Normal Incidence | 0.075 |
| Back Side Solar Reflectance at Normal Incidence | 0.075 |
| Visible Transmittance at Normal Incidence | 0.837 |
| Front Side Visible Reflectance at Normal Incidence | 0.075 |
| Back Side Visible Reflectance at Normal Incidence | 0.075 |
| Infrared Transmittance at Normal Incidence | 0 |
| Front Side Infrared Hemispherical Emissivity | 0.84 |
| Back Side Infrared Hemispherical Emissivity | 0.84 |
| Conductivity | 0.9000 |

`WindowProperty:FrameAndDivider` (1 object)

| Field | Window Frame |
|---|---|
| Name | Window Frame |
| Frame Width | 0.06985 |
| Frame Conductance | 51.65 |
| Frame Solar Absorptance | 0.6 |
| Frame Visible Absorptance | 0.6 |
| Divider Type | DividedLite |
| Divider Width | 0.06985 |
| Number of Horizontal Dividers | 1 |
| Number of Vertical Dividers | 0 |
| Divider Conductance | 51.65 |
| Divider Solar Absorptance | 0.6 |
| Divider Visible Absorptance | 0.6 |

`InternalMass` (1 object)

| Name | Construction Name | Zone or ZoneList Name | Surface Area |
|---|---|---|---|
| Interior Walls | Interior Wall | Conditioned Zone | 190.265 |

## 4. Performance curves (not in the documents)

EnergyPlus default curves of the HVAC objects.


## 5. Output requests (not in the documents)

`Output:Variable` (2 objects)

| Key Value | Variable Name | Reporting Frequency |
|---|---|---|
| * | Zone Mean Air Temperature | Hourly |
| * | Zone Ideal Loads Zone Total Heating Energy | Hourly |

`Output:Meter` (2 objects)

| Key Name | Reporting Frequency |
|---|---|
| DistrictHeating:Facility | Monthly |
| InteriorEquipment:Electricity | Monthly |

`Output:Table:SummaryReports` (1 object)

| Report 1 Name |
|---|
| AllSummary |

`Output:SQLite` (1 object)

| Option Type |
|---|
| SimpleAndTabular |
