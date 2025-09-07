import logging
from groq import Groq
import requests
import asyncio
import time
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


async def stream_groq_chat(websocket, model_name, messages, max_tokens=None):
    """
    Stream chat response from Groq model with WebSocket integration.
    
    Args:
        websocket: WebSocket connection to send chunks
        model_name (str): Name of the Groq model
        messages (list): List of message objects with role and content
        max_tokens (int, optional): Maximum number of tokens to generate
    """
    try:
        logger.info(f"Using Groq client for model: {model_name}")
        
        # Prepare chat completion parameters
        completion_params = {
            "model": str(model_name),
            "messages": messages,
            "stop": None,
            "stream": True,
        }
        
        # Add max_tokens if provided
        if max_tokens is not None:
            completion_params["max_tokens"] = max_tokens
            logger.debug(f"Using custom max_tokens: {max_tokens}")
        
        stream = get_groq_client().chat.completions.create(**completion_params)
        
        # Batch chunks for better network efficiency
        chunk_buffer = ""
        last_send_time = time.time()
        BATCH_SIZE = 20  # Characters to batch
        BATCH_TIMEOUT = 0.05  # 50ms max delay
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                chunk_buffer += content
                
                current_time = time.time()
                should_send = (
                    len(chunk_buffer) >= BATCH_SIZE or
                    current_time - last_send_time >= BATCH_TIMEOUT or
                    not content.strip()  # Send immediately for whitespace/punctuation
                )
                
                if should_send:
                    logger.debug(f"Sending batched chunk of {len(chunk_buffer)} characters")
                    await websocket.send_json({"chunk": chunk_buffer})
                    chunk_buffer = ""
                    last_send_time = current_time
                    await asyncio.sleep(0.001)  # Small delay to prevent overwhelming frontend
        
        # Send any remaining content
        if chunk_buffer:
            logger.debug(f"Sending final chunk of {len(chunk_buffer)} characters")
            await websocket.send_json({"chunk": chunk_buffer})
        
        await websocket.send_json({"finish_reason": "completed"})
        logger.info(f"Completed Groq chat response for model: {model_name}")
        
    except Exception as e:
        logger.error(f"Error streaming from Groq: {e}", exc_info=True)
        await websocket.send_json({"error": f"Error: {str(e)}"})
        await websocket.send_json({"finish_reason": "error"})