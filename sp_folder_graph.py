# sp_folder_graph.py
import re
import requests
from urllib.parse import urlparse


GRAPH_ROOT = "https://graph.microsoft.com/v1.0"


def _headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def _get(token: str, url: str, **kwargs):
    r = requests.get(url, headers=_headers(token), **kwargs)
    r.raise_for_status()
    return r.json()


def _get_bytes(token: str, url: str, **kwargs) -> bytes:
    r = requests.get(url, headers=_headers(token), **kwargs)
    r.raise_for_status()
    return r.content


def _put_bytes(token: str, url: str, content: bytes, content_type: str):
    headers = _headers(token)
    headers["Content-Type"] = content_type
    r = requests.put(url, headers=headers, data=content)
    r.raise_for_status()
    return r.json() if r.content else {}


def resolve_site_id(token: str, sharepoint_site_url: str) -> str:
    """
    sharepoint_site_url example:
    https://philsaorg.sharepoint.com/sites/YourSiteName
    """
    u = urlparse(sharepoint_site_url)
    host = u.netloc
    path = u.path.strip("/")

    if not host or not path:
        raise ValueError("Invalid sharepoint_site_url. Example: https://TENANT.sharepoint.com/sites/SITE")

    # Graph sites lookup:
    # GET /sites/{hostname}:/sites/{site-path}
    # If your URL already includes /sites/XYZ, keep it as-is in the path.
    url = f"{GRAPH_ROOT}/sites/{host}:/{path}"
    j = _get(token, url)
    site_id = j.get("id")
    if not site_id:
        raise RuntimeError("Could not resolve SharePoint site id")
    return site_id


def get_default_drive_id(token: str, site_id: str) -> str:
    # GET /sites/{site-id}/drive
    j = _get(token, f"{GRAPH_ROOT}/sites/{site_id}/drive")
    drive_id = j.get("id")
    if not drive_id:
        raise RuntimeError("Could not resolve default drive id")
    return drive_id


def list_children_by_path(token: str, drive_id: str, folder_path: str):
    # /drives/{drive-id}/root:/{path}:/children
    folder_path = folder_path.strip("/")
    url = f"{GRAPH_ROOT}/drives/{drive_id}/root:/{folder_path}:/children"
    j = _get(token, url)
    return j.get("value", [])


def list_incident_folders(token: str, drive_id: str, base_path: str):
    kids = list_children_by_path(token, drive_id, base_path)
    folders = [x for x in kids if x.get("folder") is not None]
    # Sort by name
    folders.sort(key=lambda x: x.get("name", "").lower())
    return [{"id": f["id"], "name": f["name"]} for f in folders]


def list_files(token: str, drive_id: str, folder_item_id: str):
    # /drives/{drive-id}/items/{item-id}/children
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{folder_item_id}/children"
    j = _get(token, url)
    files = [x for x in j.get("value", []) if x.get("file") is not None]
    files.sort(key=lambda x: x.get("name", "").lower())
    return [{"id": f["id"], "name": f["name"]} for f in files]


def download_file_bytes(token: str, drive_id: str, item_id: str) -> bytes:
    # /drives/{drive-id}/items/{item-id}/content
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{item_id}/content"
    return _get_bytes(token, url)


def upload_file_to_folder(token: str, drive_id: str, folder_item_id: str, filename: str, content_bytes: bytes, content_type: str):
    # PUT /drives/{drive-id}/items/{parent-id}:/{filename}:/content
    safe_name = filename.replace("\\", "/").split("/")[-1]
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{folder_item_id}:/{safe_name}:/content"
    return _put_bytes(token, url, content_bytes, content_type)


def _ensure_folder(token: str, drive_id: str, parent_item_id: str, folder_name: str):
    # Create folder under parent
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{parent_item_id}/children"
    payload = {
        "name": folder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "fail",
    }
    r = requests.post(url, headers={**_headers(token), "Content-Type": "application/json"}, json=payload)
    if r.status_code in (200, 201):
        return r.json()
    # if already exists, we’ll fall back to listing
    if r.status_code == 409:
        return None
    r.raise_for_status()


def _find_child_folder(token: str, drive_id: str, parent_item_id: str, folder_name: str):
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{parent_item_id}/children"
    j = _get(token, url)
    for item in j.get("value", []):
        if item.get("name") == folder_name and item.get("folder") is not None:
            return item
    return None


def ensure_path(token: str, drive_id: str, root_path: str, parts: list[str]):
    """
    Ensure folder path exists under drive root:
    root_path / parts[0] / parts[1] / ...
    Returns final folder item.
    """
    # Start at root_path
    root_path = root_path.strip("/")
    # Get the item id for root_path
    root_item = _get(token, f"{GRAPH_ROOT}/drives/{drive_id}/root:/{root_path}")
    parent_id = root_item["id"]

    for p in parts:
        p = (p or "").strip()
        if not p:
            continue

        existing = _find_child_folder(token, drive_id, parent_id, p)
        if existing:
            parent_id = existing["id"]
            continue

        created = _ensure_folder(token, drive_id, parent_id, p)
        if created is None:
            # race or already exists
            existing = _find_child_folder(token, drive_id, parent_id, p)
            if not existing:
                raise RuntimeError(f"Unable to create/find folder: {p}")
            parent_id = existing["id"]
        else:
            parent_id = created["id"]

    return _get(token, f"{GRAPH_ROOT}/drives/{drive_id}/items/{parent_id}")


def check_duplicate_ir(token: str, drive_id: str, root_path: str, year: str, city: str, incident_folder_name: str) -> bool:
    """
    Returns True if folder already exists under:
    root_path/year/city/incident_folder_name
    """
    path = f"{root_path}/{year}/{city}".strip("/")
    kids = list_children_by_path(token, drive_id, path)
    for x in kids:
        if x.get("folder") is not None and x.get("name") == incident_folder_name:
            return True
    return False
