# src\db\bot_db\__init__.py

from ..connections import connect_db as connect_bot_db # Import connection function from connections module for easy access

# Export schema module
from . import schema