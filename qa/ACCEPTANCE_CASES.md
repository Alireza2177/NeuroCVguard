# Acceptance-case register

These are **required future tests/review checks**, not claims of completed or passing NeuroCVguard tests. Each case must map to a real test node or explicit human-review evidence during implementation.

## S00 — Repository bootstrap and environment evidence

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S00-01 — Import has no side effects | Import in an empty temporary working directory with network calls blocked. | No new files, worker processes, network calls or dataset access. | integration |
| AT-S00-02 — Editable installation | Install the declared package in a clean virtual environment. | Import and the version entry point work using declared dependencies. | packaging |
| AT-S00-03 — Preserve unrelated work | Begin with an unrelated uncommitted file. | Bootstrap does not overwrite, remove or stage that file automatically. | review |
| AT-S00-04 — Truthful metadata | Inspect README/metadata before any public publication. | No false PyPI link, DOI, supported-platform claim or passing-CI badge. | review |
| AT-S00-05 — Instruction loading | Start a Codex task at the intended root. | It identifies AGENTS, current stage and relevant specifications actually read. | review |

## S01 — Typed models, configuration and serialization contracts

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S01-01 — Unknown config key | Add evaluation.secret_magic=true. | ConfigurationError names the unsupported key. | unit |
| AT-S01-02 — Duplicate JSON keys | Provide a JSON object with the same key twice. | Loader rejects it before last-value-wins parsing. | unit |
| AT-S01-03 — Boolean integer ambiguity | Set split.n_splits=true. | Validation fails rather than interpreting true as 1. | unit |
| AT-S01-04 — Optional defaults | Omit positive_class and max_input_mb from otherwise valid config. | Defaults are null and 128 respectively; no hidden role inference. | unit |
| AT-S01-05 — Unknown schema version | Set schema_version to an unsupported major value. | Clear incompatible-version error; no best-effort reinterpretation. | unit |
| AT-S01-06 — JSON null semantics | Serialize an undefined AUC with a reason. | value=null and a non-empty reason; never NaN. | unit |
| AT-S01-07 — No Infinity output | Attempt to serialize a non-finite numeric result. | Reject or explicitly map to a reasoned null at the metric boundary. | unit |
| AT-S01-08 — Offline schema validation | Block all sockets while validating each local schema. | No HTTP/schema download; supported examples validate. | integration |
| AT-S01-09 — Record round trip | Serialize and read a non-sensitive fixture record. | All schema-defined meanings, enums and ordering are preserved. | unit |
| AT-S01-10 — Config immutability | Pass a config into each public helper and compare afterward. | No silent mutation of user settings. | property |
| AT-S01-11 — Private/public separation | Serialize the same evaluation through both serializers. | Public projection omits private IDs/digests; operational format is visibly sensitive. | unit |

## S02 — Strict tables, identities and keyed feature joins

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S02-01 — Leading zeros | Read IDs 001 and 1 from TSV. | Two distinct participants/observation keys are preserved. | unit |
| AT-S02-02 — Duplicate headers | Read a CSV with subject_id header twice. | InputValidationError before dataframe auto-renaming. | unit |
| AT-S02-03 — UTF-8 BOM | Read a BOM-prefixed header and Unicode IDs. | Correct header recognition and exact legitimate IDs. | unit |
| AT-S02-04 — Whitespace identity | Read a subject ID with a trailing space. | Reject with sanitized repair message; do not trim silently. | unit |
| AT-S02-05 — Missing critical ID | Read an empty participant or observation key. | Fatal validation error; no assigned synthetic identity. | unit |
| AT-S02-06 — NA vocabulary | Read literal NA as an ID and n/a as an optional missing value. | NA stays a string; n/a is recognized missing. | unit |
| AT-S02-07 — Duplicate observation ID | Two rows use the same observation key. | Input rejected; no drop_duplicates fallback. | unit |
| AT-S02-08 — Shuffled feature rows | Reverse feature table order relative to cohort. | Features align exactly by observation ID. | unit |
| AT-S02-09 — Missing feature key | Remove one cohort key from feature table. | Join fails with missing count, not silent row intersection. | unit |
| AT-S02-10 — Extra feature key | Add an observation not in cohort. | Join fails explicitly. | unit |
| AT-S02-11 — Prohibited predictors | Select diagnosis or subject_id as a feature. | Configuration/input validation refuses it. | unit |
| AT-S02-12 — Numeric coercion | Selected feature contains text or infinity. | Input fails; recognized missing numeric cells remain missing. | unit |
| AT-S02-13 — DataFrame identity type | Pass integer participant IDs through Python API. | Refuse lossy implicit conversion and explain string requirement. | unit |
| AT-S02-14 — No input mutation | Pass DataFrames and compare values/index/dtypes after loading. | Original metadata/features remain unchanged. | property |
| AT-S02-15 — Unsupported sources | Pass a URL, XLSX, pickle or joblib path. | Reject unsupported local format without network/deserialization. | security |
| AT-S02-16 — Allocation guard | Describe rows/features exceeding configured limits. | Refuse before constructing avoidable dense arrays. | unit |
| AT-S02-17 — Digest invariance | Reorder rows, then separately edit a mapped metadata value. | Reorder retains digest; mapped change changes digest. | property |
| AT-S02-18 — Paths with spaces | Load files under a Unicode directory with spaces on supported systems. | No shell quoting or hard-coded slash assumption. | integration |

## S03 — Participant, dependency and cohort checks

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S03-01 — People versus observations | Use 18 people with two observations each. | Inventory gives 18 people and 36 observations. | unit |
| AT-S03-02 — Repeated participants are not leakage | Audit that cohort without any supplied splits. | Informational repeat notice; no observed split violation. | unit |
| AT-S03-03 — Global session labels | Every participant uses ses-01 and ses-02. | Distinct people are not linked by session text. | unit |
| AT-S03-04 — Changing diagnosis | One participant has different target labels over visits. | Describe target variation; block constant-target baseline eligibility without relabeling. | unit |
| AT-S03-05 — Transitive dependency | A links to B through family; B links to C through duplicate cluster. | A/B/C form one protected component. | unit |
| AT-S03-06 — Dependency namespaces | Family code X for one group and duplicate code X for unrelated people. | No cross-field equality link unless an actual participant bridges them. | unit |
| AT-S03-07 — Missing protected field | A declared family column contains missing values. | Strict planning/evaluation blocked; missing values not grouped together. | unit |
| AT-S03-08 — Cross-site participant | One participant has two site values. | One identity retained; descriptive crossing notice. | unit |
| AT-S03-09 — Exact feature equality | Different IDs share the same numeric feature vector. | Heuristic review finding; no identity merge/drop. | unit |
| AT-S03-10 — All-missing vectors | Several rows have all selected features missing. | Skip duplicate-equality inference for those vectors and record reason. | unit |
| AT-S03-11 — Component ordering | Permute rows of a transitive dependency fixture. | Same memberships and deterministic component identifiers. | property |
| AT-S03-12 — Hash collision confirmation | Mock equal hashes for unequal feature vectors. | Exact comparison prevents a false equality finding. | unit |

## S04 — Split import and independent invariant auditing

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S04-01 — Known participant overlap | Use bundled leaky plan with different visits on each side. | Participant overlap detected even with no observation overlap. | unit |
| AT-S04-02 — Clean repeated cohort | Use bundled clean plan. | No subject/component overlap violations. | unit |
| AT-S04-03 — Observation overlap | Insert the same observation into train and test. | Always rejected including diagnostic mode. | unit |
| AT-S04-04 — Across-fold train reuse | Use ordinary valid 3-fold CV. | Repeated training membership across folds is not leakage. | unit |
| AT-S04-05 — Allowed same sites | Subject-disjoint plan shares sites under unseen_participant. | No site-separation violation. | unit |
| AT-S04-06 — Forbidden same sites | Same plan declares unseen_site. | Domain overlap error for the requested objective. | unit |
| AT-S04-07 — Unknown member | Plan refers to obs-does-not-exist. | Reject membership/identity mismatch; no positional lookup. | unit |
| AT-S04-08 — Missing partition row | Omit a cohort observation from both train and test in one fold. | Per-fold coverage violation. | unit |
| AT-S04-09 — Duplicate membership | Duplicate one role/observation membership. | Reject rather than collapse to a set silently. | unit |
| AT-S04-10 — Missing training class | Outer train has only CN while target space includes AD. | Evaluation blocked for that fold. | unit |
| AT-S04-11 — Missing test class | Outer test has only CN but train has all classes. | Class-coverage warning; not an invented full-class score. | unit |
| AT-S04-12 — Inner containment | Put an outer-test ID into an inner training subset. | Nested containment violation. | unit |
| AT-S04-13 — Inner protected overlap | Separate related participants across inner train/validation. | Protected-component violation. | unit |
| AT-S04-14 — Holdout audit | A single valid train/test fold covers the cohort. | Audit supported; complete_cv=false and evaluator not permitted. | unit |
| AT-S04-15 — Repeated imported plans | Two repeat identifiers each contain valid folds. | Audit each repeat independently; baseline scope limit retained. | unit |
| AT-S04-16 — Digest mismatch | Change target metadata after binding a plan. | Reject the plan/cohort binding. | unit |
| AT-S04-17 — TSV import contract | Supply outer-only TSV and then an unsupported validation role. | Correct valid import; explicit invalid-role error. | unit |

## S05 — Group-aware and held-out-domain plan generation

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S05-01 — Participant stratification unit | Vary visit counts dramatically while participant labels stay fixed. | Stratification uses one record per participant, not visit multiplicity. | unit |
| AT-S05-02 — Protected-group disjointness | Generate arbitrary valid families and labels. | Every protected component remains on one side of each fold. | property |
| AT-S05-03 — Too few groups | Request five folds with three components. | Explicit infeasibility; no fallback to random folds. | unit |
| AT-S05-04 — Approximate stratification | Use indivisible unequal family groups. | Record actual support; do not promise exact balance. | unit |
| AT-S05-05 — Crossing domain group | A person/family spans sites for strict leave-one-site-out. | Generation rejected; cohort remains unchanged. | unit |
| AT-S05-06 — Held-out phase | Use stable participants in at least two phases. | Each phase held out once with identity separation. | unit |
| AT-S05-07 — No hidden repair | Request an infeasible split and inspect inputs/config/seed. | No row removal, merged label, changed seed or changed n_splits. | unit |
| AT-S05-08 — Independent post-audit | Inject a malformed generator result via monkeypatch. | make_splits refuses it after independent audit. | unit |
| AT-S05-09 — Seed and order stability | Same seed/versions after row permutation. | Same expanded observation assignments. | property |
| AT-S05-10 — Global RNG preservation | Record NumPy global RNG state before generation. | State unchanged afterward. | property |

## S06 — Descriptive acquisition–target association checks

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S06-01 — Zero association | Use 2x2 counts [[5,5],[5,5]]. | Cramers V equals zero within tight float tolerance. | unit |
| AT-S06-02 — Perfect association | Use counts [[10,0],[0,10]]. | Cramers V equals one within tolerance. | unit |
| AT-S06-03 — Constant variable | All participants share one site. | Null statistic with constant_variable reason. | unit |
| AT-S06-04 — Repeat invariance | Repeat each participant row ten times. | Participant table and V unchanged. | property |
| AT-S06-05 — Within-person covariate changes | One participant has different sites at visits. | Requested participant-level site pair is unassessable; no cherry-picked visit. | unit |
| AT-S06-06 — Missing pairs | One covariate value is missing. | Complete and excluded participant counts documented; cohort unchanged. | unit |
| AT-S06-07 — Sparse cells | Use table with observed/expected counts below configured threshold. | Sparse warning without p-value or significance stars. | unit |
| AT-S06-08 — High cardinality | Covariate has more than 100 levels. | Skip with too_many_categories rather than merge levels. | unit |
| AT-S06-09 — Noncausal warning | V exceeds review threshold. | Message requests review, not proof of model bias/leakage. | review |
| AT-S06-10 — Category-name invariance | Rename all site/class levels consistently. | V unchanged. | property |

## S07 — Declared preprocessing and runtime evidence model

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S07-01 — No ledger | Audit features without preprocessing history. | Upstream history remains unassessable. | unit |
| AT-S07-02 — Declared global fit | Ledger states PCA learned on all_cohort. | Qualified declared global-fit warning. | unit |
| AT-S07-03 — Declared outside-training IDs | Fit IDs include a held-out observation. | Declared boundary violation, not observed historical proof. | unit |
| AT-S07-04 — Forged runtime label | Imported JSON claims source=runtime_verified. | Schema/loader rejects unsupported source. | security |
| AT-S07-05 — Fixed conversion | Declared data_dependent=false unit conversion. | No blanket fitted-preprocessing leakage assertion. | unit |
| AT-S07-06 — External learned transform | Ledger says externally trained transform without overlap evidence. | External provenance remains unassessable. | unit |
| AT-S07-07 — No ghost fit events | Construct a planned operation without executing fit. | No observed completed fit event is recorded. | unit |

## S08 — Shared JSON/HTML reporting and privacy boundaries

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S08-01 — Default ID redaction | Use obvious sensitive markers as person/observation IDs. | Markers absent from HTML and public JSON. | security |
| AT-S08-02 — Path redaction | Inputs reside in a user/private directory. | Full path/username absent from default reports. | security |
| AT-S08-03 — Domain aliasing | Site labels contain clinic-identifying text. | Default report uses local aliases without reverse map. | security |
| AT-S08-04 — Small-cell suppression | A table has a positive cell below threshold. | Suppressed cell, totals, percentages and derived statistic absent from exported section. | security |
| AT-S08-05 — Hidden payload leakage | Search HTML source and linked/embedded report data. | No suppressed values reappear in hidden markup/JSON. | security |
| AT-S08-06 — HTML injection | A cell contains script tags and an onerror attribute. | Rendered as escaped text; no script execution. | security |
| AT-S08-07 — Formula export | Finding message begins with =, +, -, @ or control prefix. | Optional human spreadsheet export neutralizes formulas. | security |
| AT-S08-08 — No network render | Open report with networking blocked. | Complete layout and content without external assets. | integration |
| AT-S08-09 — Explicit sensitive export | Set sensitive_details=true. | Sensitive banner and clearly different output; never silently enabled. | unit |
| AT-S08-10 — Atomic write failure | Interrupt/fail while writing a new report. | Prior valid report remains intact; no unrelated deletion. | integration |
| AT-S08-11 — Overwrite refusal | Output artifacts already exist and no overwrite flag. | Clear refusal instead of clobbering. | integration |
| AT-S08-12 — Coverage visibility | Clean splits but absent provenance/site metadata. | Missing checks remain visibly incomplete, not all-green safe. | review |
| AT-S08-13 — Rendering does not recompute | Mock expensive statistical helpers to raise during rendering. | Rendering succeeds from precomputed record alone. | unit |

## S09 — CLI and usable audit milestone

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S09-01 — CLI/module parity | Invoke console and python -m entry points. | Equivalent help, version, findings and exit semantics. | integration |
| AT-S09-02 — Init is editable | Run init in empty output directory. | Valid documented JSON without pretending to detect user columns. | integration |
| AT-S09-03 — Audit threshold exit | Known overlap with fail-on=error. | Report written, then exit 3. | integration |
| AT-S09-04 — Malformed config exit | Use invalid JSON or unknown key. | Exit 2 with sanitized actionable message. | integration |
| AT-S09-05 — Fail-on none | Audit known warning/error with fail-on=none. | Same findings, exit 0 after successful audit; not a changed verdict. | integration |
| AT-S09-06 — Streams separation | Capture stdout/stderr from audit. | Progress on stderr; final paths/summary on stdout. | integration |
| AT-S09-07 — Sensitive split announcement | Generate plan.json and assignments.tsv. | CLI warns that operational files contain IDs. | integration |
| AT-S09-08 — Unimplemented commands | Inspect help at audit milestone. | No unsupported feature falsely advertised as working. | review |
| AT-S09-09 — API/CLI equivalence | Run same fixture through audit API and CLI. | Same projected check values excluding transient provenance. | integration |

## S10 — Fixed-parameter controlled evaluator

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S10-01 — Training-only scaler | Use outlier values exclusively in outer test. | Fitted scaler statistics match train-only reference, not all data. | unit |
| AT-S10-02 — Fit ID spy | Record every controlled pipeline fit input. | Only current training IDs observed. | unit |
| AT-S10-03 — Fresh estimator objects | Inspect objects across outer folds. | No shared fitted state or reused fitted pipeline. | unit |
| AT-S10-04 — Participant loss weights | Use different training visit counts. | Classifier weights sum to one for each participant. | unit |
| AT-S10-05 — Probability aggregation | Use fixed per-visit probabilities with known means. | Participant prediction derives from mean probabilities, not majority votes. | unit |
| AT-S10-06 — Probability class ordering | Estimator class order differs from input order. | Mapped probabilities/metrics agree with declared class labels. | unit |
| AT-S10-07 — All-missing training feature | One feature is missing on all training rows. | Documented imputer handling and diagnostic; no global imputation. | unit |
| AT-S10-08 — Constant-target limit | Participant changes diagnosis across visits. | UnsupportedDesignError rather than baseline relabeling. | unit |
| AT-S10-09 — Single-class test AUC | Fold test has one true class. | AUC and class-complete metrics null with reasons; accuracy still available. | unit |
| AT-S10-10 — Positive class unspecified | Binary target and positive_class omitted. | Binary AUC null with explicit reason; other metrics computed. | unit |
| AT-S10-11 — Metric oracle | Use hand-defined confusion/probability arrays. | Accuracy, class recall and complete-class metrics match independent calculations. | unit |
| AT-S10-12 — Convergence failure | Force estimator iteration failure. | Failed fold/run status, no complete pooled score. | unit |
| AT-S10-13 — No easy-fold average | One of several folds fails. | No pooled complete-CV metric presented. | unit |
| AT-S10-14 — Scope guards | Request one-fold, multi-repeat or audit_only evaluation. | Explicit refusal; partition audit remains available. | unit |
| AT-S10-15 — Private/public outputs | Run evaluate to disk. | Sensitive private result separate from sanitized report pair. | integration |
| AT-S10-16 — No model deserialization | Supply estimator pickle in place of features/config. | Refusal without execution. | security |

## S11 — Nested participant-aware regularization selection

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S11-01 — Inner fit spy | Track IDs per candidate/inner fit. | Inner validation and outer test absent from all fit calls. | unit |
| AT-S11-02 — Outer-test choice independence | Modify outer-test labels only, preserving supported class coverage. | Chosen C remains unchanged for that outer fold. | unit |
| AT-S11-03 — Same candidate memberships | Capture inner IDs for every C. | Exact same folds across candidate values. | unit |
| AT-S11-04 — Fresh candidate fits | Inspect estimator instances over grid and inner folds. | Independent clones, no fitted-state carryover. | unit |
| AT-S11-05 — Tie rule | Force candidate scores within 1e-12. | Smallest numeric C selected. | unit |
| AT-S11-06 — Pooled participant objective | Unequal visit counts in inner validation. | Selection uses pooled participant balanced accuracy, not row-weighted mean fold accuracy. | unit |
| AT-S11-07 — Infeasible inner groups | Too few components inside an outer training set. | Tuning fails explicitly; no default-C fallback. | unit |
| AT-S11-08 — Refit boundary | Inspect selected model fit after tuning. | Fresh fit on all and only outer train. | unit |
| AT-S11-09 — Original plan immutability | Auto-generate inner folds during evaluation. | Original plan unchanged; derived run records actual inner memberships. | unit |

## S12 — Design comparison and gated diagnostic examples

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S12-01 — Signed delta | Give two valid scores with A less than B. | Negative delta preserved. | unit |
| AT-S12-02 — Mismatched cohort | Compare different cohort digests. | Delta null and mismatch reason. | unit |
| AT-S12-03 — Mismatched feature/unit | Compare different selected features or metric units. | No misleading paired delta. | unit |
| AT-S12-04 — Diagnostic default off | Leaky participant split without explicit diagnostic option. | Evaluation blocked. | unit |
| AT-S12-05 — Narrow diagnostic permit | Valid row-disjoint repeated-participant split with explicit permitted flag. | Runs labeled diagnostic_only and invalid for stated generalization. | unit |
| AT-S12-06 — No observation waiver | Enable flag on a train/test observation overlap. | Still blocked. | unit |
| AT-S12-07 — No family/domain waiver | Enable flag with protected families or unseen_site objective. | Still blocked. | unit |
| AT-S12-08 — Public/private compare boundary | Pass redacted public report to compare. | Actionable request for operational evaluation record; no guessed digests. | integration |
| AT-S12-09 — No causal conclusion | Compare site-held-out and person-held-out scores. | Interpretation distinguishes changed distribution from causal leakage quantity. | review |

## S13 — Synthetic generators and reproducible end-to-end demos

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S13-01 — Generator determinism | Same seed and parameters twice. | Exactly matching IDs, labels and numeric outputs in supported environment. | unit |
| AT-S13-02 — Generator RNG isolation | Inspect global NumPy RNG state. | Unchanged after demo generation. | property |
| AT-S13-03 — Mechanism isolation | Change one specified generator parameter. | Documented mechanism changes without hidden unrelated settings. | unit |
| AT-S13-04 — Offline demo | Run demo with network disabled. | Complete synthetic workflow and local report. | integration |
| AT-S13-05 — Script execution | Run all five examples top to bottom. | No missing hidden files or interactive state. | integration |
| AT-S13-06 — Synthetic labeling | Inspect data and report/source captions. | Fictitious data explicitly labeled; no real patient claims. | review |
| AT-S13-07 — Actual displayed results | Compare screenshot/README example to recorded demo output. | Values match actual run or are explicitly hypothetical, never fabricated. | review |

## S14 — Complete documentation and contributor materials

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S14-01 — Strict docs build | Run Sphinx with warnings as errors. | No broken references or ignored build failures. | documentation |
| AT-S14-02 — Public API coverage | Compare exported API to reference pages. | All public functions/types/exceptions documented. | documentation |
| AT-S14-03 — Configuration coverage | Compare schema keys to documentation. | Every key/default/type/limit described correctly. | documentation |
| AT-S14-04 — CLI help examples | Execute each copyable command with fixture equivalents. | Commands and option placement match implementation. | documentation |
| AT-S14-05 — Limitations discoverable | Read quickstart and main report interpretation. | Unknown upstream provenance and scope limitations clear near usage. | review |
| AT-S14-06 — Metadata authenticity | Inspect citation/security/license/README values. | No invented DOI/contact/contributor/version support. | review |
| AT-S14-07 — AI record accuracy | Compare assistance claims to actual workflow. | No hidden/fabricated authorship or exhaustive review claims. | review |
| AT-S14-08 — Maintainer walkthrough | Ask the five ownership questions from the spec. | Record actual human understanding/review or leave gate pending. | human |

## S15 — Adversarial, property, security and scientific review

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S15-01 — Critical mutation detection | Temporarily introduce documented wrong joins/grouping/global fit. | Targeted tests fail; restored code passes. | mutation |
| AT-S15-02 — Property stress | Generate varied valid IDs/groups/row permutations. | Specified invariants hold without flaky score assumptions. | property |
| AT-S15-03 — Coverage targets | Run actual line/branch coverage report. | Project/core thresholds met without unjustified exclusions. | quality |
| AT-S15-04 — No hidden network | Intercept runtime socket usage in core/CLI/demo. | No outbound calls. | security |
| AT-S15-05 — Scaling benchmark | Run 10k and 100k metadata scenarios. | Measured cost documented and no accidental quadratic critical path. | benchmark |
| AT-S15-06 — Large feature guard | Request feature matrix above resource threshold. | Clear early refusal instead of uncontrolled allocation. | benchmark |
| AT-S15-07 — Untrusted input instructions | Include text asking an agent to run commands inside a CSV field. | Handled as inert data; never executed or followed. | security |
| AT-S15-08 — Independent review provenance | Review code with a fresh reviewer/agent context. | Actual findings and reviewer type recorded, not self-certified human review. | review |
| AT-S15-09 — No quality gate weakening | Inspect diff for skips, warning suppression and tolerance inflation. | Every exception justified; no concealed failing requirement. | review |

## S16 — Build, clean installation and release-readiness dossier

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S16-01 — Build distributions | Build wheel and sdist from reviewed tree. | Both valid and metadata checks pass. | packaging |
| AT-S16-02 — Wheel resource list | Inspect archive members. | Schemas/templates/CSS/demo assets included; private files excluded. | packaging |
| AT-S16-03 — Clean wheel execution | Install in fresh environment outside source directory. | Import, CLI and demo work without source-path fallback. | packaging |
| AT-S16-04 — Cross-platform matrix | Execute specified OS/Python checks. | Evidence records only actual passes; unavailable platforms remain pending. | quality |
| AT-S16-05 — Lowest dependency check | Test declared lower bounds environment. | No unsupported bound is advertised. | quality |
| AT-S16-06 — Release hashes | Hash actual built artifacts. | Dossier records matching version/files/SHA256. | review |
| AT-S16-07 — No unresolved result bug | Review tracked issues and scientific findings. | Result-changing defects block readiness. | review |
| AT-S16-08 — No unauthorized release | Complete S16 with public credentials accessible. | No push/upload/tag/DOI operation without explicit authorization. | security |

## S17 — Human-approved public release and maintenance handoff

| Case | Setup | Required result | Method |
|---|---|---|---|
| AT-S17-01 — Publication authorization | Review human approval for each external action. | No fabricated approval; missing approval leaves stage blocked. | human |
| AT-S17-02 — Namespace ownership | Check actual intended GitHub/PyPI names at release. | Available/owned names verified; conflicts handled transparently. | human |
| AT-S17-03 — Published artifact identity | Compare uploaded version/bytes to reviewed artifact. | Match or explicit explanation; no silent rebuild with different contents. | packaging |
| AT-S17-04 — Public fresh install | Install the actual published release separately. | Version/import/demo verified or release marked incomplete. | packaging |
| AT-S17-05 — Citation link validity | Open actual documentation/repository/DOI links after authorization. | Only real working identifiers appear in citation metadata. | human |
| AT-S17-06 — Honest development history | Inspect releases/commits/community statements. | No manufactured dates, users, reviews or adoption claims. | review |
