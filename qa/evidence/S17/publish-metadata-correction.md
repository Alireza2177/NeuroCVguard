# Publishing action compatibility correction

The owner completed the protected deployment review for run 36300178736.
GitHub displayed “The deployments have been approved.” Download and reviewed-byte
verification succeeded. The pinned v1.13.0 publishing container then refused:

```text
InvalidDistribution: Invalid distribution metadata: '2.5' is not a valid metadata version
```

No package upload occurred in that attempt. The approved distributions passed the
current local Twine check; the failure is the older action's metadata parser.
Official v1.14.2 release notes explicitly identify Twine 7 and core metadata 2.5
support: https://github.com/pypa/gh-action-pypi-publish/releases/tag/v1.14.2.
The official tag resolves to dc37677b2e1c63e2034f94d8a5b11f265b73ba33.
Its manifest was read and retained in publish-action-upgrade.json. It still uses
Linux, scoped OIDC, verified metadata and a pinned internal setup action. This is
bounded provenance/manifest review, not an exhaustive dependency audit.

Only the external action pin changes. Package files, release tag, hash verifier,
workflow identity, environment review, main-only rule and permissions are unchanged.
No metadata bypass, static credential or skip-existing workaround is introduced.
The new manual run still needs the required owner's deployment approval. The full
source matrix need not be repeated for this publishing-tool-only change.
