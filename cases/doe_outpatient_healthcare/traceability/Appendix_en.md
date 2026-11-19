# Appendix (natural language): DOE Outpatient Healthcare, Short IDF, Buffalo

Target IDF: `DOE/Outpatient_Healthcare/Short/DOE_OutPatientHealthCare_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas, the number of floors and the floor height; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A three-storey outpatient clinic, **51.82 m x 35.36 m** (170 ft x 116 ft) in plan (the footprint is the prototype's; xlsx Building Summary: 3 floors; PDF Table 13: 40,946 ft2, aspect ratio 1.4, floor-to-floor height 10 ft), 3804 m2 of floor in 118 zones, all with multiplier 1. Local coordinates start at the south-west corner of the building: x to the east, y to the north, z up (`GlobalGeometryRules`: upper-left corner, counterclockwise, relative). Every zone has an origin (`Zone` fields X, Y, Z Origin, in building coordinates) and the vertices of its surfaces are relative to that origin, so a zone is described by its origin and the sizes of its rectangle; the zone tables below give the extents in building coordinates. The building is made of small rooms, halls, toilets and rooms for equipment (for example `Floor 1 Operating Room 1`, `Floor 2 Office`, `Floor 3 Lobby`; see the zone table):

* **Floor 1** (z = 0.00 to 3.05 m, 10 ft): 55 zones, 1318 m2 of floor; e.g. `Floor 1 Anesthesia`, `Floor 1 Bio Haz`, `Floor 1 Cafe`, `Floor 1 Clean`, `Floor 1 Clean Work`, `Floor 1 Dictation`, ...
* **Floor 2** (z = 3.05 to 6.10 m, 10 ft): 37 zones, 1215 m2 of floor; e.g. `Floor 2 Conference`, `Floor 2 Conference Toilet`, `Floor 2 Dictation`, `Floor 2 Exam 1`, `Floor 2 Exam 2`, `Floor 2 Exam 3`, ...
* **Floor 3** (z = 6.10 to 9.14 m, 10 ft): 22 zones, 1215 m2 of floor; e.g. `Floor 3 Dressing Room`, `Floor 3 Elevator Hall`, `Floor 3 Humid`, `Floor 3 Janitor`, `Floor 3 Locker`, `Floor 3 Lounge`, ...
* **Stairs and elevators** (z = 0.00 to 9.14 m, 30 ft; the shafts run over all three floors): 4 zones, 55 m2 of floor; e.g. `NE Stair`, `NW Elevator`, `NW Stair`, `SW Stair`

* **Surfaces**: 86 exterior wall surfaces (`ExteriorWall`) and 29 roof surfaces (`Roof`) face outdoors; every other wall is an interior wall (boundary condition `Surface`, construction `GenericSurface`, a pair of reversed polygons); the floors and ceilings between the storeys are interior surfaces with the generic construction. The 59 floors of the first floor have each their own slab-on-grade construction (F-factor method, `Construction:FfactorGroundFloor`): 30 of them are in contact with the ground, 29 have the boundary condition `Adiabatic`.
* **Windows** (construction `Window`): 94 fenestration surfaces with together 308.36 m2 (the xlsx window glass area is 308.36 m2). There are no swinging doors in this IDF.

| Zone | Origin x, y, z m | x range m | y range m | z range m | Floor polygon area m2 | HVAC template |
|---|---|---|---|---|---|---|
| Floor 1 Anesthesia | 39.32, 0.00, 0.00 | 39.32 to 42.06 | 0.00 to 3.66 | 0.00 to 3.05 | 10.0 | HVAC |
| Floor 1 Bio Haz | 39.32, 25.91, 0.00 | 39.93 to 42.06 | 25.91 to 28.35 | 0.00 to 3.05 | 5.2 | HVAC |
| Floor 1 Cafe | 0.00, 19.20, 0.00 | 5.79 to 11.89 | 9.14 to 15.54 | 0.00 to 3.05 | 39.0 | HVAC |
| Floor 1 Clean | 29.26, 8.84, 0.00 | 29.26 to 32.00 | 8.84 to 13.11 | 0.00 to 3.05 | 11.7 | HVAC |
| Floor 1 Clean Work | 42.06, 9.75, 0.00 | 37.49 to 42.06 | 9.75 to 13.11 | 0.00 to 3.05 | 15.3 | HVAC |
| Floor 1 Dictation | 32.00, 8.84, 0.00 | 32.00 to 34.75 | 8.84 to 13.11 | 0.00 to 3.05 | 11.7 | HVAC |
| Floor 1 Dressing Room | 15.54, 28.35, 0.00 | 12.80 to 15.54 | 26.82 to 28.35 | 0.00 to 3.05 | 4.2 | HVAC |
| Floor 1 Electrical Room | 50.60, 18.59, 0.00 | 46.33 to 50.60 | 18.59 to 20.73 | 0.00 to 3.05 | 9.1 | HVAC |
| Floor 1 Elevator Pump Room | 3.96, 28.35, 0.00 | 0.00 to 3.96 | 26.21 to 28.35 | 0.00 to 3.05 | 8.5 | HVAC |
| Floor 1 Humid | 32.00, 14.94, 0.00 | 29.26 to 32.00 | 13.11 to 14.94 | 0.00 to 3.05 | 5.0 | HVAC |
| Floor 1 IT Hall | 33.53, 25.91, 0.00 | 33.53 to 42.06 | 24.38 to 25.91 | 0.00 to 3.05 | 13.0 | HVAC |
| Floor 1 IT Room | 37.19, 28.35, 0.00 | 33.53 to 37.80 | 25.91 to 28.35 | 0.00 to 3.05 | 10.4 | HVAC |
| Floor 1 Lobby | 2.13, 24.38, 0.00 | 2.13 to 6.40 | 11.58 to 28.35 | 0.00 to 3.05 | 57.8 | HVAC |
| Floor 1 Lobby Hall | 11.89, 19.20, 0.00 | 5.79 to 11.89 | 15.54 to 19.20 | 0.00 to 3.05 | 22.3 | HVAC |
| Floor 1 Lobby Toilet | 0.00, 26.21, 0.00 | 0.00 to 2.74 | 24.38 to 26.21 | 0.00 to 3.05 | 5.0 | HVAC |
| Floor 1 Locker Room | 29.87, 28.35, 0.00 | 23.16 to 29.87 | 19.20 to 28.35 | 0.00 to 3.05 | 61.3 | HVAC |
| Floor 1 Locker Room Hall | 23.16, 19.20, 0.00 | 23.16 to 42.06 | 16.76 to 19.20 | 0.00 to 3.05 | 46.1 | HVAC |
| Floor 1 Lounge | 29.87, 19.20, 0.00 | 29.87 to 33.53 | 19.20 to 28.35 | 0.00 to 3.05 | 33.4 | HVAC |
| Floor 1 Med Gas | 44.50, 33.22, 0.00 | 42.06 to 44.50 | 33.22 to 35.36 | 0.00 to 3.05 | 5.2 | HVAC |
| Floor 1 MRI Control Room | 12.80, 28.35, 0.00 | 6.40 to 12.80 | 25.91 to 28.35 | 0.00 to 3.05 | 15.6 | HVAC |
| Floor 1 MRI Hall | 11.89, 25.91, 0.00 | 11.89 to 17.37 | 23.77 to 26.82 | 0.00 to 3.05 | 13.7 | HVAC |
| Floor 1 MRI Room | 6.71, 25.91, 0.00 | 5.79 to 11.89 | 19.20 to 25.91 | 0.00 to 3.05 | 40.9 | HVAC |
| Floor 1 MRI Toilet | 17.37, 28.35, 0.00 | 15.54 to 17.37 | 25.60 to 28.35 | 0.00 to 3.05 | 5.0 | HVAC |
| Floor 1 Nourishment | 27.13, 16.76, 0.00 | 27.13 to 29.26 | 8.84 to 16.76 | 0.00 to 3.05 | 16.9 | HVAC |
| Floor 1 Nurse Hall | 39.32, 3.66, 0.00 | 23.16 to 42.06 | 3.66 to 6.10 | 0.00 to 3.05 | 46.1 | HVAC |
| Floor 1 Nurse Janitor | 29.26, 16.76, 0.00 | 29.26 to 32.00 | 14.94 to 16.76 | 0.00 to 3.05 | 5.0 | HVAC |
| Floor 1 Nurse Station | 32.00, 8.84, 0.00 | 23.16 to 32.00 | 6.10 to 8.84 | 0.00 to 3.05 | 24.2 | HVAC |
| Floor 1 Nurse Toilet | 37.49, 8.84, 0.00 | 35.66 to 37.49 | 6.10 to 8.84 | 0.00 to 3.05 | 5.0 | HVAC |
| Floor 1 Office | 14.63, 15.85, 0.00 | 14.33 to 20.73 | 16.76 to 23.77 | 0.00 to 3.05 | 44.9 | HVAC |
| Floor 1 Operating Room 1 | 44.81, 0.00, 0.00 | 44.50 to 50.60 | 0.00 to 7.01 | 0.00 to 3.05 | 42.7 | HVAC |
| Floor 1 Operating Room 2 | 50.60, 11.28, 0.00 | 44.50 to 50.60 | 11.28 to 18.59 | 0.00 to 3.05 | 44.6 | HVAC |
| Floor 1 Operating Room 3 | 33.53, 19.20, 0.00 | 33.53 to 42.06 | 19.20 to 24.38 | 0.00 to 3.05 | 44.2 | HVAC |
| Floor 1 PACU | 35.66, 8.84, 0.00 | 32.00 to 35.66 | 6.10 to 8.84 | 0.00 to 3.05 | 10.0 | HVAC |
| Floor 1 Pre-Op Hall | 20.73, 23.77, 0.00 | 20.73 to 23.16 | 3.66 to 23.77 | 0.00 to 3.05 | 49.1 | HVAC |
| Floor 1 Pre-Op Room 1 | 17.98, 13.41, 0.00 | 17.98 to 20.73 | 7.92 to 14.33 | 0.00 to 3.05 | 17.6 | HVAC |
| Floor 1 Pre-Op Room 2 | 24.38, 8.84, 0.00 | 23.16 to 27.13 | 8.84 to 16.76 | 0.00 to 3.05 | 31.4 | HVAC |
| Floor 1 Pre-Op Toilet | 17.98, 5.49, 0.00 | 17.98 to 20.73 | 3.66 to 5.49 | 0.00 to 3.05 | 5.0 | HVAC |
| Floor 1 Procedure Room | 22.86, 28.35, 0.00 | 17.37 to 23.16 | 23.77 to 28.35 | 0.00 to 3.05 | 26.5 | HVAC |
| Floor 1 Reception | 9.75, 9.14, 0.00 | 11.89 to 15.85 | 9.14 to 23.77 | 0.00 to 3.05 | 47.3 | HVAC |
| Floor 1 Reception Hall | 20.73, 14.33, 0.00 | 15.85 to 20.73 | 14.33 to 16.76 | 0.00 to 3.05 | 11.9 | HVAC |
| Floor 1 Recovery Room | 20.42, 0.00, 0.00 | 25.60 to 39.32 | 0.00 to 3.66 | 0.00 to 3.05 | 50.2 | HVAC |
| Floor 1 Scheduling | 15.85, 9.14, 0.00 | 15.85 to 17.98 | 9.14 to 14.33 | 0.00 to 3.05 | 11.1 | HVAC |
| Floor 1 Scrub | 44.50, 11.28, 0.00 | 44.50 to 46.33 | 7.01 to 11.28 | 0.00 to 3.05 | 7.8 | HVAC |
| Floor 1 Soil | 34.75, 13.11, 0.00 | 34.75 to 37.49 | 8.84 to 13.11 | 0.00 to 3.05 | 11.7 | HVAC |
| Floor 1 Soil Hold | 37.19, 25.91, 0.00 | 37.80 to 39.93 | 25.91 to 28.35 | 0.00 to 3.05 | 5.2 | HVAC |
| Floor 1 Soil Work | 42.06, 6.10, 0.00 | 37.49 to 42.06 | 6.10 to 9.75 | 0.00 to 3.05 | 16.7 | HVAC |
| Floor 1 Step Down | 20.42, 0.00, 0.00 | 17.98 to 25.60 | 0.00 to 3.66 | 0.00 to 3.05 | 27.9 | HVAC |
| Floor 1 Sterile Hall | 42.06, 0.00, 0.00 | 42.06 to 44.50 | 0.00 to 23.47 | 0.00 to 3.05 | 57.2 | HVAC |
| Floor 1 Sterile Storage | 32.00, 13.11, 0.00 | 32.00 to 42.06 | 13.11 to 16.76 | 0.00 to 3.05 | 36.8 | HVAC |
| Floor 1 Storage | 41.45, 35.36, 0.00 | 29.87 to 42.06 | 28.35 to 35.36 | 0.00 to 3.05 | 85.5 | HVAC |
| Floor 1 Sub-Sterile | 50.60, 7.01, 0.00 | 46.33 to 50.60 | 7.01 to 11.28 | 0.00 to 3.05 | 18.2 | HVAC |
| Floor 1 Utility Hall | 44.50, 28.96, 0.00 | 42.06 to 44.50 | 23.47 to 33.22 | 0.00 to 3.05 | 23.8 | HVAC |
| Floor 1 Utility Janitor | 44.50, 20.73, 0.00 | 44.50 to 46.33 | 18.59 to 20.73 | 0.00 to 3.05 | 3.9 | HVAC |
| Floor 1 Utility Room | 50.60, 20.73, 0.00 | 44.50 to 50.60 | 20.73 to 26.21 | 0.00 to 3.05 | 33.4 | HVAC |
| Floor 1 Vestibule | 17.98, 7.92, 0.00 | 17.98 to 20.73 | 5.49 to 7.92 | 0.00 to 3.05 | 6.7 | HVAC |
| Floor 2 Conference | 50.60, 0.00, 3.05 | 42.06 to 50.60 | 0.00 to 3.66 | 3.05 to 6.10 | 31.2 | HVAC |
| Floor 2 Conference Toilet | 44.50, 6.10, 3.05 | 42.06 to 44.50 | 3.66 to 6.10 | 3.05 to 6.10 | 5.9 | HVAC |
| Floor 2 Dictation | 42.06, 9.14, 3.05 | 39.93 to 42.06 | 6.10 to 9.14 | 3.05 to 6.10 | 6.5 | HVAC |
| Floor 2 Exam 1 | 17.98, 0.00, 3.05 | 17.98 to 21.64 | 0.00 to 9.14 | 3.05 to 6.10 | 33.4 | HVAC |
| Floor 2 Exam 2 | 23.47, 0.00, 3.05 | 23.47 to 28.96 | 0.00 to 9.14 | 3.05 to 6.10 | 50.2 | HVAC |
| Floor 2 Exam 3 | 30.78, 0.00, 3.05 | 30.78 to 38.10 | 0.00 to 9.14 | 3.05 to 6.10 | 66.9 | HVAC |
| Floor 2 Exam 4 | 39.93, 0.00, 3.05 | 39.93 to 42.06 | 0.00 to 3.66 | 3.05 to 6.10 | 7.8 | HVAC |
| Floor 2 Exam 5 | 50.60, 18.59, 3.05 | 46.33 to 50.60 | 18.59 to 26.21 | 3.05 to 6.10 | 32.5 | HVAC |
| Floor 2 Exam 6 | 44.50, 28.35, 3.05 | 39.93 to 44.50 | 23.77 to 28.35 | 3.05 to 6.10 | 20.9 | HVAC |
| Floor 2 Exam 7 | 38.10, 28.35, 3.05 | 30.78 to 38.10 | 18.29 to 28.35 | 3.05 to 6.10 | 73.6 | HVAC |
| Floor 2 Exam 8 | 28.96, 28.35, 3.05 | 23.47 to 28.96 | 23.77 to 28.35 | 3.05 to 6.10 | 25.1 | HVAC |
| Floor 2 Exam 9 | 21.64, 28.35, 3.05 | 17.98 to 21.64 | 18.29 to 28.35 | 3.05 to 6.10 | 36.8 | HVAC |
| Floor 2 Exam Hall 1 | 21.64, 0.00, 3.05 | 21.64 to 23.47 | 0.00 to 9.14 | 3.05 to 6.10 | 16.7 | HVAC |
| Floor 2 Exam Hall 2 | 28.96, 0.00, 3.05 | 28.96 to 30.78 | 0.00 to 9.14 | 3.05 to 6.10 | 16.7 | HVAC |
| Floor 2 Exam Hall 3 | 38.10, 0.00, 3.05 | 38.10 to 39.93 | 0.00 to 9.14 | 3.05 to 6.10 | 16.7 | HVAC |
| Floor 2 Exam Hall 4 | 39.93, 28.35, 3.05 | 38.10 to 39.93 | 18.29 to 28.35 | 3.05 to 6.10 | 18.4 | HVAC |
| Floor 2 Exam Hall 5 | 30.78, 28.35, 3.05 | 28.96 to 30.78 | 18.29 to 28.35 | 3.05 to 6.10 | 18.4 | HVAC |
| Floor 2 Exam Hall 6 | 23.47, 28.35, 3.05 | 21.64 to 23.47 | 18.29 to 28.35 | 3.05 to 6.10 | 18.4 | HVAC |
| Floor 2 Janitor | 0.00, 28.35, 3.05 | 0.00 to 2.74 | 26.21 to 28.35 | 3.05 to 6.10 | 5.9 | HVAC |
| Floor 2 Lounge | 44.50, 9.14, 3.05 | 42.06 to 44.50 | 6.10 to 9.14 | 3.05 to 6.10 | 7.4 | HVAC |
| Floor 2 Nurse Station 1 | 39.01, 21.34, 3.05 | 39.93 to 44.50 | 18.29 to 21.34 | 3.05 to 6.10 | 13.9 | HVAC |
| Floor 2 Nurse Station 2 | 23.47, 21.34, 3.05 | 23.47 to 28.96 | 18.29 to 21.34 | 3.05 to 6.10 | 16.7 | HVAC |
| Floor 2 Office | 50.60, 3.66, 3.05 | 46.33 to 50.60 | 3.66 to 15.85 | 3.05 to 6.10 | 52.0 | HVAC |
| Floor 2 Office Hall | 46.33, 3.66, 3.05 | 44.50 to 46.33 | 3.66 to 26.21 | 3.05 to 6.10 | 41.2 | HVAC |
| Floor 2 Reception | 2.13, 16.46, 3.05 | 2.13 to 15.85 | 9.14 to 16.46 | 3.05 to 6.10 | 91.4 | HVAC |
| Floor 2 Reception Hall | 17.98, 9.14, 3.05 | 15.85 to 44.50 | 9.14 to 10.97 | 3.05 to 6.10 | 52.4 | HVAC |
| Floor 2 Reception Toilet | 17.98, 10.97, 3.05 | 15.85 to 17.98 | 10.97 to 16.46 | 3.05 to 6.10 | 11.7 | HVAC |
| Floor 2 Scheduling 1 | 44.50, 16.46, 3.05 | 39.01 to 44.50 | 10.97 to 16.46 | 3.05 to 6.10 | 30.1 | HVAC |
| Floor 2 Scheduling 2 | 23.77, 16.46, 3.05 | 17.98 to 23.77 | 10.97 to 16.46 | 3.05 to 6.10 | 31.8 | HVAC |
| Floor 2 Storage 1 | 42.06, 3.66, 3.05 | 39.93 to 42.06 | 3.66 to 6.10 | 3.05 to 6.10 | 5.2 | HVAC |
| Floor 2 Storage 2 | 39.01, 23.77, 3.05 | 39.93 to 44.50 | 21.34 to 23.77 | 3.05 to 6.10 | 11.1 | HVAC |
| Floor 2 Storage 3 | 23.47, 21.34, 3.05 | 23.47 to 28.96 | 21.34 to 23.77 | 3.05 to 6.10 | 13.4 | HVAC |
| Floor 2 Utility | 50.60, 18.59, 3.05 | 46.33 to 50.60 | 15.85 to 18.59 | 3.05 to 6.10 | 11.7 | HVAC |
| Floor 2 Work | 17.98, 28.35, 3.05 | 2.13 to 17.98 | 18.29 to 28.35 | 3.05 to 6.10 | 157.0 | HVAC |
| Floor 2 Work Hall | 44.50, 16.46, 3.05 | 2.13 to 44.50 | 16.46 to 18.29 | 3.05 to 6.10 | 77.5 | HVAC |
| Floor 2 Work Toilet | 0.00, 26.21, 3.05 | 0.00 to 2.74 | 24.38 to 26.21 | 3.05 to 6.10 | 5.0 | HVAC |
| Floor 2 X-Ray | 39.01, 16.46, 3.05 | 23.77 to 39.01 | 10.97 to 16.46 | 3.05 to 6.10 | 83.6 | HVAC |
| Floor 3 Dressing Room | 39.01, 10.97, 6.10 | 36.88 to 39.01 | 10.97 to 12.80 | 6.10 to 9.14 | 3.9 | HVAC |
| Floor 3 Elevator Hall | 5.79, 28.35, 6.10 | 2.13 to 5.79 | 18.29 to 28.35 | 6.10 to 9.14 | 34.4 | HVAC |
| Floor 3 Humid | 35.05, 16.46, 6.10 | 35.05 to 36.88 | 10.97 to 16.46 | 6.10 to 9.14 | 10.0 | HVAC |
| Floor 3 Janitor | 0.00, 28.35, 6.10 | 0.00 to 2.74 | 26.21 to 28.35 | 6.10 to 9.14 | 5.9 | HVAC |
| Floor 3 Locker | 37.49, 20.42, 6.10 | 33.83 to 37.49 | 20.42 to 23.47 | 6.10 to 9.14 | 11.1 | HVAC |
| Floor 3 Lounge | 37.49, 28.35, 6.10 | 37.49 to 44.50 | 18.29 to 28.35 | 6.10 to 9.14 | 70.5 | HVAC |
| Floor 3 Lounge Toilet | 33.83, 23.47, 6.10 | 33.83 to 37.49 | 23.47 to 28.35 | 6.10 to 9.14 | 17.8 | HVAC |
| Floor 3 Mechanical | 50.60, 18.59, 6.10 | 46.33 to 50.60 | 18.59 to 26.21 | 6.10 to 9.14 | 32.5 | HVAC |
| Floor 3 Mechanical Hall | 46.33, 3.66, 6.10 | 44.50 to 46.33 | 10.97 to 26.21 | 6.10 to 9.14 | 27.9 | HVAC |
| Floor 3 Office | 33.83, 28.35, 6.10 | 5.79 to 33.83 | 18.29 to 28.35 | 6.10 to 9.14 | 282.1 | HVAC |
| Floor 3 Office Hall | 2.13, 16.46, 6.10 | 2.13 to 44.50 | 16.46 to 18.29 | 6.10 to 9.14 | 77.5 | HVAC |
| Floor 3 Office Toilet | 0.00, 24.38, 6.10 | 0.00 to 2.74 | 24.38 to 26.21 | 6.10 to 9.14 | 5.0 | HVAC |
| Floor 3 Physical Therapy 1 | 50.60, 0.00, 6.10 | 30.78 to 50.60 | 0.00 to 6.10 | 6.10 to 9.14 | 120.8 | HVAC |
| Floor 3 Physical Therapy 2 | 35.05, 10.97, 6.10 | 35.05 to 46.33 | 6.10 to 10.97 | 6.10 to 9.14 | 55.0 | HVAC |
| Floor 3 Physical Therapy Toilet | 39.01, 10.97, 6.10 | 36.88 to 39.01 | 12.80 to 16.46 | 6.10 to 9.14 | 7.8 | HVAC |
| Floor 3 Storage 1 | 39.01, 10.97, 6.10 | 39.01 to 44.50 | 10.97 to 12.80 | 6.10 to 9.14 | 10.0 | HVAC |
| Floor 3 Storage 2 | 37.49, 18.29, 6.10 | 33.83 to 37.49 | 18.29 to 20.42 | 6.10 to 9.14 | 7.8 | HVAC |
| Floor 3 Treatment | 30.78, 0.00, 6.10 | 30.78 to 35.05 | 6.10 to 16.46 | 6.10 to 9.14 | 44.2 | HVAC |
| Floor 3 Undeveloped 1 | 17.98, 0.00, 6.10 | 17.98 to 30.78 | 0.00 to 16.46 | 6.10 to 9.14 | 210.7 | HVAC |
| Floor 3 Undeveloped 2 | 2.13, 11.58, 6.10 | 2.13 to 17.98 | 9.14 to 16.46 | 6.10 to 9.14 | 107.0 | HVAC |
| Floor 3 Utility | 39.01, 16.46, 6.10 | 39.01 to 44.50 | 12.80 to 16.46 | 6.10 to 9.14 | 20.1 | HVAC |
| Floor 3 Work | 50.60, 18.59, 6.10 | 46.33 to 50.60 | 6.10 to 18.59 | 6.10 to 9.14 | 53.3 | HVAC |
| NE Stair | 51.82, 26.21, 0.00 | 44.50 to 51.82 | 26.21 to 28.35 | 0.00 to 9.14 | 15.6 | HVAC |
| NW Elevator | 0.00, 24.38, 0.00 | 0.00 to 2.13 | 18.29 to 24.38 | 0.00 to 9.14 | 13.0 | HVAC |
| NW Stair | 12.80, 28.35, 0.00 | 3.96 to 11.28 | 28.35 to 30.78 | 0.00 to 9.14 | 17.8 | HVAC |
| SW Stair | 0.91, 11.58, 0.00 | 2.13 to 5.79 | 9.14 to 11.58 | 0.00 to 9.14 | 8.9 | HVAC |

The IDF has 1160 building surfaces: 200 ceiling (surface), 29 floor (adiabatic), 30 floor (groundfcfactormethod), 200 floor (surface), 29 roof (outdoors), 86 wall (outdoors), 586 wall (surface). The vertex coordinates are in `Appendix_IDF.txt`. The floor polygon area is the sum of the surfaces of type Floor of the zone.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per zone that has a value in the xlsx raw_data sheet (the zone names are those of the IDF; the xlsx writes them in capital letters). All fields not named here are empty (EnergyPlus default). Every schedule is a `Schedule:Compact` written from the xlsx sheet Schedule Summary rows (Mon - Fri, Sat, Sun). The occupancy schedule of a zone is the one of its space type in the xlsx: `OFFICE_OCC_SCH` for the zones named Dictation, Dressing Room, Humid, IT Room, Office, Scheduling and Work (with the floor prefix and a number at the end allowed), `CONFERENCE_OCC_SCH` for the conference room and `BLDG_OCC_SCH` for all others.

* **`People`**: name `<zone>_People`; method `Area/Person`; floor area per person = xlsx raw_data column M; activity level schedule `ACTIVITY_SCH`. Schedules:

| Schedule | Zones |
|---|---|
| BLDG_OCC_SCH | Floor 1 Anesthesia, Floor 1 Bio Haz, Floor 1 Cafe, ... (102 zones) |
| OFFICE_OCC_SCH | Floor 1 Dictation, Floor 1 Dressing Room, Floor 1 Humid, ... (15 zones) |
| CONFERENCE_OCC_SCH | Floor 2 Conference |

* **`Lights`**: name `<zone>_Lights`; method `Watts/Area`; watts per floor area = xlsx raw_data column L; schedule `BLDG_LIGHT_SCH` (xlsx row Lighting, All).

* **`ElectricEquipment`**: name `<zone>_Equipment`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process); schedule `BLDG_EQUIP_SCH` (xlsx row Electric Equipment, All).

* **`GasEquipment`**: `Floor 1 Operating Room 1_Gas_Equipment`, `Floor 1 Operating Room 2_Gas_Equipment`, `Floor 1 Operating Room 3_Gas_Equipment`; method `EquipmentLevel`; design level = xlsx raw_data column O (gas power, W); schedule `OR_GAS_EQUIP_SCH` (xlsx row Gas Equipment, Operating Room).

* **`ZoneInfiltration:DesignFlowRate`**: name `<zone>_Infiltration` for every zone that has a value in xlsx raw_data column R (flow per exterior surface area); method `Flow/ExteriorWallArea`; schedule `INFIL_SCH` (xlsx row Infiltration, All). The columns S and T (zone flow, entrances) are 0 in the xlsx.

* **`HVACTemplate:Thermostat`**: `ORThermostat` (heating schedule `OR_HTGSETP_SCH`, cooling schedule `OR_CLGSETP_SCH`); `OthersThermostat` (heating schedule `HTGSETP_SCH`, cooling schedule `CLGSETP_SCH`) (xlsx Schedule Summary, Heating / Cooling Set Point, space types OR and Others). The operating rooms use `ORThermostat`, all other zones `OthersThermostat`.

* **`HVACTemplate:System:VAV`** (2 objects, named by xlsx raw_data column I: `AHU-1`, `AHU-2`): availability schedule `HVACOperationSchd`; cooling coil type `ChilledWater`; heating coil type `HotWater`; economizer type `NoEconomizer`.

* **`HVACTemplate:Zone:VAV`** (118 objects, every zone): zone name; template system = the VAV system named in raw_data column I (`AHU-1` or `AHU-2`); thermostat as above; outdoor air method `Flow/Area` with the outdoor air per floor area that follows from the xlsx sheet Zone and HVAC System Summary (Total OSA Ventilation: cfm/person x people, cfm/ft2 or cfm/zone; it equals raw_data column P divided by the floor area); reheat coil type `HotWater`.

The plant loops (one chilled water loop with a chiller and a tower, one hot water loop with a boiler) are in `Appendix_IDF.txt`: the xlsx names the system type only; the chiller type and COP are required by EnergyPlus and are not in the documents. The wall and roof constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.084 Btu/h-ft2-F (Table 20, steel frame wall; Table 18) and roof U = 0.063 (Table 19, insulation entirely above deck; Table 17), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25); the slab F-factor 1.26363 W/m-K is the 90.1-2004 value of an uninsulated slab (Table 22: no insulation required).
