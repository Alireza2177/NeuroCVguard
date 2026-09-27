# Security and sensitive research data

NeuroCVguard runs locally and accepts strict CSV/TSV/JSON. It does not expose a
network service, fetch remote schemas, execute input instructions, or load
pickle/joblib/YAML models. Resource limits and HTML escaping reduce risks; they
do not make arbitrary data safe to publish.

Split plans, assignments, configs, preprocessing ledgers and private evaluation
records may identify participants. Default reports remove selected identifiers
and suppress small cells but are not guaranteed anonymous. Explicit sensitive
reports retain more information. Keep files in authorized local storage; review
every attachment before sharing. Debug output is not permission to disclose data.

Report security concerns privately to maintainer Alireza Emad at
[Alireza221177@gmail.com](mailto:Alireza221177@gmail.com). Include the affected
version and a minimal synthetic reproduction. Do not include patient data,
credentials or sensitive research files, and do not post an unreviewed
vulnerability or sensitive example in a public issue.

The maintainer approved this contact during S17. No response-time or long-term
support commitment is promised. For a confirmed scientific-result defect, retain
the affected version and original outputs; a correction will be documented rather
than silently changing published artifacts.
