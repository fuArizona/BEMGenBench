# Sources and licenses

| Part | Author | License |
|---|---|---|
| Code (`evaluator/`) | BEMGenBench contributors | MIT, `LICENSE` |
| The six Residence cases (`cases/res_*`: input files, reference IDFs, traceability files) | BEMGenBench contributors | MIT, `LICENSE` |
| The DOE cases and their documents, the weather files | other sources, see below | their own terms |

The DOE data and the weather files below come from other sources and keep their own terms. This section says what each file is, where it comes from, and what is still to be confirmed before the repository is made public. **Items marked "to confirm" must be checked by the maintainers before the first public release.**

## DOE cases (16)

| Files | Source | Terms |
|---|---|---|
| `data/DOE/inputs/PNNL_Prototype_Scorecards.xlsx` | Pacific Northwest National Laboratory (PNNL), prototype building scorecards of the DOE commercial prototype building models (distributed with the prototype models at energycodes.gov) | US Department of Energy / PNNL publication. To confirm: the exact download page, date and license statement. |
| `data/DOE/inputs/U.S. Department of Energy Commercial Reference Building Models of ... .pdf` | NREL report "U.S. Department of Energy Commercial Reference Building Models of the National Building Stock" (Deru et al., NREL/TP-550-46861, 2011) | US Government work (NREL / DOE). To confirm: statement of the NREL publication page. |
| `cases/doe_*/reference/reference.idf` | Reduced from the DOE/PNNL ASHRAE 90.1-2004 prototype IDF of each building type (Buffalo, NY): only the data of the two documents above and what EnergyPlus needs to run. Edited and annotated by the benchmark authors. | Derived from the DOE/PNNL prototype models. To confirm: license of the prototype models (EnergyPlus example and prototype files). |
| `data/DOE/inputs/run_conditions.txt` | Written by the benchmark authors (the weather file and the run year of the 16 DOE cases) | same as this repository (MIT) |
| `cases/doe_*/traceability/doc_to_idf_map.xlsx`, `not_in_documents.md` | Written by the benchmark authors | same as this repository |
| `cases/doe_*/traceability/full/` (nine DOE cases: `reference_full.idf`, appendices, map workbook, `Result_changes_vs_original.md`) | The DOE/PNNL Prototype Building Models (ASHRAE 90.1-2004, Buffalo, NY), converted to EnergyPlus 23.1, annotated and edited by the benchmark authors. A reference only; the benchmark is scored against the reduced `reference/reference.idf`. | Derived from the DOE/PNNL prototype models. To confirm: license of the prototype models (same as `reference.idf`). |

## Residence cases (6)

Author of all files of the six Residence cases: **BEMGenBench contributors**. License: **MIT** (`LICENSE`; `author` and `license` in each `case.yaml`). This is the declaration of the maintainers of the benchmark.

| Case | Files |
|---|---|
| `res_lupton_house` | `input/input1.txt`, `reference/reference.idf`, `traceability/` |
| `res_simply_family_house` | `input/info.txt`, the floor-plan images and `HVAC.png` of `input/`, `reference/reference.idf`, `traceability/` |
| `res_iunit` | `input/iunit_epc_inputs.xlsx`, `reference/reference.idf`, `traceability/` |
| `res_l100ac`, `res_l100al` | `input/L100A.pdf`, `L100A_Text*.txt`, `L100A_Figures.txt`, `reference/reference.idf`, `traceability/` |
| `res_nzertf` | `input/nzertf-inputs.xlsx`, `reference/reference.idf`, `traceability/` |

Anyone who adds a file to these cases must be able to license it under the MIT License.

## Weather files

The repository does not contain weather files. `data/weather/weather_files.csv` lists the download link, the checksum and the cases of each file, and `data/weather/download_weather.py` downloads them. All seven files are downloaded from climate.onebuilding.org (TMY3 files of US stations and TMYx 2011-2025 files); the TMY3 data originate from the US National Solar Radiation Database / NREL and are distributed for EnergyPlus.

## EnergyPlus

EnergyPlus is not included. The evaluator needs an installation of EnergyPlus 23.1 (its schema; the transition programs if a candidate has another version, and ExpandObjects for HVACTemplate objects; and the `energyplus` program, which by default runs a candidate once with the weather file of its case; with `--no-run` the evaluator does not run a candidate). EnergyPlus is a product of the US Department of Energy and licensed under its own terms.
