# sp_folder_graph.py
"""
SharePoint / OneDrive helper functions via Microsoft Graph.

This file is intentionally lightweight and safe:
- Works in Streamlit Cloud
- Uses plain requests
- Provides resolve_site_id (required by IR_gen)
"""

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
    Resolve a SharePoint Site ID from a standard site URL.

    Example:
        site_url = "https://tenant.sharepoint.com/sites/SMCOD"
    """
    u = urlparse(site_url)
    host = u.netloc
    path = u.path.rstrip("/")

    if not host or not path:
        raise ValueError(f"Invalid site_url: {site_url}")

    # Graph site addressing format:
    # /sites/{hostname}:{server-relative-path}
    url = f"{GRAPH_ROOT}/sites/{host}:{path}"

    r = requests.get(url, headers=_headers(access_token), timeout=30)
    r.raise_for_status()
    data = r.json()

    if "id" not in data:
        raise RuntimeError(f"Could not resolve site id from: {site_url}. Response: {data}")

    return data["id"]


def resolve_drive_id(access_token: str, site_id: str) -> str:
    """
    Resolve the default document library drive ID for the given site.
    """
    url = f"{GRAPH_ROOT}/sites/{site_id}/drive"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    r.raise_for_status()
    data = r.json()

    if "id" not in data:
        raise RuntimeError(f"Could not resolve drive id. Response: {data}")

    return data["id"]


def resolve_folder_id_by_path(access_token: str, drive_id: str, folder_path: str) -> str:
    """
    Resolve a folder item id by path within a drive.

    folder_path examples:
      - "Shared Documents/Reports"
      - "/Shared Documents/Reports"
    """
    folder_path = folder_path.lstrip("/")
    url = f"{GRAPH_ROOT}/drives/{drive_id}/root:/{folder_path}"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    r.raise_for_status()
    data = r.json()

    if "id" not in data:
        raise RuntimeError(f"Could not resolve folder id for path '{folder_path}'. Response: {data}")

    return data["id"]


def list_children(access_token: str, drive_id: str, folder_item_id: str) -> list[dict]:
    """
    List child items of a folder item id (files/folders).
    """
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{folder_item_id}/children"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("value", [])


def upload_file_to_folder(
    access_token: str,
    drive_id: str,
    folder_path: str,
    filename: str,
    content: bytes,
) -> dict:
    """
    Upload a small file (<4MB) directly into a SharePoint folder by path.
    For larger files, use upload session (not included here unless you need it).
    """
    folder_path = folder_path.strip("/")

    if folder_path:
        upload_url = f"{GRAPH_ROOT}/drives/{drive_id}/root:/{folder_path}/{filename}:/content"
    else:
        upload_url = f"{GRAPH_ROOT}/drives/{drive_id}/root:/{filename}:/content"

    r = requests.put(upload_url, headers=_headers(access_token), data=content, timeout=60)
    r.raise_for_status()
    return r.json()
