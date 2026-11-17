"""Writes site/status.json (the hub's status) and site/release.json (the latest release) before each deploy.

Run by .github/workflows/pages.yml every 15 minutes. "since" is carried over from the status.json that is
currently published, so "Offline since 14:05" survives between runs without any storage.
Environment: STATUS_URL (the hub's /status address), SITE_URL (the published site), GH_TOKEN, GITHUB_REPOSITORY.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

site = sys.argv[1] if len(sys.argv) > 1 else "site"
now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_json(url, headers=None, timeout=10):
    try:
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "DoomHub-Site-Status"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:  # offline, timeout, bad JSON...
        print("could not read", url, "-", e)
        return None


prev = get_json(os.environ.get("SITE_URL", "").rstrip("/") + "/status.json") or {}
hub = get_json(os.environ["STATUS_URL"])
if hub and hub.get("online"):
    state = "maintenance" if hub.get("maintenance") else "online"
    status = {
        "state": state,
        "players": int(hub.get("players", 0)),
        "rooms": int(hub.get("rooms", 0)),
        "version": str(hub.get("version", ""))[:20],
        "reason": str(hub.get("reason", ""))[:200] if state == "maintenance" else "",
        "checked": now,
        "since": prev.get("since", now) if prev.get("state") == state else now,
    }
else:
    status = {
        "state": "offline",
        "checked": now,
        "since": prev.get("since", now) if prev.get("state") == "offline" else prev.get("checked", now),
    }
with open(os.path.join(site, "status.json"), "w", encoding="utf-8") as f:
    json.dump(status, f)
print("status:", status)

repo = os.environ.get("GITHUB_REPOSITORY", "Marcus101RR/DoomHub")
headers = {"User-Agent": "DoomHub-Site-Status", "Accept": "application/vnd.github+json"}
if os.environ.get("GH_TOKEN"):
    headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
rel = get_json(f"https://api.github.com/repos/{repo}/releases/latest", headers) or {}
release = {}
if rel.get("tag_name"):
    exe = next((a for a in rel.get("assets", []) if a.get("name") == "DoomHub.exe"), {})
    release = {
        "version": rel["tag_name"].lstrip("vV"),
        "date": rel.get("published_at", ""),
        "url": exe.get("browser_download_url", rel.get("html_url", "")),
        "size": exe.get("size", 0),
    }
with open(os.path.join(site, "release.json"), "w", encoding="utf-8") as f:
    json.dump(release, f)
print("release:", release)
