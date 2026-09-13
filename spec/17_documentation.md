# 17 — Documentation, examples and community standards

## 17.1 Required documentation set

Write a concise top-level README and a complete Sphinx site. The README answers: what problem is addressed; what the package does not do; install instructions that actually work; a minimal demo; how to interpret a warning; where the full documentation/tests are; research-only status; license; support; and citation instructions once valid citation metadata exists.

The documentation must include installation and troubleshooting for Windows/Linux/macOS; a getting-started walkthrough; the input data dictionary; configuration reference; split objectives; rule catalog; reporting/privacy; controlled evaluation/tuning; limitations; Python API reference; CLI reference; contributor setup; testing; release procedure; and a glossary. Each documented configuration key and public function must be linked to a real contract/test.

A standard Sphinx/MyST site is sufficient [R14]. Do not design a custom documentation framework. Avoid large duplicated passages across README, API docs and tutorials; link to the authoritative page.

## 17.2 Wording and tone

Write direct sentences for researchers. Prefer “checks participant overlap in supplied folds” to “revolutionizes trustworthy neuro-AI.” Do not call the package production-ready, clinically validated, comprehensive, state-of-the-art or universally leakage-safe. State what is implemented now; label the roadmap separately.

Code comments explain why a boundary matters. Docstrings show a small real example and disclose important failure cases. Do not surround every helper with a paragraph of generated praise. Tables and figures must convey useful structure, not make an empty repository look mature.

## 17.3 Practical interpretation pages

Explain repeated sessions without automatically calling them leakage. Explain why unseen-site evaluation may be infeasible when a participant spans sites. Explain missing-class metrics and why a fold can have useful accuracy but undefined AUC. Explain why a global PCA declaration cannot be repaired by subsequently placing a scaler in a Pipeline. Explain that scanner–target association can be relevant without proving a model uses a shortcut.

Provide a short “What to do next” for each warning: inspect the supplied identities; choose an objective; curate an explicit cohort; obtain missing metadata; review acquisition imbalance; or document an unassessable operation. Do not prescribe medical action or silently perform cohort curation.

## 17.4 Governance files

Provide LICENSE, CONTRIBUTING.md, CHANGELOG.md, SECURITY.md, a code of conduct, issue templates for bug reports/methodological questions, and a pull-request checklist. Select BSD-3-Clause as the proposed project license; final copyright ownership requires maintainer confirmation before public release. Do not copy third-party code under an incompatible license.

Use CITATION.cff only with verified actual author identity, repository/version and release date. Do not invent an ORCID, DOI, institution or paper. No citation badge until it resolves correctly. Package-name availability, GitHub namespace and documentation URL must be checked at release time.

SECURITY.md must explain that reports may contain sensitive data and provide a real approved contact path. Until a private contact is supplied, mark public release blocked rather than publishing a fake security address. Internal templates may have clearly labeled owner-confirmation fields; a public release may not.

## 17.5 Transparent AI assistance

Maintain AI_ASSISTANCE.md recording actual tools, dates or versions where known, types of assistance and human review performed. Do not invent a model version that was not recorded. Avoid both disguising assistance and making unsupported claims of exhaustive review. A factual entry can say that AI assisted with code drafting and tests, followed by named human review of specified parts when it actually occurs.

Current JOSS policy allows AI assistance with disclosure and human accountability [R18]. This is not blanket permission from every journal or university. Re-check the intended venue before submission. The repository should demonstrate actual readable work and verification, not a fabricated persona or history.

## 17.6 Human usability trial

Before release, ask an independent researcher or technically competent tester to install from a clean wheel and complete the synthetic demo plus a column-mapping exercise without verbal coaching. Record actual friction and fix it. No real external tester is assumed to exist; absence of this feedback remains a documented release-readiness limitation. An agent-run walkthrough can supplement but cannot be relabeled external user feedback.

The maintainer should be able to explain one participant-overlap case, one impossible site split, one inner-loop leakage test, one undefined metric, and one privacy limitation without reading generated code aloud. This is a practical ownership check, not a test of writing style.
