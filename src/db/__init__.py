# src\db\__init__.py

import os
from config.env_vars import BACKUPS_ENABLED, REPLICATION_ENABLED

# Global database directories
DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
BACKUPS_DIR = os.path.join(DB_DIR, 'backups')
REPLICAS_DIR = os.path.join(DB_DIR, 'replicas')

# Global databases dictionary that stores the filename and its module
DATABASES = {} # Gets populated when the dbs are initializeds

# Create necessary directories if they don't exist
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)
os.makedirs(REPLICAS_DIR, exist_ok=True)

# Exported modules
from . import connections
from . import context_json
from . import backups
