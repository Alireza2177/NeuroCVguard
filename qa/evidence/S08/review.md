# S08 implementing-agent review

Review by the implementing Codex agent, 2026-09-26. This is neither independent
review nor human acceptance. All fixtures are synthetic; no clinical result is claimed.

The source/diff review covered shared projection, renderer, templates, writer,
public wrapper, rule registration, tests and docs. Existing computation, participant
grouping, split identity, evaluation schema and normative files remain unchanged.
Rendering consumes the same projection as JSON and performs no statistical fits.
Unknown preprocessing stays unassessable, failed folds remain present, and design
differences are explicitly descriptive. No trust score or safety certificate appears.

Public projection removes open identity/path-bearing text, aliases visible domain
labels and suppresses whole linked tables when small cells exist. Alias compaction
prevents suppressed labels from changing a later public rerender. A dedicated test
checks this mixed-table case. Eligible tables display only allowlisted precomputed
counts/statistics, never recomputed statistics or hidden raw payloads. Existing
metric suppression and private operational serializers are preserved.

HTML uses autoescaping, no safe/Markup bypass, an inline fixed stylesheet, CSP and
no script. Tests cover closing tags, event attributes, quotes and long Unicode text;
optional findings CSV neutralizes formula prefixes without changing machine keys.
Sensitive detail requires an explicit boolean and a visible warning. JSON/HTML
artifacts never include operational plans or private prediction files automatically.

Write tests inject failures at every replacement position and during staging,
verify prior report bytes and unrelated files, refuse overwrite, preserve another
writer's lock and remove only invocation-owned new artifacts. Recovery is per-file
atomic with ordinary failure rollback, not a multi-file power-loss transaction.

## Actual visual review

`render_fixtures.py` executed a 20-participant, 40-observation synthetic audit with
two fictitious sites, balanced target groups, missing phase context and unknown
preprocessing. It wrote public and explicitly sensitive HTML/JSON/manifest bundles.
The sensitive fixture includes malicious script/image text only for escaping QA.

A temporary local server was run with:

`.venv/Scripts/python.exe -m http.server 8878 --bind 127.0.0.1 --directory qa/evidence/S08/rendered`

The Codex in-app browser opened both reports. Actual screenshots are public-top.png,
public-associations.png, sensitive-top.png and sensitive-escaped-text.png. The browser
showed readable headings, labelled amber incomplete coverage before findings, site
aliases/count tables and the red sensitive warning. Injected tags appeared as text;
the DOM contained zero script/image elements and there was no JavaScript dialog.
Pressing Enter on the Coverage contents link navigated to #coverage. The eleven
headings were in the specified order and no horizontal page overflow was observed
at the default 1265-by-712 screenshot viewport. browser-review.json records the
DOM observations. The temporary tab was closed and server stopped intentionally
with Ctrl+C (server exit 1); it is not a product service.

The renderer test blocks Python socket creation and verifies inline CSS/internal
links with no external asset tags. Browser review was local, but the browser's
network adapter was not disabled. Print CSS is tested structurally; physical print
and a multi-browser/mobile accessibility matrix were NOT RUN. No claims are based
on an imagined screenshot. check_rendered.py verifies the reviewed HTML is exactly
reproducible by the final renderer; asset checks compare actual wheel/sdist bytes.

The initial rendering and full-suite failures were invalid test fixtures (incomplete
evaluation retaining pooled metrics; renamed classes retaining an old positive class).
They were corrected without loosening contract checks. Earlier lint/type failures
were fixed in implementation/helpers; all failed command records remain. Build and
install dependency access failures were retried with explicit sandbox escalation.

The first reviewed-artifact helper compared a sensitive report reconstructed from
canonical JSON with HTML produced from the original record, exposing only changed
dictionary display order. The corrected helper regenerates the same original
synthetic inputs in a fresh temporary directory and verifies all six artifact bytes.

ComparisonResult keeps its existing standalone schema. A versioned manifest names
that schema instead of inventing an audit inventory. No normative conflict or schema
change was introduced. S09 CLI, evaluation, ingestion, publication and human review
remain outside this stage.
