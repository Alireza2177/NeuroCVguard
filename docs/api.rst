Python API
==========

The root API below is intentional. Use keyword-only options. Calls do not
read implicit project configuration. See contracts for serialization/privacy
and the linked workflow guides for prerequisites and failure policies.

neurocvguard
------------

.. autofunction:: neurocvguard.compare_designs

.. autofunction:: neurocvguard.evaluate_baseline

.. autofunction:: neurocvguard.load_config

.. autofunction:: neurocvguard.load_cohort

.. autofunction:: neurocvguard.audit_cohort

.. autofunction:: neurocvguard.make_splits

.. autofunction:: neurocvguard.load_split_plan

.. autofunction:: neurocvguard.audit_splits

.. autofunction:: neurocvguard.write_report

neurocvguard.config
-------------------

.. autoclass:: neurocvguard.config.Objective

.. autoclass:: neurocvguard.config.SplitScheme

.. autoclass:: neurocvguard.config.ConfigRecord

.. autoclass:: neurocvguard.config.ColumnMap

.. autoclass:: neurocvguard.config.StudyConfig

.. autoclass:: neurocvguard.config.SplitConfig

.. autoclass:: neurocvguard.config.AssociationConfig

.. autoclass:: neurocvguard.config.EvaluationConfig

.. autoclass:: neurocvguard.config.ReportConfig

.. autoclass:: neurocvguard.config.LimitsConfig

.. autoclass:: neurocvguard.config.AuditConfig

.. autofunction:: neurocvguard.config.load_config

neurocvguard.models
-------------------

.. autoclass:: neurocvguard.models.CheckStatus

.. autoclass:: neurocvguard.models.Severity

.. autoclass:: neurocvguard.models.EvidenceKind

.. autoclass:: neurocvguard.models.ReportStatus

.. autoclass:: neurocvguard.models.EvaluationStatus

.. autoclass:: neurocvguard.models.FoldStatus

.. autoclass:: neurocvguard.models.PlanOrigin

.. autoclass:: neurocvguard.models.PlainRecord

.. autoclass:: neurocvguard.models.MetricValue

.. autoclass:: neurocvguard.models.ClassMetric

.. autoclass:: neurocvguard.models.MetricSet

.. autoclass:: neurocvguard.models.CheckResult

.. autoclass:: neurocvguard.models.InnerFold

.. autoclass:: neurocvguard.models.SplitFold

.. autoclass:: neurocvguard.models.SplitPlan

.. autoclass:: neurocvguard.models.CandidateScore

.. autoclass:: neurocvguard.models.EvaluationFold

.. autoclass:: neurocvguard.models.FitEvent

.. autoclass:: neurocvguard.models.EvaluationResult

.. autoclass:: neurocvguard.models.ComparisonContext

.. autoclass:: neurocvguard.models.ComparisonDesign

.. autoclass:: neurocvguard.models.MetricDifference

.. autoclass:: neurocvguard.models.ComparisonResult

.. autoclass:: neurocvguard.models.AuditReport

.. autoclass:: neurocvguard.models.LedgerEvent

.. autoclass:: neurocvguard.models.PreprocessingLedger

.. autoclass:: neurocvguard.models.Cohort

neurocvguard.errors
-------------------

.. autoclass:: neurocvguard.errors.NeuroCVguardError

.. autoclass:: neurocvguard.errors.ConfigurationError

.. autoclass:: neurocvguard.errors.InputValidationError

.. autoclass:: neurocvguard.errors.SplitValidationError

.. autoclass:: neurocvguard.errors.UnsupportedDesignError

.. autoclass:: neurocvguard.errors.PlanningError

.. autoclass:: neurocvguard.errors.EvaluationError

Records inherit from_dict/from_json for strict schema parsing where applicable.
to_dict returns a detached public projection for reports/results. SplitPlan and
PreprocessingLedger require to_operational_dict; EvaluationResult offers both.
SplitPlan.write writes sensitive plan.json/assignments.tsv with no overwrite
unless requested. summary returns text. Cohort properties return copies.

Implementation helpers outside this inventory are not a stability promise.
The documented synthetic interface is in the synthetic guide; lower-level
helpers mentioned by methodological guides retain their stated boundaries.
