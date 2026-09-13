# 01 — Scientific contract and permitted claims

## 1.1 Terms that must remain distinct

**Observation:** one explicitly keyed row, such as a processed scan, visit, run or feature record. **Participant:** the person whose data generated one or more observations. **Session:** a participant-local label; `ses-01` occurring for many people is normal. **Independence component:** participants connected by any declared protected relationship, such as family or verified duplicate identity. **Domain:** a site or acquisition phase the researcher intends to hold out. **Split:** the training and test observation IDs for one repeat/fold. **Evaluation objective:** the population to which performance is intended to generalize.

A repeated participant in a cohort is not itself leakage. The same participant on both sides of a split is an observed overlap; it violates a claim about unseen participants. A site shared by training and test is not automatically leakage: it may be appropriate for new people at known sites. Site–diagnosis association is a distributional fact, not proof that a trained model used a shortcut. A held-out-site estimate and a within-site estimate answer different questions.

## 1.2 Supported objectives

| `study.objective` | Mandatory separation | Meaning |
|---|---|---|
| `unseen_participant` | Participant and every protected independence component | New people under the represented acquisition setting |
| `unseen_site` | Participant, protected components, and site | People at a site not used for training |
| `unseen_phase` | Participant, protected components, and acquisition phase | People from a phase not used for training |
| `audit_only` | Describe overlaps; no automatic valid-design conclusion | Inspect supplied information without claiming a supported prediction target |

The evaluator refuses `audit_only`. Within-person prediction is not interchangeable with unseen-person prediction and is unsupported in v0.1.0. The project does not designate a universally safest objective. Recommendations must be conditional: “For a claim about new sites, use site-held-out evaluation.”

## 1.3 Evidence model

Every check records a stable rule ID, status, severity, evidence kind, scope and explanation. Evidence kind is one of `observed`, `declared`, `heuristic`, or `unassessable`. A direct set intersection is observed evidence. A user's assertion that PCA was fitted globally is declared evidence. Identical feature vectors are observed equality but only a heuristic indication of duplicated acquisition. Unknown upstream preprocessing is unassessable.

A plain external file cannot authenticate how another program actually ran. Imported provenance is always treated as declared, even if its text says “runtime verified.” Runtime fit events captured by NeuroCVguard's own evaluator can be marked observed for that run only. They do not certify earlier feature extraction.

A check status is `pass`, `fail`, `not_assessable`, or `not_applicable`. A pass means that particular check was evaluated and found no violation under its stated assumptions. A missing site column is `not_assessable` for a requested site check, never pass. Keep the coverage inventory visible beside the finding list.

## 1.4 Disallowed inferences

Never infer any of the following from a clean audit: all upstream operations were fold-local; participants with different IDs are definitely different people; images were correctly processed; labels were clinically valid; a model is fair; site and diagnosis are causally confounded; deployment performance will equal cross-validation performance; the study meets regulatory requirements.

A `Pipeline` encapsulates transformations that it contains; it cannot undo feature selection, atlas learning, harmonization, or preprocessing already performed globally. The implementation must retain an explicit upstream-provenance limitation even when all internal fitting events are correct. This boundary follows the distinction between controlled fitting and unknown prior transformations [R03, R05].

## 1.5 Comparison wording

Replace the earlier conversational idea `compare_naive_vs_safe()` with the neutral API `compare_designs()`. Report `design_A_score - design_B_score` as a **descriptive design difference**, including sign and metric unit. Do not call every difference an “estimated leakage bias” or assume it is positive. A change to held-out sites changes the evaluation distribution. A decrease can reflect genuine domain shift, different training sizes, class coverage or sampling, not just leakage.

Only a controlled synthetic experiment that holds other design choices fixed can support a narrowly stated attribution to the manipulated mechanism. Even there, the claim applies to that simulation, not all neuroimaging studies. Reusing cross-validation scores to select the most flattering design invalidates a confirmatory interpretation.

## 1.6 Test-set adaptation and clinical language

Exploratory cohort audits may expose label distributions. Once a final test set is designated, repeated inspection followed by model redesign is a research governance issue the software cannot reconstruct. Documentation must tell users to freeze an evaluation plan and record subsequent amendments. A split generator must never search seeds until the most flattering score appears.

Use “target,” “class,” “participant,” “evaluation,” and “research baseline.” Do not label the logistic baseline a clinical diagnostic system. A participant-level audit report is research support, not advice for an individual patient.

## 1.7 Reporting completeness

Every human-facing report must contain: stated objective; supplied/missing inputs; assessed checks; unassessable checks; observed violations; descriptive distribution diagnostics; next actions; software/configuration provenance; and limitations. Absence of violations must not visually conceal incomplete coverage. No trust score, traffic-light percentage, certified seal, or universal low/medium/high scientific-validity score is authorized.
