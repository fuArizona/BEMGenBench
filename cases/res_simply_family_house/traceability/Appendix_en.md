# Appendix (natural language): Residence test 5, single-storey house (Tucson, AZ)

Target IDF: `Residence/test5/Simply_family_house.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that cannot be written in words, with the values of the documents replaced by markers). Documents: `orig/info.txt` and the 15 images of `orig/` (floorplan_area.png, floorplan_size1..12.png, floorplan9834.png, HVAC.png). Section 1 describes the geometry; the following sections give every field of the object classes that `Appendix_IDF.txt` leaves out, so that the IDF can be rebuilt from the documents and these two files.

## 1. Geometry in words

* **Zoning.** The 10 conditioned rooms of the floor plan (Kitchen, Living Room, Laundry, Closet, Bathroom 110, Bathroom 45, Bedroom 197, Bedroom 118, Bedroom 109, Bedroom 110) are ONE zone, `Conditioned House` (info.txt: the interior doors are normally open, a return air path exists, one thermostat serves them). The garage (info.txt: Office 113, Office 104 and the Hallway merged into the 2-car garage) is a second, unconditioned zone, `Garage` (its entry door is normally closed). Floor area of `Conditioned House` 147.0 m2 (the sum of the room labels, 1,582 ft2; the living area of info.txt is 1,815 ft2 because hallways and wall thicknesses are not modelled), `Garage` 34.8 m2.
* **Coordinates and orientation.** The plan of floorplan9834.png is drawn with north at the bottom; info.txt says the front door faces north (checked on site). The plan coordinates (u, v) are therefore rotated by -90 degrees: X = v, Y = -u, Z = 0 at the floor, `Building` north axis 0, world coordinates, vertices counter-clockwise seen from outside. The entry side of the plan (the Kitchen wall with the front door) faces north, the covered back patio (south side) carries the Living Room patio door. Every vertex has its formula (the plan coordinates u0, u1 = u0 + w, v0, v1 = v0 +/- d) in `Appendix_IDF.txt`.
* **Size of each room.** Every room is a rectangle (the garage is a 6-point polygon). The area A is the label of floorplan_area.png. A room with two printed edges uses both (Laundry 5 ft 4 in x 7 ft 4 in, Closet 8 ft 5 in x 7 ft 4 in, Bedroom 197 12 ft 2 in x 16 ft 2 in); a room with one printed edge has the other edge d = A / w (Bathroom 110 w = 5 ft 0 in, Bedroom 118 w = 10 ft 11 in, Bedroom 109 w = 10 ft 1 in, Bedroom 110 w = 10 ft 2 in); a room with no printed edge has the aspect ratio 2:1, w = sqrt(2 A), d = sqrt(A / 2) (Kitchen 410 ft2 = 8.73 m x 4.36 m, Living Room 383 ft2 = 8.44 m x 4.22 m, Bathroom 45 45 ft2 = 2.90 m x 1.45 m; ASSUMED). The garage polygon in plan coordinates is (0, d113) (w113 + w104, d113) (w113 + w104, 0) (wh, 0) (wh, -dh) (0, -dh) with w113 = 10 ft 8 in, d113 = 10 ft 7 in, w104 = 9 ft 10 in, wh = 21 ft 0 in, dh = 7 ft 6 in (floorplan_size1, 10, 11, 12.png): floor area 34.8 m2.
* **Position of the rooms.** Only four relations are on floorplan9834.png: the Kitchen lies right of the garage / hallway side (u = 6.40 to 15.13 m), the Living Room right of the Kitchen (u = 15.13 to 23.56 m), the Laundry below the Living Room and the Closet right of the Laundry; these rooms share walls. The other six rooms (Bathroom 110, Bedroom 197, Bedroom 118, Bathroom 45, Bedroom 109, Bedroom 110) have no position hint and are placed one after the other along u, each 5.0 m after the previous one (ASSUMED), with v0 = 0. So the model is a string of boxes: bounding box x = -6.45 to 6.71 m, y = -71.19 to 0 m, and only 6 pairs of coincident walls exist (named after the room that carries the first surface: Closet 2, Kitchen 2, Laundry 1, Garage 1; the partner is the `_mirror` surface on the neighbouring room) that are interior walls (`Surface` boundary); every other room wall is an exterior wall (`Outdoors`). This is a modelling consequence of the missing adjacency data, not a statement of the documents.
* **Heights.** The ceiling height is 9 ft 1 in = 2.769 m where a floorplan_size image gives it (Kitchen, Bedroom 109, Bathroom 110, Garage) and 9 ft 0 in = 2.743 m for the other rooms (info.txt: 9 ft ceilings; ASSUMED where the image is silent). Each room has a floor, a flat roof at the ceiling height (the roof slope is not in the documents) and one wall per polygon edge; no attic, overhang, porch or patio roof is modelled (info.txt gives them, but no shading object is written).
* **Build-up.** Floor: 150 mm concrete slab on grade (`constr-default-slabongrade`, boundary Ground; info.txt gives a post-tension slab, the thickness is ASSUMED). Exterior walls: wall model A of info.txt (stucco, R-6 rigid foam, OSB, 2x4 studs with R-13 batt, gypsum; `constr-exterior-wall`). Interior walls: gypsum / air space / gypsum, 5/8 in Type X at the garage wall. Roof: R-30 ceiling insulation with a roofing layer, plywood and gypsum (`constr-roof`).
* **Openings** (sill 24 in = 0.610 m for all windows; U = 1.987 W/m2K, SHGC = 0.25 simple glazing, the code limits because the label values are unknown): Bedroom 118 north window 60 x 72 in (1.524 x 1.829 m), centred; Bedroom 109 and Bedroom 110 east windows 36 x 76 in (0.914 x 1.930 m); Bedroom 197 two south windows 36 x 76 in; Living Room west window 36 x 76 in (on the corner of the Laundry); Living Room patio sliding door (glass door, 6 ft x 8 ft = 1.829 x 2.438 m) in the south wall; front door 3 ft x 6 ft 8 in (0.914 x 2.032 m) in the north wall of the Kitchen; the garage entry door of the same size appears twice, once in the garage wall and once as its mirror in the Kitchen wall. Total: 6 windows 11.61 m2, 1 glass door 4.46 m2, 3 door leaves 5.57 m2. The Kitchen, bathrooms, closet and laundry have no windows.
* **Check numbers (computed from the IDF).** 73 building surfaces (11 floor, 11 roof, 39 exterior wall, 12 interior wall), 10 openings; exterior wall area 347.2 m2 (`Conditioned House`) and 59.6 m2 (`Garage`); window / exterior wall ratio 5.7 % and 3.1 %. The room, surface, opening and vertex tables below are produced from the IDF.

Computed from the IDF: 2 zone(s), 73 building surfaces (11 floor (ground), 11 roof (outdoors), 39 wall (outdoors), 12 wall (surface)) and 10 openings. Coordinates in metres; bounding box of all vertices: x = -6.45 to 6.71, y = -71.19 to -0.00, z = 0.00 to 2.77 m. The vertex coordinates, each with its formula, are in `Appendix_IDF.txt`.

| Zone | Multiplier | x range m | y range m | z range m | Floor polygon area m2 |
|---|---|---|---|---|---|
| Conditioned House | 1 | -6.45 to 6.71 | -71.19 to -6.40 | 0.00 to 2.77 | 147.0 |
| Garage | 1 | -2.29 to 3.23 | -6.40 to -0.00 | 0.00 to 2.77 | 34.8 |

| Surface type | Construction | Boundary condition | Count | Total area m2 |
|---|---|---|---|---|
| Floor | constr-default-slabongrade | Ground | 11 | 181.8 |
| Roof | constr-roof | Outdoors | 11 | 181.8 |
| Wall | constr-exterior-wall | Outdoors | 39 | 406.9 |
| Wall | constr-interior-wall | Surface | 5 | 29.7 |
| Wall | constr-interior-wall_rev | Surface | 5 | 29.6 |
| Wall | constr-garage-interior-wall_rev | Surface | 1 | 6.3 |
| Wall | constr-garage-interior-wall | Surface | 1 | 6.3 |

| Opening type | Construction | Count | Total area m2 |
|---|---|---|---|
| Window | constr-window | 6 | 11.61 |
| GlassDoor | constr-window | 1 | 4.46 |
| Door | constr-exterior-door | 3 | 5.57 |

Building North Axis = 0 degrees; the directions below are the compass directions of the outward normals (y axis = north when the axis is 0).

Zone summary (volume = floor polygon area x height of the bounding box of the zone, an upper bound for a zone with a pitched roof):

| Zone | Floor area m2 | Height m | Volume m3 | Surfaces | Envelope area (outdoors + ground) m2 | Exterior wall area m2 | Opening area m2 | Opening / wall |
|---|---|---|---|---|---|---|---|---|
| Conditioned House | 147.0 | 2.77 | 407.0 | 65 | 641.3 | 347.2 | 19.79 | 5.7 % |
| Garage | 34.8 | 2.77 | 96.3 | 8 | 129.2 | 59.6 | 1.86 | 3.1 % |

Exterior walls and their openings by direction (gross wall area; an opening is counted in the wall it sits in):

| Direction | Wall surfaces | Gross wall area m2 | Window area m2 | Door / glass door area m2 | Window / gross wall |
|---|---|---|---|---|---|
| N | 9 | 90.0 | 2.79 | 1.86 | 3.1 % |
| E | 10 | 113.5 | 3.53 | 0.00 | 3.1 % |
| S | 9 | 89.9 | 3.53 | 4.46 | 3.9 % |
| W | 11 | 113.5 | 1.77 | 0.00 | 1.6 % |

| Roof surface | Zone | Area m2 | Tilt deg | Faces |
|---|---|---|---|---|
| surf-sp-bathroom-110-L1-roof-1 | Conditioned House | 10.2 | 0.0 | flat |
| surf-sp-bathroom-45-L1-roof-1 | Conditioned House | 4.2 | 0.0 | flat |
| surf-sp-bedroom-109-L1-roof-1 | Conditioned House | 10.1 | 0.0 | flat |
| surf-sp-bedroom-110-L1-roof-1 | Conditioned House | 10.2 | 0.0 | flat |
| surf-sp-bedroom-118-L1-roof-1 | Conditioned House | 11.0 | 0.0 | flat |
| surf-sp-bedroom-197-L1-roof-1 | Conditioned House | 18.3 | 0.0 | flat |
| surf-sp-closet-L1-roof-1 | Conditioned House | 5.7 | 0.0 | flat |
| surf-sp-kitchen-L1-roof-1 | Conditioned House | 38.1 | 0.0 | flat |
| surf-sp-laundry-L1-roof-1 | Conditioned House | 3.6 | 0.0 | flat |
| surf-sp-living-room-L1-roof-1 | Conditioned House | 35.6 | 0.0 | flat |
| surf-sp-garage-L1-roof-1 | Garage | 34.8 | 0.0 | flat |

Rooms (the surfaces whose names carry the same room part belong to one room):

| Room key | Zone(s) of its surfaces | Surfaces | x range m | y range m | Floor area m2 | Ceiling height m | Exterior wall m2 | Interior wall m2 | Opening m2 |
|---|---|---|---|---|---|---|---|---|---|
| bathroom-110 | Conditioned House | 6 | 0.00 to 6.71 | -30.09 to -28.56 | 10.2 | 2.77 | 45.6 | 0.0 | 0.00 |
| bathroom-45 | Conditioned House | 6 | 0.00 to 1.45 | -55.02 to -52.12 | 4.2 | 2.74 | 23.8 | 0.0 | 0.00 |
| bedroom-109 | Conditioned House | 6 | 0.00 to 3.30 | -63.09 to -60.02 | 10.1 | 2.77 | 35.3 | 0.0 | 1.77 |
| bedroom-110 | Conditioned House | 6 | 0.00 to 3.30 | -71.19 to -68.09 | 10.2 | 2.74 | 35.1 | 0.0 | 1.77 |
| bedroom-118 | Conditioned House | 6 | 0.00 to 3.29 | -47.12 to -43.80 | 11.0 | 2.74 | 36.3 | 0.0 | 2.79 |
| bedroom-197 | Conditioned House | 6 | 0.00 to 4.93 | -38.80 to -35.09 | 18.3 | 2.74 | 47.4 | 0.0 | 3.53 |
| closet | Conditioned House | 8 | -6.45 to -4.22 | -19.32 to -16.75 | 5.7 | 2.74 | 13.2 | 26.3 | 0.00 |
| garage | Conditioned House + Garage | 9 | -2.29 to 3.23 | -6.40 to -0.00 | 34.8 | 2.77 | 59.6 | 12.7 | 3.72 |
| kitchen | Conditioned House | 9 | -4.36 to 0.00 | -15.13 to -6.40 | 38.1 | 2.77 | 54.1 | 24.1 | 1.86 |
| laundry | Conditioned House | 6 | -6.45 to -4.22 | -16.75 to -15.13 | 3.6 | 2.74 | 10.2 | 8.9 | 0.00 |
| living-room | Conditioned House | 5 | -4.22 to 0.00 | -23.56 to -15.13 | 35.6 | 2.74 | 46.4 | 0.0 | 6.22 |

All building surfaces (tilt 0 = faces up, 90 = vertical, 180 = faces down):

| Surface | Type | Construction | Zone | Boundary | Vertices | Area m2 | Tilt deg | Direction |
|---|---|---|---|---|---|---|---|---|
| surf-sp-bathroom-110-L1-floor-1 | Floor | constr-default-slabongrade | Conditioned House | Ground | 4 | 10.22 | 180 | - |
| surf-sp-bathroom-110-L1-roof-1 | Roof | constr-roof | Conditioned House | Outdoors | 4 | 10.22 | 0 | - |
| surf-sp-bathroom-110-L1-wall-1 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 4.22 | 90 | W |
| surf-sp-bathroom-110-L1-wall-2 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 18.57 | 90 | S |
| surf-sp-bathroom-110-L1-wall-3 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 4.22 | 90 | E |
| surf-sp-bathroom-110-L1-wall-4 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 18.57 | 90 | N |
| surf-sp-bathroom-45-L1-floor-1 | Floor | constr-default-slabongrade | Conditioned House | Ground | 4 | 4.18 | 180 | - |
| surf-sp-bathroom-45-L1-roof-1 | Roof | constr-roof | Conditioned House | Outdoors | 4 | 4.18 | 0 | - |
| surf-sp-bathroom-45-L1-wall-1 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 7.93 | 90 | W |
| surf-sp-bathroom-45-L1-wall-2 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 3.97 | 90 | S |
| surf-sp-bathroom-45-L1-wall-3 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 7.93 | 90 | E |
| surf-sp-bathroom-45-L1-wall-4 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 3.97 | 90 | N |
| surf-sp-bedroom-109-L1-floor-1 | Floor | constr-default-slabongrade | Conditioned House | Ground | 4 | 10.13 | 180 | - |
| surf-sp-bedroom-109-L1-roof-1 | Roof | constr-roof | Conditioned House | Outdoors | 4 | 10.13 | 0 | - |
| surf-sp-bedroom-109-L1-wall-1 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 8.51 | 90 | W |
| surf-sp-bedroom-109-L1-wall-2 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 9.13 | 90 | S |
| surf-sp-bedroom-109-L1-wall-3 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 8.51 | 90 | E |
| surf-sp-bedroom-109-L1-wall-4 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 9.13 | 90 | N |
| surf-sp-bedroom-110-L1-floor-1 | Floor | constr-default-slabongrade | Conditioned House | Ground | 4 | 10.22 | 180 | - |
| surf-sp-bedroom-110-L1-roof-1 | Roof | constr-roof | Conditioned House | Outdoors | 4 | 10.22 | 0 | - |
| surf-sp-bedroom-110-L1-wall-1 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 8.50 | 90 | W |
| surf-sp-bedroom-110-L1-wall-2 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 9.05 | 90 | S |
| surf-sp-bedroom-110-L1-wall-3 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 8.50 | 90 | E |
| surf-sp-bedroom-110-L1-wall-4 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 9.05 | 90 | N |
| surf-sp-bedroom-118-L1-floor-1 | Floor | constr-default-slabongrade | Conditioned House | Ground | 4 | 10.96 | 180 | - |
| surf-sp-bedroom-118-L1-roof-1 | Roof | constr-roof | Conditioned House | Outdoors | 4 | 10.96 | 0 | - |
| surf-sp-bedroom-118-L1-wall-1 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 9.13 | 90 | W |
| surf-sp-bedroom-118-L1-wall-2 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 9.04 | 90 | S |
| surf-sp-bedroom-118-L1-wall-3 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 9.13 | 90 | E |
| surf-sp-bedroom-118-L1-wall-4 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 9.04 | 90 | N |
| surf-sp-bedroom-197-L1-floor-1 | Floor | constr-default-slabongrade | Conditioned House | Ground | 4 | 18.27 | 180 | - |
| surf-sp-bedroom-197-L1-roof-1 | Roof | constr-roof | Conditioned House | Outdoors | 4 | 18.27 | 0 | - |
| surf-sp-bedroom-197-L1-wall-1 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 10.17 | 90 | W |
| surf-sp-bedroom-197-L1-wall-2 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 13.52 | 90 | S |
| surf-sp-bedroom-197-L1-wall-3 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 10.17 | 90 | E |
| surf-sp-bedroom-197-L1-wall-4 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 13.52 | 90 | N |
| surf-sp-closet-L1-floor-1 | Floor | constr-default-slabongrade | Conditioned House | Ground | 4 | 5.73 | 180 | - |
| surf-sp-closet-L1-roof-1 | Roof | constr-roof | Conditioned House | Outdoors | 4 | 5.73 | 0 | - |
| surf-sp-closet-L1-wall-1 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 7.04 | 90 | W |
| surf-sp-closet-L1-wall-2 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 6.13 | 90 | S |
| surf-sp-closet-L1-wall-3 | Wall | constr-interior-wall | Conditioned House | Surface | 4 | 7.04 | 90 | E |
| surf-sp-closet-L1-wall-3_mirror | Wall | constr-interior-wall_rev | Conditioned House | Surface | 4 | 7.04 | 90 | W |
| surf-sp-closet-L1-wall-4 | Wall | constr-interior-wall | Conditioned House | Surface | 4 | 6.13 | 90 | N |
| surf-sp-closet-L1-wall-4_mirror | Wall | constr-interior-wall_rev | Conditioned House | Surface | 4 | 6.13 | 90 | S |
| surf-sp-garage-L1-wall-2_mirror | Wall | constr-garage-interior-wall_rev | Conditioned House | Surface | 4 | 6.33 | 90 | N |
| surf-sp-kitchen-L1-floor-1 | Floor | constr-default-slabongrade | Conditioned House | Ground | 4 | 38.09 | 180 | - |
| surf-sp-kitchen-L1-roof-1 | Roof | constr-roof | Conditioned House | Outdoors | 4 | 38.09 | 0 | - |
| surf-sp-kitchen-L1-wall-1 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 24.16 | 90 | W |
| surf-sp-kitchen-L1-wall-2 | Wall | constr-interior-wall | Conditioned House | Surface | 4 | 0.41 | 90 | S |
| surf-sp-kitchen-L1-wall-2_mirror | Wall | constr-interior-wall_rev | Conditioned House | Surface | 4 | 0.40 | 90 | N |
| surf-sp-kitchen-L1-wall-3 | Wall | constr-interior-wall | Conditioned House | Surface | 4 | 11.68 | 90 | S |
| surf-sp-kitchen-L1-wall-3_mirror | Wall | constr-interior-wall_rev | Conditioned House | Surface | 4 | 11.57 | 90 | N |
| surf-sp-kitchen-L1-wall-4 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 24.16 | 90 | E |
| surf-sp-kitchen-L1-wall-5 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 5.75 | 90 | N |
| surf-sp-laundry-L1-floor-1 | Floor | constr-default-slabongrade | Conditioned House | Ground | 4 | 3.63 | 180 | - |
| surf-sp-laundry-L1-roof-1 | Roof | constr-roof | Conditioned House | Outdoors | 4 | 3.63 | 0 | - |
| surf-sp-laundry-L1-wall-1 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 4.46 | 90 | W |
| surf-sp-laundry-L1-wall-2 | Wall | constr-interior-wall | Conditioned House | Surface | 4 | 4.46 | 90 | E |
| surf-sp-laundry-L1-wall-2_mirror | Wall | constr-interior-wall_rev | Conditioned House | Surface | 4 | 4.46 | 90 | W |
| surf-sp-laundry-L1-wall-3 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 5.73 | 90 | N |
| surf-sp-living-room-L1-floor-1 | Floor | constr-default-slabongrade | Conditioned House | Ground | 4 | 35.58 | 180 | - |
| surf-sp-living-room-L1-roof-1 | Roof | constr-roof | Conditioned House | Outdoors | 4 | 35.58 | 0 | - |
| surf-sp-living-room-L1-wall-1 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 11.64 | 90 | W |
| surf-sp-living-room-L1-wall-2 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 11.57 | 90 | S |
| surf-sp-living-room-L1-wall-3 | Wall | constr-exterior-wall | Conditioned House | Outdoors | 4 | 23.14 | 90 | E |
| surf-sp-garage-L1-floor-1 | Floor | constr-default-slabongrade | Garage | Ground | 6 | 34.79 | 180 | - |
| surf-sp-garage-L1-roof-1 | Roof | constr-roof | Garage | Outdoors | 6 | 34.79 | 0 | - |
| surf-sp-garage-L1-wall-1 | Wall | constr-exterior-wall | Garage | Outdoors | 4 | 17.72 | 90 | W |
| surf-sp-garage-L1-wall-2 | Wall | constr-garage-interior-wall | Garage | Surface | 4 | 6.33 | 90 | S |
| surf-sp-garage-L1-wall-3 | Wall | constr-exterior-wall | Garage | Outdoors | 4 | 0.42 | 90 | E |
| surf-sp-garage-L1-wall-4 | Wall | constr-exterior-wall | Garage | Outdoors | 4 | 8.93 | 90 | S |
| surf-sp-garage-L1-wall-5 | Wall | constr-exterior-wall | Garage | Outdoors | 4 | 17.30 | 90 | E |
| surf-sp-garage-L1-wall-6 | Wall | constr-exterior-wall | Garage | Outdoors | 4 | 15.26 | 90 | N |

Opening sizes (width = the longer horizontal extent of the polygon, height = z extent, sill = lowest z):

| Opening | Type | In surface | Direction | Width m | Height m | Sill m | Area m2 |
|---|---|---|---|---|---|---|---|
| Bedroom 118 North Window | Window | surf-sp-bedroom-118-L1-wall-4 | N | 1.524 | 1.829 | 0.610 | 2.79 |
| Bedroom 109 East Window | Window | surf-sp-bedroom-109-L1-wall-3 | E | 0.914 | 1.930 | 0.610 | 1.77 |
| Bedroom 110 East Window | Window | surf-sp-bedroom-110-L1-wall-3 | E | 0.914 | 1.930 | 0.610 | 1.77 |
| Bedroom 197 South Window 1 | Window | surf-sp-bedroom-197-L1-wall-2 | S | 0.914 | 1.930 | 0.610 | 1.77 |
| Bedroom 197 South Window 2 | Window | surf-sp-bedroom-197-L1-wall-2 | S | 0.914 | 1.930 | 0.610 | 1.77 |
| Living Room West Window | Window | surf-sp-living-room-L1-wall-1 | W | 0.914 | 1.930 | 0.610 | 1.77 |
| Living Room Patio Door | GlassDoor | surf-sp-living-room-L1-wall-2 | S | 1.829 | 2.438 | 0.000 | 4.46 |
| Front Door | Door | surf-sp-kitchen-L1-wall-5 | N | 0.914 | 2.032 | 0.000 | 1.86 |
| Garage Entry Door | Door | surf-sp-garage-L1-wall-2 | S | 0.914 | 2.032 | 0.000 | 1.86 |
| Kitchen Garage Entry Door | Door | surf-sp-garage-L1-wall-2_mirror | N | 0.914 | 2.032 | 0.000 | 1.86 |

## 2. Settings, sizing periods and constant schedules (not in the documents)

These objects are required by EnergyPlus or are modelling choices; the documents do not give them.

`Version` (1 object)

| Version Identifier |
|---|
| 23.1 |

`SimulationControl` (1 object)

| Do Zone Sizing Calculation | Do System Sizing Calculation | Do Plant Sizing Calculation | Run Simulation for Sizing Periods | Run Simulation for Weather File Run Periods |
|---|---|---|---|---|
| Yes | Yes | No | Yes | Yes |

`Timestep` (1 object)

| Number of Timesteps per Hour |
|---|
| 6 |

`RunPeriod` (1 object)

| Field | Run Period 1 |
|---|---|
| Name | Run Period 1 |
| Begin Month | 1 |
| Begin Day of Month | 1 |
| End Month | 12 |
| End Day of Month | 31 |
| Day of Week for Start Day | Friday |
| Use Weather File Holidays and Special Days | No |
| Use Weather File Daylight Saving Period | No |
| Apply Weekend Holiday Rule | No |

`GlobalGeometryRules` (1 object)

| Starting Vertex Position | Vertex Entry Direction | Coordinate System |
|---|---|---|
| UpperLeftCorner | Counterclockwise | World |

`ScheduleTypeLimits` (4 objects)

| Name | Lower Limit Value | Upper Limit Value | Numeric Type | Unit Type |
|---|---|---|---|---|
| Fraction | 0 | 1 | Continuous | Dimensionless |
| ActivityLevel | 0 |  | Continuous | ActivityLevel |
| OnOff | 0 | 1 | Discrete |  |
| HVACTemplate Any Number |  |  |  |  |

`SizingPeriod:DesignDay` (2 objects)

| Field | Tucson-Davis-Monthan.AFB Ann Clg .4% Condns DB=>MWB | Tucson-Davis-Monthan.AFB Ann Htg 99.6% Condns DB |
|---|---|---|
| Name | Tucson-Davis-Monthan.AFB Ann Clg .4% Condns DB=>MWB | Tucson-Davis-Monthan.AFB Ann Htg 99.6% Condns DB |
| Month | 6 | 12 |
| Day of Month | 21 | 21 |
| Day Type | SummerDesignDay | WinterDesignDay |
| Maximum Dry-Bulb Temperature | 40.8 | 0.1 |
| Daily Dry-Bulb Temperature Range | 16.9 | 0.0 |
| Dry-Bulb Temperature Range Modifier Type | DefaultMultipliers | DefaultMultipliers |
| Humidity Condition Type | WetBulb | WetBulb |
| Wetbulb or DewPoint at Maximum Dry-Bulb | 18.6 | 0.1 |
| Daily Wet-Bulb Temperature Range | 6.0 |  |
| Barometric Pressure | 91810.0 | 91810.0 |
| Wind Speed | 4.6 | 2.4 |
| Wind Direction | 310.0 | 140.0 |
| Rain Indicator | No | No |
| Snow Indicator | No | No |
| Daylight Saving Time Indicator | No | No |
| Solar Model Indicator | ASHRAETau2017 | ASHRAEClearSky |
| ASHRAE Clear Sky Optical Depth for Beam Irradiance (taub) | 0.357 |  |
| ASHRAE Clear Sky Optical Depth for Diffuse Irradiance (taud) | 2.321 |  |
| Sky Clearness |  | 0.0 |

`Site:GroundTemperature:BuildingSurface` (1 object)

| Field | #1 |
|---|---|
| January Ground Temperature | 18.0 |
| February Ground Temperature | 18.0 |
| March Ground Temperature | 18.0 |
| April Ground Temperature | 18.0 |
| May Ground Temperature | 18.0 |
| June Ground Temperature | 18.0 |
| July Ground Temperature | 18.0 |
| August Ground Temperature | 18.0 |
| September Ground Temperature | 18.0 |
| October Ground Temperature | 18.0 |
| November Ground Temperature | 18.0 |
| December Ground Temperature | 18.0 |

## 3. Materials, constructions, glazing and internal mass

The layer thicknesses and the values that the documents give are marked in the comments of the IDF ("Source:"); the other values (conductivity, density, specific heat, absorptances, roughness) are assumptions that EnergyPlus needs.

`Material` (9 objects)

| Name | Roughness | Thickness | Conductivity | Density | Specific Heat | Thermal Absorptance | Solar Absorptance | Visible Absorptance |
|---|---|---|---|---|---|---|---|---|
| Stucco 7/16 in | Rough | 0.0111 | 0.72 | 1860 | 840 |  |  |  |
| OSB 7/16 in | Smooth | 0.0111 | 0.12 | 544 | 1210 |  |  |  |
| Fiberglass Batt R-13 3.5 in | Rough | 0.0889 | 0.03883 | 12 | 840 |  |  |  |
| Gypsum 1/2 in | MediumSmooth | 0.0127 | 0.16 | 800 | 1090 |  |  |  |
| Gypsum 5/8 in Type X | MediumSmooth | 0.0159 | 0.16 | 800 | 1090 |  |  |  |
| Insulated Door 1.75 in | MediumSmooth | 0.0445 | 0.05048 | 300 | 1200 | 0.9 | 0.6 | 0.6 |
| mat-default-m14-150mm-heavyweight-concrete | MediumRough | 0.1524 | 1.95 | 2240.0 | 900.0 |  |  |  |
| mat-default-f13-built-up-roofing | Rough | 0.0095 | 0.16 | 1120.0 | 1460.0 |  |  |  |
| mat-default-g02-16mm-plywood | Smooth | 0.0159 | 0.12 | 544.0 | 1210.0 |  |  |  |

`Material:NoMass` (3 objects)

| Name | Roughness | Thermal Resistance |
|---|---|---|
| Rigid Foam R-6 | MediumSmooth | 1.05666 |
| Ceiling Insulation R-30 | Rough | 5.28330 |
| mat-lib-f04-wall-air-space-resistance | MediumRough | 0.15 |

`Construction` (9 objects)

| Name | Outside Layer | Layer 2 | Layer 3 | Layer 4 | Layer 5 |
|---|---|---|---|---|---|
| constr-exterior-wall | Stucco 7/16 in | Rigid Foam R-6 | OSB 7/16 in | Fiberglass Batt R-13 3.5 in | Gypsum 1/2 in |
| constr-interior-wall | Gypsum 1/2 in | mat-lib-f04-wall-air-space-resistance | Gypsum 1/2 in |  |  |
| constr-interior-wall_rev | Gypsum 1/2 in | mat-lib-f04-wall-air-space-resistance | Gypsum 1/2 in |  |  |
| constr-garage-interior-wall | Gypsum 5/8 in Type X | mat-lib-f04-wall-air-space-resistance | Gypsum 5/8 in Type X |  |  |
| constr-garage-interior-wall_rev | Gypsum 5/8 in Type X | mat-lib-f04-wall-air-space-resistance | Gypsum 5/8 in Type X |  |  |
| constr-roof | mat-default-f13-built-up-roofing | mat-default-g02-16mm-plywood | Ceiling Insulation R-30 | Gypsum 1/2 in |  |
| constr-exterior-door | Insulated Door 1.75 in |  |  |  |  |
| constr-window | Window Glazing U-0.35 SHGC-0.25 |  |  |  |  |
| constr-default-slabongrade | mat-default-m14-150mm-heavyweight-concrete |  |  |  |  |

`WindowMaterial:SimpleGlazingSystem` (1 object)

| Name | U-Factor | Solar Heat Gain Coefficient |
|---|---|---|
| Window Glazing U-0.35 SHGC-0.25 | 1.98739 | 0.25 |

## 4. Performance curves (not in the documents)

EnergyPlus default curves of the HVAC objects.

`Curve:Quadratic` (5 objects)

| Name | Coefficient1 Constant | Coefficient2 x | Coefficient3 x**2 | Minimum Value of x | Maximum Value of x |
|---|---|---|---|---|---|
| hvac-hp Cool Coil Cap-FF | 0.8 | 0.2 | 0 | 0.5 | 1.5 |
| hvac-hp Cool Coil EIR-FF | 1.1552 | -0.1808 | 0.0256 | 0.5 | 1.5 |
| hvac-hp Cool Coil PLF | 0.85 | 0.15 | 0 | 0 | 1 |
| hvac-hp HP Heating Coil EIR-FF | 1.3824 | -0.4336 | 0.0512 | 0.0 | 1.0 |
| hvac-hp HP Heating Coil PLF | 0.75 | 0.25 | 0.0 | 0.0 | 1.0 |

`Curve:Biquadratic` (3 objects)

| Field | hvac-hp Cool Coil Cap-FT | hvac-hp Cool Coil EIR-FT | hvac-hp HP Heating Coil DefrEIR-FT |
|---|---|---|---|
| Name | hvac-hp Cool Coil Cap-FT | hvac-hp Cool Coil EIR-FT | hvac-hp HP Heating Coil DefrEIR-FT |
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
| hvac-hp HP Heating Coil Cap-FT | 0.758746 | 0.027626 | 0.000148716 | 0.0000034992 | -20.0 | 20.0 |
| hvac-hp HP Heating Coil Cap-FF | 0.84 | 0.16 | 0.0 | 0.0 | 0.5 | 1.5 |
| hvac-hp HP Heating Coil EIR-FT | 1.19248 | -0.0300438 | 0.00103745 | -0.000023328 | -20.0 | 20.0 |

## 5. Output requests (not in the documents)

`Output:Variable` (6 objects)

| Key Value | Variable Name | Reporting Frequency |
|---|---|---|
| * | Site Outdoor Air Drybulb Temperature | Hourly |
| * | Zone Mean Air Temperature | Hourly |
| * | Zone Air Relative Humidity | Hourly |
| * | Zone Air System Sensible Heating Energy | Hourly |
| * | Zone Air System Sensible Cooling Energy | Hourly |
| * | Facility Total Purchased Electricity Energy | Hourly |

`Output:Meter` (2 objects)

| Key Name | Reporting Frequency |
|---|---|
| Electricity:Facility | Hourly |
| NaturalGas:Facility | Hourly |

`Output:Table:SummaryReports` (1 object)

| Report Name 1 |
|---|
| AllSummary |

`OutputControl:Table:Style` (1 object)

| Column Separator |
|---|
| CommaAndHTML |

`Output:SQLite` (1 object)

| Option Type |
|---|
| SimpleAndTabular |
