"""Read public service metadata without credentials or remote mutations."""

import datetime
import json
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINTS = {
    "repository": "https://api.github.com/repos/Alireza2177/NeuroCVguard",
    "releases": "https://api.github.com/repos/Alireza2177/NeuroCVguard/releases?per_page=100",
    "tags": "https://api.github.com/repos/Alireza2177/NeuroCVguard/tags?per_page=100",
    "pypi": "https://pypi.org/pypi/neurocvguard/json",
}


def main():
    records = []
    for name, url in ENDPOINTS.items():
        record = {
            "name": name,
            "url": url,
            "checked_at_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        request = urllib.request.Request(url, headers={"User-Agent": "NeuroCVguard-release-check"})
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                record["http_status"] = response.status
                data = json.load(response)
            if name == "repository":
                record["metadata"] = {
                    key: data.get(key)
                    for key in (
                        "full_name",
                        "html_url",
                        "private",
                        "visibility",
                        "default_branch",
                        "archived",
                        "has_pages",
                    )
                }
                record["owner_login"] = data.get("owner", {}).get("login")
            elif name in {"releases", "tags"}:
                record["entries"] = [
                    {
                        key: item.get(key)
                        for key in (
                            ("tag_name", "html_url", "draft", "prerelease", "published_at")
                            if name == "releases"
                            else ("name", "commit")
                        )
                    }
                    for item in data
                ]
                record["scope"] = "First 100 public entries only."
            else:
                record["metadata"] = {
                    key: data["info"].get(key) for key in ("name", "version", "project_url")
                }
                record["releases"] = sorted(data.get("releases", {}))
        except urllib.error.HTTPError as error:
            record["http_status"] = error.code
            record["interpretation"] = (
                "No public resource returned; not proof of name availability or account ownership."
            )
        except (OSError, ValueError) as error:
            record["error_type"] = type(error).__name__
            record["interpretation"] = "Check unavailable; ownership/availability unverified."
        records.append(record)
    destination = Path(__file__).with_name("namespaces.json")
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2)
        handle.write("\n")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
