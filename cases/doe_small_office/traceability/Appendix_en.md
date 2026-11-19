# Appendix (natural language): DOE Small Office, Short IDF, Buffalo

Target IDF: `DOE/Small_Office/Short/DOE_OfficeSmall_2004_Buffalo.idf`. Companion file: `Appendix_IDF.txt` (the IDF text that the documents do not give, with the values of the documents replaced by markers). The IDF holds only the data of the documents (`inputs/PNNL_Prototype_Scorecards.xlsx`, `inputs/*.pdf`) and what EnergyPlus needs to run. Section 1 describes the geometry, which the documents give only as areas; section 2 says how the objects that `Appendix_IDF.txt` leaves out are written from the documents.

## 1. Geometry in words

A one-storey office building, **27.69 m x 18.46 m** (90.85 ft x 60.56 ft) in plan, 511 m2 of conditioned floor, with a pitched-roof attic above it. Local coordinates start at the south-west corner of the building: x to the east, y to the north, z up; all zone origins are 0, so the vertices are building coordinates (`GlobalGeometryRules`: upper-left corner, counterclockwise, relative).

* **Five conditioned zones**, 3.05 m (10 ft) high: a core zone `Core_ZN`, 17.69 m x 8.46 m, and four perimeter zones, strips 5.00 m (16.4 ft) deep around it. `Perimeter_ZN_1` is the south strip and `Perimeter_ZN_3` the north strip (the full width of the building); `Perimeter_ZN_2` is the east strip and `Perimeter_ZN_4` the west strip. The strips meet at the corners along 45 degree lines, so the plan sizes in the zone table are bounding rectangles and the floor areas are smaller than the rectangles.
* **The attic** (`Attic`, not conditioned) lies on top of the conditioned zones, from z = 3.05 m to 6.33 m. It has four roof planes with a pitch of about 18.5 degrees and four soffit floors that overhang the walls by 0.60 m (2.0 ft). It is a row of the xlsx (area, infiltration, no HVAC); the roof planes and soffits are not in the documents.
* **Surfaces**: the ceiling of every conditioned zone and the floor of the attic above it are a pair of interior surfaces (boundary condition `Surface`, construction `AtticCeiling`); the walls between the core and the perimeter zones and between neighbouring perimeter zones are interior walls (`GenericSurface`); the four exterior walls (`ExteriorWall`) are the outer walls of the perimeter zones; the roof planes and the soffit floors of the attic (`GenericSurface`) face outdoors. The floors of the four perimeter zones are slab on grade (F-factor method, `Construction:FfactorGroundFloor`); the floor of `Core_ZN` is adiabatic.
* **Windows** (construction `Window`, 20 windows and one glass door, no swinging doors): all windows are 2.79 m2 each, in a row of equal windows in each exterior wall (six in the south and north walls, four in the east and west walls); the glass door in the south wall is 3.91 m2. Together 59.65 m2.

| Zone | Plan x by y m | z range m | Floor area m2 |
|---|---|---|---|
| Core_ZN | 17.69 x 8.46 | 0.00 to 3.05 | 149.7 |
| Perimeter_ZN_1 | 27.69 x 5.00 | 0.00 to 3.05 | 113.5 |
| Perimeter_ZN_2 | 5.00 x 18.46 | 0.00 to 3.05 | 67.3 |
| Perimeter_ZN_3 | 27.69 x 5.00 | 0.00 to 3.05 | 113.4 |
| Perimeter_ZN_4 | 5.00 x 18.46 | 0.00 to 3.05 | 67.3 |
| Attic | 28.89 x 19.66 | 3.05 to 6.33 | attic |

The IDF has 43 building surfaces: 5 ceiling (surface), 1 floor (adiabatic), 4 floor (groundfcfactormethod), 4 floor (outdoors), 5 floor (surface), 4 roof (outdoors), 4 wall (outdoors), 16 wall (surface). The vertex coordinates are in `Appendix_IDF.txt`.

## 2. Objects written from the documents by a rule (not in `Appendix_IDF.txt`)

Each class below has one object per conditioned zone (the 5 zones of the xlsx that have an HVAC system; not the attic, except the infiltration). All fields not named here are empty (EnergyPlus default).

* **`People`**: name `<zone>_People`; schedule `BLDG_OCC_SCH_wo_SB`; method `Area/Person`; floor area per person = xlsx raw_data column M (18.58 m2/person); activity level schedule `ACTIVITY_SCH`.
* **`Lights`**: name `<zone>_Lights`; schedule `ltg_sch_office`; method `Watts/Area`; watts per floor area = xlsx raw_data column L (10.6713 W/m2).
* **`ElectricEquipment`**: name `<zone>_Equipment`; schedule `BLDG_EQUIP_SCH`; method `Watts/Area`; watts per floor area = xlsx raw_data column N (plug and process, 6.78 W/m2).
* **`ZoneInfiltration:DesignFlowRate`**: name `<zone>_Infiltration` for every perimeter zone (raw_data column R, 0.00103 m3/s-m2); schedule `INFIL_QUARTER_ON_SCH`; method `Flow/ExteriorWallArea`. For `Perimeter_ZN_1` also `<zone>_Door_Infiltration`: method `Flow/Zone`, no schedule, design flow rate = raw_data column T (0.12979 m3/s). For `Attic` `Attic_Zone_Infiltration`: method `Flow/Zone`, no schedule, design flow rate = raw_data column S (0.2001 m3/s).
* **`HVACTemplate:Thermostat`**: one object `OfficeThermostat`; heating schedule `HTGSETP_SCH_NO_OPTIMUM`, cooling schedule `CLGSETP_SCH_NO_SETBACK` (xlsx Schedule Summary).
* **`HVACTemplate:System:UnitaryHeatPump:AirToAir`**: five objects, one per conditioned zone, named by xlsx raw_data column I (`PSZ-AC:1` for `Core_ZN`, `PSZ-AC:2` ... `PSZ-AC:5` for `Perimeter_ZN_1` ... `Perimeter_ZN_4`); availability schedule `HVACOperationSchd`; control zone = the zone; supplemental heating coil type `Gas` (xlsx HVAC system type 4.2, PSZ-HP with gas auxiliary heat).
* **`HVACTemplate:Zone:Unitary`**: zone name; template system = the unit of the zone; thermostat `OfficeThermostat`; outdoor air method `Flow/Area` with the outdoor air per zone floor area of the xlsx sheet Zone and HVAC System Summary (0.000508 m3/s-m2).

The wall and ceiling constructions come from the NREL PDF (Chicago 5A, new construction): wall U = 0.151 Btu/h-ft2-F (Table 21, mass wall, the wall type that the PDF assigns to the Small Office; the xlsx says wood frame and gives no U-value) and ceiling below the attic U = 0.034 (Table 19, roof, attic and other), each written as one layer whose resistance is 1/U minus the surface films; window U = 0.57 Btu/h-ft2-F and SHGC = 0.39 (Tables 24 and 25).
