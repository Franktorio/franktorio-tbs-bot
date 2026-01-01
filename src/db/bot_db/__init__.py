# src\db\bot_db\__init__.py

from ..connections import connect_db as connect_bot_db # Import connection function from connections module for easy access

from . import active_vcs
from . import create_vc_templates
from . import global_blacklists
from . import leaders
from . import minor_wins
from . import schema
from . import under_review
from . import users
from . import wins