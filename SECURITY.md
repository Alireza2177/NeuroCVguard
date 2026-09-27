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

**Public release is blocked until the maintainer supplies and approves a real
private security contact.** No email address, reporting URL or response-time
promise is invented here. Until then, contact the owner through your existing
private project channel. Do not publish a vulnerability containing patient data
or upload sensitive examples to a public issue. A minimal synthetic reproduction
and affected local version are sufficient for an initial report.
