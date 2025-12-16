# src\api\api.py
# API module for external controllers/webapps to interact with the bot.

# Third-party imports
import fastapi

# Local imports
from config.env_vars import LOCAL_API_KEY

app = fastapi.FastAPI()