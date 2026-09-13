# 13 — Offline reports, usability and privacy projection

## 13.1 Default report structure

Produce a self-contained HTML page that opens locally without a server, JavaScript, external fonts, analytics, CDN assets or internet access. Use a standard readable layout, real headings, tables with captions, a compact contents index, keyboard-accessible links and print CSS. An attractive report is helpful; a complex dashboard framework is unnecessary.

Sections appear in this order: scope/objective; execution and coverage summary; actionable violations; cohort and missingness summary; partition checks; acquisition association diagnostics; optional evaluation/comparison; provenance; limitations; recommended next actions; rule/source references. Always distinguish not_assessable from pass. Show both labels and colors; never make color the only signal.

Critical messages come before graphs or scores. Clean wording is conditional and scoped. Example: “No participant overlap was found in the supplied folds. Upstream feature preprocessing was not verified.” Do not show an unconditional green “safe” banner.

## 13.2 Structured data first

JSON is the machine-readable report contract; HTML renders the same projected result. Rendering must not rerun associations, regroup participants or recalculate metrics. The report projection is tested separately from the core record, and both serialization paths share it. Numeric display rounding is not written back into the computation result.

The CLI `report` command can render a previously exported compatible public report JSON; it cannot recover identifiers or details removed during projection. Version mismatches and malformed JSON fail clearly.

## 13.3 Privacy boundary

By default, do not export raw participant/observation IDs, individual feature values, full filesystem paths, email addresses, per-person predictions, or original domain/category labels that act as site identifiers. Alias domain labels deterministically within each report (Site 01, Site 02; Phase 01, etc.) without publishing the reverse mapping. Target class names may be shown because their semantic interpretation is essential, but document that even aggregates can be sensitive.

Default positive cell counts below report.small_cell_threshold are suppressed. When a table has suppressed cells, omit all row/column totals, percentages and derived association statistics from that **exported table section**, including its embedded/public JSON representation, to avoid easy reconstruction. Internal analysis results remain available through the local Python object, which is not a public anonymous export. This suppression is not a formal anonymization guarantee, differential privacy or proof of compliance.

`report.sensitive_details=true` explicitly enables a sensitive local report/projection, with a visible “Sensitive research output: do not publish without review” label. It may include raw finding IDs/evidence and unsuppressed tables. The user remains responsible for authorization and sharing. No option sends output anywhere automatically.

## 13.4 Split artifacts differ from reports

A usable split plan necessarily contains observation IDs. Therefore `plan.json` and `assignments.tsv` are **sensitive operational files**, not privacy-projected public reports. The CLI must announce this distinction when creating them. Keep default real-data outputs under an ignored local output directory and use restrictive permissions where supported. Do not include operational plans or raw prediction files inside a convenient public-report zip by default.

Dataset digests are also not anonymization. Default public report provenance omits full raw-data hashes and machine usernames; a private local manifest may retain digests for reproducibility. Separate public shareability from local reproducibility instead of pretending one file automatically serves both safely.

## 13.5 Escaping and injection protection

Enable Jinja2 autoescaping for all user-originating content. Do not apply safe/Markup to dataset strings. Embed no raw user JSON in script tags; JavaScript is not needed. Test malicious cells such as closing tags, script markup, event handlers, quotes and long Unicode names. They must render as text, never code.

For human spreadsheet-oriented finding CSV exports, neutralize formula-leading strings beginning with =, +, -, @, tab or carriage return. Do not silently change observation keys in canonical machine TSV/JSON files; validate canonical identifiers and warn that machine files should not be treated as sanitized spreadsheet reports. Keep machine assignments separate from optional safe human tables.

## 13.6 Filesystem and report failures

Writes are atomic: build temporary files in the output parent, validate them, then rename. Refuse overwriting existing outputs unless `--overwrite` is explicit. Never delete unrelated files or recursively clean a user directory. A report error must not erase a previously good report. All bundled assets must be present in the built wheel and sdist.

The core report is static. Optional diagrams can be ordinary tables or locally generated, accessible SVG with safe fixed labels; do not add charts solely to imitate a polished product. A screenshot used in README must come from a real executed demo.
