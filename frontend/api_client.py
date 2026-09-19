import os
import requests
from typing import List, Dict, Any, Optional

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

def check_health() -> Dict[str, Any]:
    """Check backend API health status."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if response.status_code == 200:
            return {"healthy": True, "data": response.json()}
        return {"healthy": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"healthy": False, "error": str(e)}

def get_clients(active_only: bool = False) -> List[Dict[str, Any]]:
    """Fetch clients list from FastAPI backend."""
    params = {"active_only": "true" if active_only else "false"}
    response = requests.get(f"{BACKEND_URL}/clients", params=params, timeout=5)
    response.raise_for_status()
    return response.json()

def create_client(name: str, phone: Optional[str] = None, email: Optional[str] = None, active: bool = True) -> Dict[str, Any]:
    """Create a new client via FastAPI backend."""
    payload = {
        "name": name,
        "phone": phone if phone else None,
        "email": email if email else None,
        "active": active
    }
    response = requests.post(f"{BACKEND_URL}/clients", json=payload, timeout=5)
    if response.status_code != 201:
        try:
            error_json = response.json()
            detail = error_json.get("detail", "Failed to create client")
            if isinstance(detail, list):
                messages = []
                for err in detail:
                    msg = err.get("msg", "")
                    if "Value error, " in msg:
                        msg = msg.replace("Value error, ", "")
                    field = err.get("loc", [])[-1] if err.get("loc") else "Field"
                    messages.append(f"{str(field).capitalize()}: {msg}")
                raise ValueError("; ".join(messages))
            elif isinstance(detail, str):
                raise ValueError(detail)
            else:
                raise ValueError(str(detail))
        except Exception as parse_err:
            if isinstance(parse_err, ValueError):
                raise parse_err
            raise ValueError(f"HTTP {response.status_code}: {response.text}")
    return response.json()
