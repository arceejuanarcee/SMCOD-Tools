# sp_folder_graph.py
from __future__ import annotations

from urllib.parse import urlparse
import requests

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"


def _headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }


def resolve_site_id(access_token: str, site_url: str) -> str:
    """
    Resolve SharePoint Site ID from URL.
    Example: https://tenant.sharepoint.com/sites/SMCOD
    """
    u = urlparse(site_url)
    host = u.netloc
    path = u.path.rstrip("/")

    if not host or not path:
        raise ValueError(f"Invalid SHAREPOINT_SITE_URL: {site_url}")

    url = f"{GRAPH_ROOT}/sites/{host}:{path}"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    r.raise_for_status()
    data = r.json()

    if "id" not in data:
        raise RuntimeError(f"resolve_site_id() failed. Response: {data}")

    return data["id"]
