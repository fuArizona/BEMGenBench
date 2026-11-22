# Keys that an equivalent construction gives back

Written by `rules_markdown()` of `evaluator/engine/idf_equiv.py`; `evaluator/tests/test_equivalences.py` checks that this file is the same as its output. Do not edit it by hand: edit `RULES` in the code.

A construction of the reference and its partner in the candidate (the construction named by the paired surfaces) are **equivalent** when the thermal resistance of their layers is the same within 1 % **and** the heat capacity per m2 within 10 % **and** the order of the layers is the same (the centroid of the heat capacity along the resistance within 0.10; an opaque construction; the surface films are the same on both sides and are not added) or the U-factor and the SHGC that EnergyPlus reports are the same within 1 % (a window construction). The heat capacity per m2 is density x specific heat x thickness, summed over the layers; both without mass is the same. A pair with the same resistance but another heat capacity or order is NOT equivalent and gives nothing back, EXCEPT for a construction that the documents give only as a U-value (listed in `traceability/u_only_constructions.json`): there the resistance alone decides, and the density and the specific heat are not given back (the mass is not known to be the same). A verdict of a judge (idf_judge.py) can make a pair equivalent that the numbers cannot decide; then the mass is not known and the density and the specific heat are not given back.

A key of the score that is lost only because the two files write the layers differently is given back when its field is in the table below and its condition holds. The keys of an object that the other file does not have at all (a material that one file writes as layers and the other as one resistance) are given back only for the fields that the table allows. For a material that several constructions use, the condition must hold for every one of them. The key score is not changed; the number with the keys given back is `rate_with_equivalents`.

| class | field | condition | why |
|---|---|---|---|
| Construction | the layer names (outside_layer, layer_2 ...) | equivalent | the layer names are the way the stack is written; the stack of the other file has the same thermal resistance. The order of the layers is checked by the position of the heat capacity along the resistance (ORDER_TOL). |
| Material | thickness | equivalent | with the conductivity, one of the two ways to write the resistance (thickness / conductivity). The resistance is that of the whole construction, not of this layer. |
| Material | conductivity | equivalent | see thickness. |
| Material | density | equivalent and mass | the resistance does not determine it; it is given back only when the heat capacity per m2 of the construction is the same too. |
| Material | specific heat | equivalent and mass | see density. |
| Material | roughness, absorptances | never | they are not part of the thermal resistance or the heat capacity; a file that does not write them has not given the documented value. |
| Material:NoMass | thermal resistance | equivalent | the quantity itself (the whole construction has the same resistance). |
| Material:NoMass | roughness, absorptances | never | see Material. |
| Material:AirGap | thermal resistance | equivalent | the quantity itself. |
| Material:InfraredTransparent | all fields | never | it has no resistance. |
| WindowMaterial:* (glazing, gas, simple glazing system, ...) | all fields | equivalent | the U-factor and the SHGC that EnergyPlus reports for the construction are the same; the glazing data are only the way they are written. The visible transmittance is not compared. |
| WindowProperty:FrameAndDivider, shading and shading control | all fields | never | frames, dividers and shading are not part of the U-factor and SHGC computed here. |

Not checked: frames and dividers, shading, the visible transmittance.
