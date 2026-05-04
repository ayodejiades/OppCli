"""
oppcli/data_manager.py — Opportunity data store and filtering logic.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

def calculate_fingerprint(opp: Dict[str, Any]) -> str:
    """Creates a unique SHA-256 hash based on the core content of an opportunity."""
    # We hash the key fields that define the opportunity's unique identity
    # and content. If any of these change, the fingerprint changes.
    core_str = f"{opp.get('title','')}|{opp.get('org','')}|{opp.get('link','')}|{opp.get('description','')}"
    return hashlib.sha256(core_str.encode("utf-8")).hexdigest()

CATEGORIES = ["Fellowship", "Scholarship", "Hackathon", "Grant", "Internship", "Conference"]
REGIONS = ["Pan-Africa", "West Africa", "East Africa", "Southern Africa", "North Africa", "Global"]

def _get_data_path() -> str:
    """Returns the path to the internal opportunities.json file."""
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "data", "opportunities.json")

def load_raw_opportunities() -> List[Dict[str, Any]]:
    path = _get_data_path()
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _enrich(opp: Dict[str, Any]) -> Dict[str, Any]:
    """Add computed deadline fields to an opportunity dict."""
    o = dict(opp)
    try:
        dt = datetime.strptime(o["deadline"], "%Y-%m-%d")
        now = datetime.utcnow()
        days_left = (dt - now).days
        o["deadline_dt"] = dt
        o["days_left"] = days_left
        o["expired"] = days_left < 0
    except (ValueError, TypeError):
        o["deadline_dt"] = None
        o["days_left"] = None
        o["expired"] = False
    return o

def get_all() -> List[Dict[str, Any]]:
    raw = load_raw_opportunities()
    return [_enrich(o) for o in raw]

def get_filtered(
    category: Optional[str] = None,
    region: Optional[str] = None,
    stipend_only: bool = False,
    hide_expired: bool = True,
    query: Optional[str] = None,
) -> List[Dict[str, Any]]:
    results = get_all()

    if hide_expired:
        results = [o for o in results if not o["expired"]]
    if category:
        results = [o for o in results if o["category"].lower() == category.lower()]
    if region:
        results = [o for o in results if region.lower() in o["region"].lower()]
    if stipend_only:
        results = [o for o in results if o["stipend"]]
    if query:
        q = query.lower()
        results = [
            o for o in results
            if q in o["title"].lower()
            or q in o["description"].lower()
            or q in o["org"].lower()
            or any(q in tag for tag in o["tags"])
        ]

    results.sort(key=lambda o: o["days_left"] if o["days_left"] is not None else 9999)
    return results

def get_by_id(opp_id: int) -> Optional[Dict[str, Any]]:
    for o in get_all():
        if o["id"] == opp_id:
            return o
    return None

def save_all(opportunities: List[Dict[str, Any]]):
    """Persists a list of opportunities to the JSON data store."""
    path = _get_data_path()
    to_save = []
    for o in opportunities:
        clean_o = dict(o)
        clean_o.pop("deadline_dt", None)
        clean_o.pop("days_left", None)
        clean_o.pop("expired", None)
        # Ensure fingerprint is present
        if "fingerprint" not in clean_o:
            clean_o["fingerprint"] = calculate_fingerprint(clean_o)
        to_save.append(clean_o)
        
    with open(path, "w") as f:
        json.dump(to_save, f, indent=2)
