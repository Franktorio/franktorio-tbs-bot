# src\commands\permissions.py
# Helper functions for permission checks

# Third-party imports
import discord

# Local imports
from src.db.context_json import get_developers

def is_developer(user_id: int) -> bool:
    """Check if the user is a developer."""
    return user_id in get_developers()