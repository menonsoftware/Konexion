import logging
import requests
import json
from models.ai import AIModel
from config import get_ollama_config

# Setup logging
logger = logging.getLogger(__name__)

# Get configuration
ollama_config = get_ollama_config()

def get_ollama_models():
    """
    Fetch available models from Ollama running on a network URL.
    
    Returns:
        List of models compatible with AIModel structure
    """
    try:
        # Ollama API endpoint for listing models
        models_url = f"{ollama_config.url}/api/tags"
        
        logger.debug(f"Fetching Ollama models from: {models_url}")
        response = requests.get(models_url, timeout=ollama_config.timeout)
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"Received {len(data.get('models', []))} models from Ollama API")
        
        all_models = [
            {
                "client_type": "ollama",
                "model_id": model["name"],
                # Ollama doesn't provide context_window in the API response
                # Default to a reasonable value, can be overridden per model
                "context_window": model.get("context_length", 4096),
                "owned_by": "ollama",
            }
            for model in data.get("models", [])
        ]
        
        ollama_models = [AIModel.model_validate(model) for model in all_models]
        logger.info(f"Successfully loaded {len(ollama_models)} Ollama models")
        return {"models": ollama_models}
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error connecting to Ollama at {ollama_config.url}: {e} (Status: {e.response.status_code})")
        return {"models": []}
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error connecting to Ollama at {ollama_config.url}: {e}")
        return {"models": []}
    except Exception as e:
        logger.error(f"Unexpected error fetching Ollama models: {e}", exc_info=True)
        return {"models": []}


def get_ollama_client():
    """
    Get Ollama client configuration for making requests.
    
    Returns:
        dict: Configuration for Ollama requests
    """
    return {
        "base_url": ollama_config.url,
        "generate_url": f"{ollama_config.url}/api/generate",
        "chat_url": f"{ollama_config.url}/api/chat"
    }


def generate_ollama_response(model_name, prompt, stream=False):
    """
    Generate response from Ollama model.
    
    Args:
        model_name (str): Name of the Ollama model
        prompt (str): Input prompt
        stream (bool): Whether to stream the response
    
    Returns:
        Response from Ollama API
    """
    client_config = get_ollama_client()
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "num_predict": ollama_config.max_tokens
        }
    }
    
    try:
        response = requests.post(
            client_config["generate_url"],
            json=payload,
            timeout=ollama_config.timeout
        )
        response.raise_for_status()
        logger.debug(f"Successfully generated response from Ollama model: {model_name}")
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating response from Ollama: {e}")
        return {"error": str(e)}


def stream_ollama_chat(model_name, messages, max_tokens=None):
    """
    Stream chat response from Ollama model.
    
    Args:
        model_name (str): Name of the Ollama model
        messages (list): List of message objects with role and content
        max_tokens (int, optional): Maximum number of tokens to generate
    
    Yields:
        Generator of response chunks
    """
    client_config = get_ollama_client()
    
    # Use provided max_tokens or fall back to config default
    tokens_limit = max_tokens if max_tokens is not None else ollama_config.max_tokens
    
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": True,
        "options": {
            "num_predict": tokens_limit
        }
    }
    
    try:
        logger.debug(f"Starting chat stream with Ollama model: {model_name}")
        response = requests.post(
            client_config["chat_url"],
            json=payload,
            timeout=ollama_config.timeout,
            stream=True
        )
        response.raise_for_status()
        
        chunk_count = 0
        for line in response.iter_lines():
            if line:
                try:
                    chunk_data = line.decode('utf-8')
                    chunk_json = json.loads(chunk_data)
                    
                    if 'message' in chunk_json and 'content' in chunk_json['message']:
                        content = chunk_json['message']['content']
                        if content:
                            chunk_count += 1
                            yield content
                    
                    # Check if this is the final chunk
                    if chunk_json.get('done', False):
                        logger.debug(f"Completed Ollama chat stream with {chunk_count} chunks")
                        break
                        
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Error parsing Ollama response chunk: {e}")
                    continue
                    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error streaming from Ollama: {e}")
        yield f"Error: {str(e)}"
