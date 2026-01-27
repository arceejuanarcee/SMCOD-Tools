# sp_folder_graph.py
import requests
import ms_graph

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"


def _headers():
    token = ms_graph.get_access_token()
    if not token:
        raise RuntimeError("Not authenticated with Microsoft Graph.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def get_site(site_hostname: str, site_path: str):
    """
    Example:
      site_hostname = "philsa.sharepoint.com"
      site_path     = "/sites/SMCOD"
    """
    url = f"{GRAPH_ROOT}/sites/{site_hostname}:{site_path}"
    r = requests.get(url, headers=_headers())
    r.raise_for_status()
    return r.json()


def list_drive_root(site_id: str):
    """
    Lists root items of the default document library.
    """
    url = f"{GRAPH_ROOT}/sites/{site_id}/drive/root/children"
    r = requests.get(url, headers=_headers())
    r.raise_for_status()
    return r.json().get("value", [])


def list_folder_children(drive_id: str, folder_id: str):
    """
    List items inside a specific folder.
    """
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{folder_id}/children"
    r = requests.get(url, headers=_headers())
    r.raise_for_status()
    return r.json().get("value", [])


def create_folder(drive_id: str, parent_id: str, folder_name: str):
    """
    Create a folder under a parent folder.
    """
    url = f"{GRAPH_ROOT}/drives/{drive_id}/items/{parent_id}/children"
    payload = {
        "name": folder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename",
    }
    r = requests.post(url, headers=_headers(), json=payload)
    r.raise_for_status()
    return r.json()
