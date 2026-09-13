# 00 — Project charter and release boundary

**Project:** NeuroCVguard. **Python distribution, import and command:** `neurocvguard`.
**Foundation version:** 1.0.0, prepared 12 September 2026.
**Target:** a maintainable research-software package, not a clinical product, a journal submission, or a collection of disconnected notebooks.
**Document status:** implementation specification. No NeuroCVguard software has been implemented or validated by delivering this foundation.

## 0.1 Product statement

NeuroCVguard helps researchers inspect whether the data partitions and evaluation procedures used for neuroimaging machine learning match their intended generalization claim. It reads local cohort tables, optional numeric feature tables, explicit split assignments, and optional preprocessing declarations. It reports participant and dependency overlap, requested site/phase separation violations, incomplete assessments, acquisition–target associations, and evaluation limitations. It can generate subject-disjoint or domain-held-out partitions and run a small, controlled classification baseline. It produces human-readable offline HTML and structured JSON reports with evidence, limitations, and practical next actions.

It does not look inside MRI images, diagnose a patient, certify a study as leakage-free, determine causal confounding, or infer the history of an arbitrary feature matrix. “No violation detected in the supplied information” is the strongest permitted clean-result claim.

## 0.2 Why this project exists

The project grows from real methodological questions in multimodal MRI, repeated-session data, held-out-site evaluation, and acquisition-phase robustness. Its first useful output is not a new classifier: it is a reproducible description of which evaluation assumptions can and cannot be checked. Existing scikit-learn components should do ordinary splitting, fitting, and scoring; NeuroCVguard adds explicit identities, constraints, diagnostics, provenance boundaries, reports, and tests.

The proposed architecture and thresholds below are project decisions, not findings from a publication. Scientific background and external software facts are separately identified in the source register. No claim that this is the first, only, or best leakage-auditing package is authorized.

## 0.3 Users and principal workflows

| User | Input they already have | Useful outcome |
|---|---|---|
| Graduate researcher | CSV/TSV of participants, visits, labels and sites | An understandable pre-model audit and a defensible split file |
| Neuroimaging analyst | Extracted regional/connection features and explicit cohort keys | A fold-local baseline and reproducible evaluation report |
| Reviewer or collaborator | Exported split assignments and method declarations | Verifiable overlaps and a list of unanswered questions |
| Methodological researcher | Synthetic scenarios and independent reference implementations | Reproducible test and benchmark evidence without patient data |

The ordinary first-run experience is: install locally; run a bundled synthetic demo; inspect the HTML; map the user's own table columns in one JSON configuration; validate; audit; create a split; optionally evaluate; inspect limitations. This must work without an API key, online account, GPU, or network connection after installation.

## 0.4 Fixed first-release scope

The complete requested first release is **v0.1.0**. It includes CSV/TSV ingestion, strict keyed joins, explicit configuration, identity/dependency diagnostics, imported split auditing, group-aware split generation, descriptive categorical association diagnostics, declared-versus-observed preprocessing provenance, offline HTML/JSON reports, a command-line interface, a Python API, a restricted logistic-regression baseline, optional nested selection of its regularization parameter, design comparisons, synthetic examples, tests, documentation, installation checks and release procedures.

The baseline is intentionally limited to binary and multiclass classification with a **constant target per participant**. The audit can describe longitudinal data with changing diagnoses, but v0.1.0 must not silently turn it into a participant-level classification experiment. Unsupported cases are reported, not repaired by a convenient assumption.

An internal **audit milestone** after stage S09 is already useful but is not permission to advertise the complete v0.1.0 feature set. The first release is ready only after S16. External publication is a separate human-controlled operation in S17.

## 0.5 Explicit non-goals

Do not build a new neuroimaging preprocessing pipeline, NIfTI/DICOM reader, segmentation system, atlas, connectivity estimator, BIDS validator, harmonization implementation, causal-inference engine, automated paper writer, web service, cloud upload portal, desktop installer, neural-network framework, or broad AutoML platform. Do not add a proprietary LLM/API dependency. Do not implement arbitrary plugin loading, estimator deserialization, notebook execution on user input, or remote dataset downloads.

Regression, within-person forecasting, survival outcomes, multilabel tasks, missing-label semi-supervision, temporal leakage detection, fuzzy image duplicates, calibrated uncertainty claims, inferential permutation tests, automated ComBat, and arbitrary-estimator tuning belong to a reviewed later roadmap. Detect unsupported requests explicitly.

## 0.6 Delivery and authorship standards

Use conventional, readable names, small functions, ordinary package structure, scientific references, useful docstrings, and concise documentation. Avoid promotional adjectives, emoji-filled README files, repeated boilerplate comments, enormous generated classes, meaningless abstractions, and unsupported badges. This is how the repository earns credibility.

Do not fabricate users, testimonials, contributor names, peer review, performance numbers, historical commits, stars, downloads, publication acceptance, DOI identifiers, or continuous-integration results. Do not deliberately add mistakes or hide AI assistance to simulate a human development history. Record substantive AI assistance and actual human review in a development record; public disclosures must match applicable venue requirements. Authorship and release responsibility remain with the human maintainer.

## 0.7 Resource discipline

Use CPU-only tests and small local fixtures. Default to one worker. No long simulation campaign belongs in the ordinary unit suite. A change that expands research scope, adds a production dependency, relaxes a safety constraint, or changes an evaluation population requires a decision record before implementation. When a requirement cannot be satisfied, leave it visibly blocked rather than manufacturing success.

Success means a newcomer can reproduce the documented demo from an installed wheel, understand its warnings, and safely apply the same workflow to their own authorized tables. A large file count or a green badge alone is not success.
