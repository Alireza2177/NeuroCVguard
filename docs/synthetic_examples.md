# Offline synthetic scenarios and tutorials

These are fictitious tabular mechanisms inspired by workflow structure, not
biologically realistic brain models, patient observations or clinical results.
Generation, audits, fitting and HTML reports run locally without a download or
account. Ordinary report projection stays enabled unless sensitive detail is
explicitly requested. Synthetic labels do not authenticate arbitrary imported files.

## First run

After local installation, run from any working directory:

```text
python -m neurocvguard demo --out local_outputs/demo
```

Open `report.html` in the output directory. The default `clean` scenario generates
two observations per participant and uses participant-disjoint CV. Repeated visits
alone are not leakage. The report retains unknown upstream preprocessing; the
generator's existence does not change the evaluator's general provenance boundary.

```text
python -m neurocvguard demo --scenario repeated --out local_outputs/repeated
python -m neurocvguard demo --scenario site_shift --out local_outputs/site-shift
```

`repeated` explicitly compares ordinary participant-disjoint CV with a row-random
StratifiedKFold diagnostic. Its warning says not to report it as evidence for
unseen-participant generalization. Pooling diagnostic predictions per participant
does not remove the training leakage. `site_shift` compares participant and site
holdouts: shared input identities do not make the estimates causally comparable.
Neither scenario guarantees a higher or lower score. No seeds are searched.

## Parameters and mechanisms

```python
from neurocvguard.synthetic import generate_synthetic, scenario_parameters
from neurocvguard.demo import run_demo

parameters = scenario_parameters("clean", n_participants=60, signal_strength=0.5)
data = generate_synthetic(parameters)
config = data.config()  # Explicit role and selected-feature names.
run_demo(output_dir="local_outputs/custom", parameters=parameters)
```

`SyntheticParameters` accepts these explicit fields. A passed parameter object
replaces the entire scenario preset; the effective values are always recorded.

| Parameter | Clean default | Supported bounds |
|---|---:|---|
| seed | 2026 | integer 0 through 2**32-1 |
| n_participants | 60 | integer 2 through 100,000 |
| observations_per_participant | 2 | integer 1 through 100 |
| n_classes | 2 | integer 2 through 100, no more than participants |
| n_sites | 3 | integer 1 through 100, no more than participants |
| n_features | 8 | integer 1 through 1,000 |
| signal_strength | 1.0 | finite number 0 through 100 |
| participant_effect | 0.5 | finite number 0 through 100 |
| site_effect | 0.0 | finite number 0 through 100 |
| site_target_association | 0.0 | finite number 0 through 1 |

The allocation guard permits at most 2,000,000 observation-feature values; this
is an implementation bound, not a scientific threshold. A structurally valid
generator configuration can still produce an infeasible split. The planner refuses
that design without reducing folds, removing rows, relabeling or trying another seed.
Not every declared site must appear in a finite random realization.

Six independent local NumPy Generator streams draw label order, site assignment,
class vectors, participant vectors, site vectors and observation noise. Labels
are shuffled balanced class indices and are constant for each participant.
Each feature vector is unit-normal observation noise plus:

```text
signal_strength * class_vector[target]
+ participant_effect * participant_vector[person]
+ site_effect * site_vector[site]
```

Each latent vector has independent standard normal components. Strength changes
reuse the same draws and preserve all identities, labels and site assignments.
The participant vector is constant across visits, introducing within-person feature
similarity. Session labels are intentionally reused across people.

Site assignment mixes uniform random allocation with class-associated allocation.
For the associated allocation, site is `class_index % n_sites` with probability
0.75 or the next site modulo n_sites with probability 0.25. A per-person uniform
draw selects this allocation when below `site_target_association`; otherwise the
independent allocation is used. Changing this parameter never relabels a person.
With `site_effect=0`, changing allocation changes metadata but leaves features exact.

The `repeated` preset changes **only** participant_effect to 3.0. `site_shift`
changes **only** site_effect to 2.0 and site_target_association to 0.8. All other
defaults, including seed, visits, classes and noise, remain the clean defaults.
Exact reproducibility is checked in the recorded supported environments; do not
assume byte-identical RNG or numerical library behavior across arbitrary versions.

## Five executable tutorials

Run each script after installing NeuroCVguard. No repository fixtures, notebook
state or user dataset is read. The scripts call the packaged workflow implementation
in `neurocvguard.demo`; inspect that module for the complete shared code.

```text
python examples/01_cohort_audit.py --out local_outputs/example-01
python examples/02_repeated_observations.py --out local_outputs/example-02
python examples/03_site_held_out.py --out local_outputs/example-03
python examples/04_preprocessing_provenance.py --out local_outputs/example-04
python examples/05_explicit_feature_join.py --out local_outputs/example-05
```

1. Generate local TSVs, map columns, audit and evaluate participant-disjoint folds.
2. Compare the explicitly invalid observation-random diagnostic and participant CV.
3. Hold sites out. This tutorial explicitly sets association to 1.0, retaining the
   default seed and other site_shift parameters. Single-class test folds preserve
   meaningful accuracy and null class-complete metrics with `missing_true_class`;
   every actual training fold still has both classes.
4. Compare a fictitious global-PCA declaration with unknown provenance. No PCA is
   actually fitted. The declaration remains declared evidence, not authenticated
   history; feature values cannot certify either history.
5. Write an extracted-feature table with reversed rows, custom `scan_key` and
   `person_key` columns, and explicit feature names. Join by key through load_cohort.

Scripts are also bundled as resources under `neurocvguard/examples` in the wheel,
and included in the source distribution. The default CLI loads packaged generator
code, never repository fixtures. Script and demo installed journeys execute outside
the repository. No notebook is required.

## Outputs, actual results and privacy

`report.json`, `report.html` and `report.manifest.json` form the main report.
Prefixed audit/design reports provide supporting views. Each report visibly says
fully synthetic; public projection preserves only that exact fixed notice, not
arbitrary input free text. Sensitive detail remains an explicit independent option.

The flat output bundle also includes generated cohort/features TSVs, config files,
private evaluation records and identity-bearing plans. `demo.private.json` retains
the exact effective parameters, seed, dependency versions, input digests, process
argv (or a null argv for Python API calls), status and SHA-256 checksums of other
artifacts. Full original process paths belong only in this private manifest. All
data and keys created here are visibly fictitious; do not infer synthetic status
from arbitrary filenames in another workflow.

The whole named bundle is staged before publication and rolls back ordinary write
failures through the existing writer. Existing files require a new destination or
explicit `--overwrite`; unrelated names are preserved. Switching scenarios with
overwrite can leave older unrelated scenario files, so prefer a fresh directory
for each scenario and use the current manifest's artifact inventory.

[Executed runs](../qa/evidence/S13/executed/runs.json) retain actual results from all
five examples and three scenarios. These values are outputs, not independently
generated test oracles or claims about real neuroimaging data. The retained private
manifest argv has machine-specific path prefixes redacted; scientific artifacts
and their recorded checksums are unchanged. Screenshot capture was blocked by
the browser's local-URL policy; the reports have numerical and HTML/JSON
consistency checks, but the planned visual review remains incomplete. See
{download}`the capture record <../qa/evidence/S13/screenshot-blocked.md>` and
{download}`the documented exception <../state/decisions/ADR-S13-001-screenshot-exception.md>`.
