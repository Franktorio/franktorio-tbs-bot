# config\leader_config.py
# Leader configuration loading

PRINT_PREFIX = "LEADER CONFIG"

# Standard library imports
import json
import os

# Third-party imports
from discord import app_commands

LEADER_CONFIG_PATH: str = os.path.join("config", "leader_config.json")

with open(LEADER_CONFIG_PATH, "r") as file:
    leader_config: dict = json.load(file)

LEADER_TIERS: list[str] = [tier.lower() for tier in leader_config.get("leader_tiers", {}).keys()]
LEADER_TIERS_CHOICE: list[app_commands.Choice[str]] = [app_commands.Choice(name=tier, value=tier) for tier in LEADER_TIERS]


def get_leader_tier_config(tier: str) -> dict:
    """Get the configuration for a specific leader tier.
    
    Returns:
        dict: Tier configuration with structure:
        {
            "wins_to_reach": int | None,
            "hdt_days": int | None,
            "next_tier": str | None,
            "role_id": int
        }
    """
    return leader_config.get("leader_tiers", {}).get(tier.lower(), {})

def get_leader_role_id(tier: str) -> int | None:
    """Get the Discord role ID for a specific leader tier."""
    tier_config = get_leader_tier_config(tier)
    return tier_config.get("role_id", None)

def get_all_leader_role_ids() -> dict[str, int]:
    """Get a mapping of leader tiers to their Discord role IDs.
    
    Returns:
        dict[str, int]: Dictionary with structure:
        {
            "trial": 1450547888613490885,
            "graduate": 1450547888613490886,
            "experienced": 1453930184708460586,
            ...
        }
    """
    role_ids = {}
    for tier in LEADER_TIERS:
        role_id = get_leader_role_id(tier)
        if role_id is not None:
            role_ids[tier] = role_id
    return role_ids

def get_general_leader_role_id() -> int | None:
    """Get the general leader role ID."""
    return leader_config.get("general_leader_role_id", None)
