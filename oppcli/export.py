"""
oppcli/export.py — Export filtered opportunities to CSV or JSON.
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

def _clean(opp: Dict[str, Any]) -> Dict[str, Any]:
    """Strip non-serialisable fields before export."""
    o = dict(opp)
    o.pop("deadline_dt", None)
    o["stipend"] = "Yes" if o["stipend"] else "No"
    if isinstance(o["tags"], list):
        o["tags"] = ", ".join(o["tags"])
    o["expired"] = "Yes" if o.get("expired") else "No"
    return o

def export_csv(opps: List[Dict[str, Any]], path: Optional[str] = None) -> str:
    if path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"oppcli_export_{ts}.csv"

    path = os.path.expanduser(path)
    fields = ["id", "title", "org", "category", "region", "deadline",
              "days_left", "stipend", "expired", "tags", "link", "description"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for o in opps:
            writer.writerow(_clean(o))

    return path

def export_json(opps: List[Dict[str, Any]], path: Optional[str] = None) -> str:
    if path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"oppcli_export_{ts}.json"

    path = os.path.expanduser(path)
    cleaned = [_clean(o) for o in opps]

    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "count": len(cleaned), 
            "exported_at": datetime.utcnow().isoformat(), 
            "opportunities": cleaned
        }, f, indent=2)

    return path
