# src\db\__init__.py

import os

# Global database directories
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_DIR = os.path.join(PROJECT_ROOT, "data")
SNAPSHOTS_DIR = os.path.join(DB_DIR, 'backups')
REPLICAS_DIR = os.path.join(DB_DIR, 'replicas')

# Global databases dictionary that stores the filename and its module
DATABASES = {} # Gets populated when the dbs are initializeds

# Create necessary directories if they don't exist
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
os.makedirs(REPLICAS_DIR, exist_ok=True)

# Exported modules
from . import connections
from . import context_json
from . import backups
from . import bot_db


