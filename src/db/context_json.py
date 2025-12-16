# src\db\context_json.py
# Context JSON Handler - Manages context.json file
# Stores channel and role mappings for the application.

PRINT_PREFIX = "CONTEXT JSON"

# Standard library imports
import json
import os

# Local imports
from . import DB_DIR

# Determine project root and context.json path
CONTEXT_JSON_PATH = os.path.join(DB_DIR, "context.json")

# Create context.json if it doesn't exist
if not os.path.exists(CONTEXT_JSON_PATH):
    with open(CONTEXT_JSON_PATH, 'w') as f:
        json.dump(
            {
                "categories": {},
                "channels": {},
                "roles": {}, 
                "dev": {} # For developer-specific context data not specified in detail (timestamps, locks, etc.)
            }, f)


# Load context data
with open(CONTEXT_JSON_PATH, 'r') as f:
    context_data = json.load(f)


# Function to save context data back to context.json
def _save_context_json() -> None:
    """Save the context_data dictionary to context.json file."""
    with open(CONTEXT_JSON_PATH, 'w') as f:
        json.dump(context_data, f, indent=2)
    print(f"[DEBUG] [{PRINT_PREFIX}] context.json saved")


# Functions to add or update entries in contextdata
def add_category_entry(key: str, value: any) -> None:
    """Add or update a category entry in context_data."""
    context_data["categories"][key] = value
    _save_context_json()

def add_channel_entry(key: str, value: any) -> None:
    """Add or update a channel entry in context_data."""
    context_data["channels"][key] = value
    _save_context_json()

def add_role_entry(key: str, value: any) -> None:
    """Add or update a role entry in context_data."""
    context_data["roles"][key] = value
    _save_context_json()

def add_dev_entry(key: str, value: any) -> None:
    """Add or update a developer-specific entry in context_data."""
    context_data["dev"][key] = value
    _save_context_json()


# Functions to retrieve entries from contextdata
def get_category_entry(key: str, default: any = None) -> any:
    """Retrieve a category entry from context_data."""
    return context_data["categories"].get(key, default)

def get_channel_entry(key: str, default: any = None) -> any:
    """Retrieve a channel entry from context_data."""
    return context_data["channels"].get(key, default)

def get_role_entry(key: str, default: any = None) -> any:
    """Retrieve a role entry from context_data."""
    return context_data["roles"].get(key, default)

def get_dev_entry(key: str, default: any = None) -> any:
    """Retrieve a developer-specific entry from context_data."""
    return context_data["dev"].get(key, default)


# Function to delete entries from contextdata
def delete_category_entry(key: str) -> None:
    """Delete a category entry from context_data."""
    if key in context_data["categories"]:
        del context_data["categories"][key]
        _save_context_json()

def delete_channel_entry(key: str) -> None:
    """Delete a channel entry from context_data."""
    if key in context_data["channels"]:
        del context_data["channels"][key]
        _save_context_json()

def delete_role_entry(key: str) -> None:
    """Delete a role entry from context_data."""
    if key in context_data["roles"]:
        del context_data["roles"][key]
        _save_context_json()

def delete_dev_entry(key: str) -> None:
    """Delete a developer-specific entry from context_data."""
    if key in context_data["dev"]:
        del context_data["dev"][key]
        _save_context_json()