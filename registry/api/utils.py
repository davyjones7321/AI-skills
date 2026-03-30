from datetime import date, datetime
from typing import Any

def make_json_safe(obj: Any) -> Any:
    """Recursively convert date/datetime objects to ISO strings for JSON serialization."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_safe(item) for item in obj]
    return obj
