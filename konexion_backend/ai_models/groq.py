import logging
from groq import Groq
import requests
from models.ai import AIModel
from config import get_groq_config

# Setup logging
logger = logging.getLogger(__name__)

# Get configuration
groq_config = get_groq_config()

# Initialize Groq client with configuration

def get_groq_client() -> Groq:
    """Get Groq client if API key is configured, else raise an exception."""
    if groq_config.api_key:
        groq_client = Groq(api_key=groq_config.api_key)
        logger.info("Groq client initialized successfully")
        return groq_client
    logger.warning("Groq API key not configured, client not available")
    raise Exception("Groq API key not configured, cannot initialize Groq client")
    

def get_groq_models():
    """Fetch available models from Groq API with proper error handling and logging."""
    if not groq_config.api_key:
        logger.warning("Groq API key not configured, returning empty model list")
        return {"models": []}
    
    headers = {
        "Authorization": f"Bearer {groq_config.api_key}",
        "Content-Type": "application/json",
    }
    
    try:
        logger.debug(f"Fetching Groq models from: {groq_config.url}")
        response = requests.get(groq_config.url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"Received {len(data.get('data', []))} models from Groq API")
        
        all_models = [
            {
                "client_type": "groq",
                "model_id": model["id"],
                "context_window": model["context_window"],
                "owned_by": model["owned_by"],
            }
            for model in data["data"]
            if "tts" not in model["id"].lower() and "whisper" not in model["id"].lower() and "guard" not in model["id"].lower()
        ]
        
        groq_models = [AIModel.model_validate(model) for model in all_models]
        logger.info(f"Successfully loaded {len(groq_models)} Groq models")
        return {"models": groq_models}
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching Groq models: {e} (Status: {e.response.status_code})")
        return {"models": []}
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching Groq models: {e}")
        return {"models": []}
    except Exception as e:
        logger.error(f"Unexpected error fetching Groq models: {e}", exc_info=True)
        return {"models": []}