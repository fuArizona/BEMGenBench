# Appendix (natural language): DOE High-rise Apartment, Short IDF, Buffalo

Target IDF: `DOE/High-rise_Apartment/Short/DOE_ApartmentHighRise_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A 10-storey apartment building, **46.33 m x 16.92 m** (152.0 ft x 55.5 ft) in plan, 30.48 m high (the PDF has no High-rise Apartment), 7836 m2 of floor in 27 zones. Local coordinates start at the south-west corner of the building: x to the east (the long side), y to the north, z up. `GlobalGeometryRules`: UpperLeftCorner, Counterclockwise, relative. **The vertices of the surfaces are relative to the origin of their zone** (the `Zone` fields X, Y, Z Origin give the origins). All coordinates are feet x 0.3048 x a scale factor k; the comment of every vertex shows the calculation, the block `Vertex formulas of the ...` explains the symbols and gives k.

Three levels are modelled (ground, middle, top); the middle level stands for 8 floors by the zone multiplier (the other floors of the building have the same zones):

* **Level 1**: z = 0.00 to 3.05 m, 9 zones, zone multiplier 1.
* **Level 2**: z = 12.19 to 15.24 m, 9 zones, zone multiplier 8.
* **Level 3**: z = 27.43 to 30.48 m, 9 zones, zone multiplier 1.

Each level is one long block: a row of 4 zones along the south wall (y = 0.00 to 7.62 m), a corridor (7.62 to 9.30 m, 46.33 m long) and a row of 4 zones along the north wall (y = 9.30 to 16.92 m). Each apartment is 11.58 m (38 ft) wide. On the ground level the south row from west to east is `G SW Apartment`, `G S1 Apartment`, `G S2 Apartment`, `Office` (the office is `Office`), the north row `G NW Apartment`, `G N1 Apartment`, `G N2 Apartment`, `G NE Apartment`. The upper levels have the same layout with the apartments only.

* **Surfaces**: the exterior walls (`ExteriorWall`) and the flat roofs (`Roof`) face outdoors; the floors of the ground level are slab on grade (F-factor method, `Construction:FfactorGroundFloor`); the walls between zones and the floors and ceilings between levels are interior surfaces (reversed pairs of surfaces of the construction `GenericSurface`).
* **Windows** (construction `Window`): 42 windows with together 346.69 m2 on the outer walls (the xlsx window glass area is the sum of column K, 306.9 m2 with the multipliers). There are no doors in this IDF.

| Zone | Multiplier | Origin x, y, z m | x range m | y range m | z range m | Floor polygon area m2 | HVAC template |
|---|---|---|---|---|---|---|---|
| G SW Apartment | 1 | 0.00, 0.00, 0.00 | 0.00 to 11.58 | 0.00 to 7.62 | 0.00 to 3.05 | 88.2 | HVAC |
| G NW Apartment | 1 | 0.00, 9.30, 0.00 | 0.00 to 11.58 | 9.30 to 16.92 | 0.00 to 3.05 | 88.2 | HVAC |
| Office | 1 | 34.75, 0.00, 0.00 | 34.75 to 46.33 | 0.00 to 7.62 | 0.00 to 3.05 | 88.2 | HVAC |
| G NE Apartment | 1 | 34.75, 9.30, 0.00 | 34.75 to 46.33 | 9.30 to 16.92 | 0.00 to 3.05 | 88.2 | HVAC |
| G N1 Apartment | 1 | 11.58, 9.30, 0.00 | 11.58 to 23.16 | 9.30 to 16.92 | 0.00 to 3.05 | 88.2 | HVAC |
| G N2 Apartment | 1 | 23.16, 9.30, 0.00 | 23.16 to 34.75 | 9.30 to 16.92 | 0.00 to 3.05 | 88.2 | HVAC |
| G S1 Apartment | 1 | 11.58, 0.00, 0.00 | 11.58 to 23.16 | 0.00 to 7.62 | 0.00 to 3.05 | 88.2 | HVAC |
| G S2 Apartment | 1 | 23.16, 0.00, 0.00 | 23.16 to 34.75 | 0.00 to 7.62 | 0.00 to 3.05 | 88.2 | HVAC |
| G Corridor | 1 | 0.00, 7.62, 0.00 | 0.00 to 46.33 | 7.62 to 9.30 | 0.00 to 3.05 | 77.7 | none |
| M SW Apartment | 8 | 0.00, 0.00, 12.19 | 0.00 to 11.58 | 0.00 to 7.62 | 12.19 to 15.24 | 88.2 | HVAC |
| M NW Apartment | 8 | 0.00, 9.30, 12.19 | 0.00 to 11.58 | 9.30 to 16.92 | 12.19 to 15.24 | 88.2 | HVAC |
| M SE Apartment | 8 | 34.75, 0.00, 12.19 | 34.75 to 46.33 | 0.00 to 7.62 | 12.19 to 15.24 | 88.2 | HVAC |
| M NE Apartment | 8 | 34.75, 9.30, 12.19 | 34.75 to 46.33 | 9.30 to 16.92 | 12.19 to 15.24 | 88.2 | HVAC |
| M N1 Apartment | 8 | 11.58, 9.30, 12.19 | 11.58 to 23.16 | 9.30 to 16.92 | 12.19 to 15.24 | 88.2 | HVAC |
| M N2 Apartment | 8 | 23.16, 9.30, 12.19 | 23.16 to 34.75 | 9.30 to 16.92 | 12.19 to 15.24 | 88.2 | HVAC |
| M S1 Apartment | 8 | 11.58, 0.00, 12.19 | 11.58 to 23.16 | 0.00 to 7.62 | 12.19 to 15.24 | 88.2 | HVAC |
| M S2 Apartment | 8 | 23.16, 0.00, 12.19 | 23.16 to 34.75 | 0.00 to 7.62 | 12.19 to 15.24 | 88.2 | HVAC |
| M Corridor | 8 | 0.00, 7.62, 12.19 | 0.00 to 46.33 | 7.62 to 9.30 | 12.19 to 15.24 | 77.7 | none |
| T SW Apartment | 1 | 0.00, 0.00, 27.43 | 0.00 to 11.58 | 0.00 to 7.62 | 27.43 to 30.48 | 88.2 | HVAC |
| T NW Apartment | 1 | 0.00, 9.30, 27.43 | 0.00 to 11.58 | 9.30 to 16.92 | 27.43 to 30.48 | 88.2 | HVAC |
| T SE Apartment | 1 | 34.75, 0.00, 27.43 | 34.75 to 46.33 | 0.00 to 7.62 | 27.43 to 30.48 | 88.2 | HVAC |
| T NE Apartment | 1 | 34.75, 9.30, 27.43 | 34.75 to 46.33 | 9.30 to 16.92 | 27.43 to 30.48 | 88.2 | HVAC |
| T N1 Apartment | 1 | 11.58, 9.30, 27.43 | 11.58 to 23.16 | 9.30 to 16.92 | 27.43 to 30.48 | 88.2 | HVAC |
| T N2 Apartment | 1 | 23.16, 9.30, 27.43 | 23.16 to 34.75 | 9.30 to 16.92 | 27.43 to 30.48 | 88.2 | HVAC |
| T S1 Apartment | 1 | 11.58, 0.00, 27.43 | 11.58 to 23.16 | 0.00 to 7.62 | 27.43 to 30.48 | 88.2 | HVAC |
| T S2 Apartment | 1 | 23.16, 0.00, 27.43 | 23.16 to 34.75 | 0.00 to 7.62 | 27.43 to 30.48 | 88.2 | HVAC |
| T Corridor | 1 | 0.00, 7.62, 27.43 | 0.00 to 46.33 | 7.62 to 9.30 | 27.43 to 30.48 | 77.7 | none |

The IDF has 138 building surfaces: 18 ceiling (surface), 9 floor (groundfcfactormethod), 18 floor (surface), 9 roof (outdoors), 42 wall (outdoors), 42 wall (zone). The vertex coordinates are in `Appendix_IDF.txt`.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per zone that has a value in the xlsx raw_data sheet (the zone names are those of the IDF; the xlsx writes them in capital letters). All fields not named here are empty (EnergyPlus default). The schedule of a zone is the one of its space type in the xlsx sheet Schedule Summary; where the xlsx gives none for a load the schedule `AlwaysOn` (when the schedule of the prototype is constant 1) or `AlwaysOff` is written; the schedule names are the names of the `Schedule:Compact` objects of `Appendix_IDF.txt`.

* **`People`**: name `<zone>_People`; method `Area/Person`; floor area per person = xlsx raw_data column M; activity level schedule `ACTIVITY_SCH`. Schedules:

| Schedule | Zones |
|---|---|
| OCC_APT_SCH_WORKING_FAMILY | G SW Apartment, G S1 Apartment, G S2 Apartment, M SW Apartment, M SE Apartment, M S1 Apartment, M S2 Apartment, T SW Apartment, T SE Apartment, T S1 Apartment, T S2 Apartment |
| OCC_APT_SCH_STAY_HOME_FAMILY | G NW Apartment, G NE Apartment, G N1 Apartment, G N2 Apartment, M NW Apartment, M NE Apartment, M N1 Apartment, M N2 Apartment, T NW Apartment, T NE Apartment, T N1 Apartment, T N2 Apartment |
| OCC_OFF_w_SB_SCH | Office |
| OCC_APT_SCH_CORRIDOR | G Corridor, M Corridor, T Corridor |

* **`Lights`**: name `<zone>_Lights`; method `Watts/Area`; watts per floor area = xlsx raw_data column L. Schedules:

| Schedule | Zones |
|---|---|
| ltg_sch_apartment_hardwired | G SW Apartment, G NW Apartment, G NE Apartment, G N1 Apartment, G N2 Apartment, G S1 Apartment, G S2 Apartment, M SW Apartment, M NW Apartment, M SE Apartment, M NE Apartment, M N1 Apartment, M N2 Apartment, M S1 Apartment, M S2 Apartment, T SW Apartment, T NW Apartment, T SE Apartment, T NE Apartment, T N1 Apartment, T N2 Apartment, T S1 Apartment, T S2 Apartment |
| ltg_sch_office | Office |
| ltg_sch_corridor | G Corridor, M Corridor, T Corridor |

* **`ElectricEquipment`**: name `<zone>_Equipment`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process; the elevators are in the plug load of the ground corridor). Schedules:

| Schedule | Zones |
|---|---|
| EQP_APT_SCH | G SW Apartment, G NW Apartment, G NE Apartment, G N1 Apartment, G N2 Apartment, G S1 Apartment, G S2 Apartment, M SW Apartment, M NW Apartment, M SE Apartment, M NE Apartment, M N1 Apartment, M N2 Apartment, M S1 Apartment, M S2 Apartment, T SW Apartment, T NW Apartment, T SE Apartment, T NE Apartment, T N1 Apartment, T N2 Apartment, T S1 Apartment, T S2 Apartment |
| EQP_OFF_SCH | Office |
| BLDG_ELEVATORS | T Corridor |

* **`ZoneInfiltration:DesignFlowRate`**: `<zone>_Infiltration` for every zone: method `Flow/ExteriorWallArea`, flow per exterior surface area = raw_data column R; `<zone>_Door_Infiltration` (the ground corridor): method `Flow/Zone`, no schedule, design flow rate = column T. Method and schedule:

| Method | Schedule | Zones |
|---|---|---|
| Flow/ExteriorWallArea | INF_APT_SCH | 27 zones |
| Flow/Zone | (none: always on) | G Corridor |

* **`HVACTemplate:Thermostat`** (xlsx Schedule Summary, Heating / Cooling Set Point; each zone uses the schedules of its set point control in the prototype, checked against the xlsx hourly values):

| Object | Heating schedule | Cooling schedule | Zones |
|---|---|---|---|
| ApartmentThermostat1 | HTGSETP_APT_SCH | CLGSETP_APT_SCH | 24 zones |

* **`HVACTemplate:Zone:WaterToAirHeatPump`**: one per conditioned zone (xlsx type 15 WSHP): zone name; thermostat as above; availability schedule = the xlsx HVAC schedule; outdoor air method `Flow/Zone` with the outdoor air per zone of xlsx raw_data column P (m3/s). The corridors have no HVAC (type NA). The plant loops (mixed water loop with a tower and a boiler) are in `Appendix_IDF.txt`.

The wall and roof constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.084 Btu/h-ft2-F (Table 20, steel-frame wall) and roof U = 0.063 (Table 19, insulation entirely above deck), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25).
