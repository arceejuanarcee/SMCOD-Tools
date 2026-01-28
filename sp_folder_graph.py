# sp_folder_graph.py
"""
SharePoint helper functions via Microsoft Graph for SMCOD tools.

This module is designed to match the function names used by IR_gen.py:
- resolve_site_id
- get_default_drive_id
- ensure_path
- list_incident_folders
- list_files
- download_file_bytes
- upload_file_to_folder
- check_duplicate_ir
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional
from urllib.parse import urlparse

import requests

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}


def _raise_for_graph(r: requests.Response):
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        # Include Graph error body for debugging
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"Graph request failed: {e} | detail={detail}") from e


def resolve_site_id(access_token: str, site_url: str) -> str:
    """
    Resolve a SharePoint Site ID from a standard site URL.
    Example:
        https://tenant.sharepoint.com/sites/SMCOD
    """
    u = urlparse(site_url)
    host = u.netloc
    path = u.path.rstrip("/")

    if not host or not path:
        raise ValueError(f"Invalid SHAREPOINT_SITE_URL: {site_url}")

    url = f"{GRAPH_ROOT}/sites/{host}:{path}"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    _raise_for_graph(r)
    data = r.json()

    if "id" not in data:
        raise RuntimeError(f"resolve_site_id() failed. Response: {data}")
    return data["id"]


def get_default_drive_id(access_token: str, site_id: str) -> str:
    """
    Returns the default document library (drive) ID for the site.
    Graph endpoint: GET /sites/{site-id}/drive
    """
    url = f"{GRAPH_ROOT}/sites/{site_id}/drive"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    _raise_for_graph(r)
    data = r.json()

    if "id" not in data:
        raise RuntimeError(f"get_default_drive_id() failed. Response: {data}")
    return data["id"]


def _get_child_by_name(access_token: str, drive_id: str, parent_item_id: str, name: str) -> Optional[dict]:
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{parent_item_id}/children"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    _raise_for_graph(r)
    items = r.json().get("value", [])
    for it in items:
        if it.get("name") == name:
            return it
    return None


def _create_folder(access_token: str, drive_id: str, parent_item_id: str, name: str) -> dict:
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{parent_item_id}/children"
    payload = {
        "name": name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "fail",
    }
    r = requests.post(url, headers={**_headers(access_token), "Content-Type": "application/json"}, json=payload, timeout=30)
    _raise_for_graph(r)
    return r.json()


def _resolve_path_item(access_token: str, drive_id: str, path: str) -> dict:
    """
    Resolve an item by path. Path should be like:
      "Ground Station Operations/Incident Reports/2026/Davao City"
    Graph: GET /drives/{drive-id}/root:/{path}
    """
    path = path.strip("/")

    url = f"{GRAPH_ROOT}/drives/{drive_id}/root:/{path}"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    _raise_for_graph(r)
    return r.json()


def ensure_path(access_token: str, drive_id: str, root_path: str, parts: List[str]) -> dict:
    """
    Ensure folders exist for: root_path / parts[0] / parts[1] / ...
    Returns the final folder item metadata.
    """
    # First resolve the root_path item
    root_item = _resolve_path_item(access_token, drive_id, root_path)
    parent_id = root_item["id"]

    for name in parts:
        existing = _get_child_by_name(access_token, drive_id, parent_id, name)
        if existing is None:
            existing = _create_folder(access_token, drive_id, parent_id, name)
        parent_id = existing["id"]

    # Return final item metadata
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{parent_id}"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    _raise_for_graph(r)
    return r.json()


def list_incident_folders(access_token: str, drive_id: str, base_path: str) -> List[dict]:
    """
    Lists folders under a given base_path (by path).
    Returns list of items with 'id' and 'name'.
    """
    base_item = _resolve_path_item(access_token, drive_id, base_path)
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{base_item['id']}/children"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    _raise_for_graph(r)
    items = r.json().get("value", [])
    # Keep folders only
    return [it for it in items if "folder" in it]


def list_files(access_token: str, drive_id: str, folder_item_id: str) -> List[dict]:
    """
    Lists files under a folder item id.
    """
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{folder_item_id}/children"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    _raise_for_graph(r)
    items = r.json().get("value", [])
    # Keep files only
    return [it for it in items if "file" in it]


def download_file_bytes(access_token: str, drive_id: str, item_id: str) -> bytes:
    """
    Download file content as bytes.
    Graph: GET /drives/{drive-id}/items/{item-id}/content
    """
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{item_id}/content"
    r = requests.get(url, headers=_headers(access_token), timeout=60)
    _raise_for_graph(r)
    return r.content


def upload_file_to_folder(
    access_token: str,
    drive_id: str,
    folder_item_id: str,
    filename: str,
    content_bytes: bytes,
    content_type: str = "application/octet-stream",
) -> dict:
    """
    Upload a small file to a folder item id.
    Graph: PUT /drives/{drive-id}/items/{folder-id}:/{filename}:/content
    """
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{folder_item_id}:/{filename}:/content"
    headers = {**_headers(access_token), "Content-Type": content_type}
    r = requests.put(url, headers=headers, data=content_bytes, timeout=120)
    _raise_for_graph(r)
    return r.json()


def check_duplicate_ir(
    access_token: str,
    drive_id: str,
    incident_reports_root_path: str,
    year: str,
    city: str,
    full_incident_no: str,
) -> bool:
    """
    Checks if the incident folder already exists under:
      root/year/city/full_incident_no
    Returns True if exists, False otherwise.
    """
    path = f"{incident_reports_root_path}/{year}/{city}/{full_incident_no}".strip("/")
    url = f"{GRAPH_ROOT}/drives/{drive_id}/root:/{path}"
    r = requests.get(url, headers=_headers(access_token), timeout=30)
    if r.status_code == 404:
        return False
    _raise_for_graph(r)
    return True
