# src\db\bot_db\helpers.py

# Standard library imports
import json
from typing import Optional

def serialize_json(data) -> str:
    """Serialize Python objects to JSON string for database storage."""
    return json.dumps(data) if data is not None else None

def deserialize_json(data: Optional[str], default=None):
    """Deserialize JSON string from database to Python objects."""
    if data is None:
        return default
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default
