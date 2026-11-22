# Calibration of a judge of construction pairs

The evaluator never calls a language model. A judge (a person, or a language model run outside the evaluator, for example by a skill of the Agent Harness in a fresh sub-agent) answers the construction pairs that `idf_equiv.py` cannot decide, through two files (format: `evaluator/engine/idf_judge.py`):

- the evaluator writes `<case>.judgement_requests.json` (tasks `cannot_compute`, `no_counterpart`, `classify_near`);
- the judge writes a verdict file; `evaluate.py --judgements <file or folder of <case>.judgements.json>` reads it and gives `equivalences.llm` (`rate_with_llm`, the accepted and rejected verdicts). A verdict never overrules a computed number (more than 5 % apart: refused), and it is not part of the key score.

The judge is the skill `bemgenbench_judge` of the Agent Harness (`tools/claude_skills/bemgenbench_judge/` in this repository, `~/.claude/skills/bemgenbench_judge/` installed; `/bemgenbench_judge`): it splits the requests into batches, gives each batch to a fresh sub-agent with the prompt `judge_prompt.md` (the criterion of `docs/equivalence_rules.md`), merges the answers (`scripts/merge_verdicts.py`, which records the model, the skill version, the isolation and the date) and, for a calibration set, scores them with `score_judgements.py`.

Before a judge is trusted, it is calibrated here.

## The set (`set_v1/`, made by `build_set.py`, seed 1)

187 pairs made from the constructions and window systems of the reference IDFs by a known change: renamed layers, a layer split in two, a material rescaled (k, t, density) with the same resistance and mass, a one-layer `NoMass` construction, the layers in the other order, a density 60 % higher, a layer deleted, the resistance 0.5 / 2 / 5 / 10 / 30 % off, and for windows the U-factor 0.2 / 2 / 10 % and the SHGC 5 / 15 % off. `requests.json` is what the judge sees (no label); `truth.json` has the label, the family, the difficulty and the split (by the base construction: dev to write the prompt, test frozen and used once).

Labels: `equivalent` (resistance within 1 %, heat capacity within 10 % and the same order of the layers: the centroid of the heat capacity along the resistance within 0.10), `u_equivalent_only` (the same resistance, another heat capacity or order: NOT equivalent, user decision 2026-11-21; the name is kept), `not_equivalent` (more than 3 % apart), `boundary` (1 to 3 %, left out of the accuracy). The strict view of `score_judgements.py` is the criterion; the lenient view counts `u_equivalent_only` as equivalent.

```bash
python evaluator/calibration/build_set.py                                   # rebuild (the same seed gives the same set)
python evaluator/calibration/score_judgements.py evaluator/calibration/set_v1 verdicts.json --split dev
python evaluator/calibration/score_judgements.py evaluator/calibration/set_v1 --baseline   # the rule of idf_equiv.py on the numbers of the requests
```

## What the set shows, and what it does not

- The rule of the evaluator alone is right on all 172 pairs outside the boundary (strict view), because the labels follow from the same numbers (resistance, heat capacity, centroid). So this set is easy for the code: a judge can only be shown to be as good as the rule, not better. The cases where a judge could be better are those the numbers cannot decide, and they are not here.
- The labels follow the rules of `idf_equiv.py`: the set shows whether a judge applies the same rules, not whether the rules are right. A part of it (about 10 to 20 %) should be checked by a person, and for the order of the layers, EnergyPlus could arbiter.
- The cases a judge is for (a layer without a value, a construction without a partner, an unusual material) are NOT in the set: they need a person to label. On the 22 candidates of the gbxml2idf pipeline the evaluator asks for 7 pairs only (4 `classify_near`, 3 `no_counterpart`, no `cannot_compute`), so the real cases are few; they are in `<case>.judgement_requests.json` of a run.
- Not included: air (outdoor air, ventilation), frames and shading, and the natural differences between the code editions of the DOE prototype IDFs (a possible source of not_equivalent pairs).

## Runs

- `runs/2026-11-21_dev/`: the judge on the dev split, with and without the computed numbers (README there). Test split: see below.
- `runs/2026-11-21_test40/`: the judge on 40 pairs of the test split (reduced, text only; README there). The other 72 pairs of the test split are not used.
- `set_hard_v1/` (made by `build_hard.py`): 60 hard pairs without computed numbers (missing values, unusual materials, misleading names); `runs/2026-11-21_hard_dev_run1/` and `runs/2026-11-21_hard_dev_run2/`: the judge on its dev split with prompt v1 and v2. Its test split (34 pairs): `runs/2026-11-21_hard_test/` (used once, prompt v2 frozen).
- `runs/2026-11-21_real_candidates/`: the judge on the 14 requests of the real gbxml2idf candidates (requests, per-case judgement files, README).
- `class_controls_v1/` (made by `build_class_controls.py`, scored by `score_class.py`) and `runs/2026-11-21_class_keys_pilot/`: the pilot of the class keys ("ambiguous info"): 16 hand-made controls and the 4 real requests.
- `runs/2026-11-21_class_keys_final/`: the class keys judged through `/bemgenbench_judge` with the controls mixed in, rule "uncertain left out of the keys".
