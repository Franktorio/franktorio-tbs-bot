# config\env_vars.py
# Load environment variables from .env file

PRINT_PREFIX = "ENV VARS"

import os
from dotenv import load_dotenv
from typing import Optional, Sequence

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

def _get_env_int(key: str, default: Optional[int | str] = None) -> int:
    """Helper function to get integer from environment with error handling"""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Required environment variable {key} not found")
    try:
        print(f"[INFO] [{PRINT_PREFIX}] Loaded integer env var {key}={value}")
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable {key} must be a valid integer, got: {value}")

def _get_env_int_list(key: str, default: Optional[Sequence[int] | str] = None) -> list[int]:
    """Helper function to get comma-separated integers from environment"""
    value = os.getenv(key)
    if value is None:
        if default is None:
            raise ValueError(f"Required environment variable {key} not found")
        if isinstance(default, (list, tuple)):
            print(f"[INFO] [{PRINT_PREFIX}] Using default integer list for env var {key}={default}")
            return [int(x) for x in default]
        value = str(default)
    try:
        print(f"[INFO] [{PRINT_PREFIX}] Loaded integer list env var {key}={value}")
        return [int(x.strip()) for x in value.split(',') if x.strip()]
    except ValueError:
        raise ValueError(f"Environment variable {key} must be comma-separated integers, got: {value}")

def _get_env_str_list(key: str, default: Optional[Sequence[str] | str] = None) -> list[str]:
    """Helper function to get comma-separated strings from environment"""
    value = os.getenv(key)
    if value is None:
        if default is None:
            raise ValueError(f"Required environment variable {key} not found")
        if isinstance(default, (list, tuple)):
            print(f"[INFO] [{PRINT_PREFIX}] Using default string list for env var {key}={default}")
            return [str(x) for x in default]
        value = str(default)
    print(f"[INFO] [{PRINT_PREFIX}] Loaded string list env var {key}={value}")
    return [x.strip() for x in value.split(',') if x.strip()]
    
def _get_env_bool(key: str, default: Optional[bool | str] = None) -> bool:
    """Helper function to get boolean from environment"""
    value = os.getenv(key)
    if value is None:
        if default is None:
            raise ValueError(f"Required environment variable {key} not found")
        value = str(default)
        print(f"[INFO] [{PRINT_PREFIX}] Using default boolean env var {key}={value}")
    else:
        print(f"[INFO] [{PRINT_PREFIX}] Loaded boolean env var {key}={value}")
    return value.lower() in ('true', '1', 'yes')
    
# SECRET KEYS AND TOKENS
BOT_TOKEN: str = os.getenv("BOT_TOKEN")
WORKER_TOKENS: list[str] = _get_env_str_list("WORKER_TOKENS", [])
LOCAL_API_KEY: str = os.getenv("API_KEY", "default_api_key") # Default API key if not set
API_PORT: int = _get_env_int("API_PORT", 8000)
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")

# CONFIGURATION SETTINGS
HOME_GUILD_ID: int = _get_env_int("HOME_GUILD_ID") # ID of the home guild/server for the bot
ALLOWED_GUILDS: list[int] = _get_env_int_list("ALLOWED_GUILDS", [])

DEBUG_ENABLED: bool = _get_env_bool("DEBUG_ENABLED", "False")

BACKUP_INTERVAL_MINUTES: int = _get_env_int("BACKUP_INTERVAL_MINUTES", 60)
REPLICATION_INTERVAL_MINUTES: int = _get_env_int("REPLICATION_INTERVAL_MINUTES", 5)

BOT_NAME: str = os.getenv("BOT_NAME", "Mr. Franktorio") # Default bot name if not set (CHANGE OR BOT WILL HAVE MY DEFAULT NAME)