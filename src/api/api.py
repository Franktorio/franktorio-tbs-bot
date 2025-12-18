# src\api\api.py
# API module for external controllers/webapps to interact with the bot.

PRINT_PREFIX = "LOCAL API"

# Third-party imports
import fastapi
import uvicorn

# Local imports
from config.env_vars import API_HOST, API_PORT

app = fastapi.FastAPI()

def run_api():
    """Function to run the FastAPI application, must be run in a separate thread."""
    print(f"[INFO] [{PRINT_PREFIX}] Starting API server at http://{API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)