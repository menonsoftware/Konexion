from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Any, Optional
from starlette.websockets import WebSocketDisconnect
from ai_models.groq import stream_groq_chat
from ai_models.ollama import stream_ollama_chat_websocket
from config import get_security_config, get_server_config, get_logging_config
from vision import process_vision_request, prepare_vision_message
from model_registry import model_registry

# Setup logging
logging_config = get_logging_config()
log_level = getattr(logging, logging_config.level.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format=logging_config.format,
    filename=logging_config.file if logging_config.file else None
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    This replaces the deprecated @app.on_event decorators with the modern
    lifespan context manager pattern.
    """
    # Startup
    logger.info("Starting Konexion AI Backend")
    logger.info("Pre-loading model registry...")
    try:
        # Pre-load models to cache them
        counts = await model_registry.preload_models()
        logger.info(f"Successfully pre-loaded {counts['total']} models "
                   f"({counts['groq']} Groq, {counts['ollama']} Ollama)")
    except Exception as e:
        logger.warning(f"Failed to pre-load models: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Konexion AI Backend")
    model_registry.refresh_cache()  # Clear cache


app = FastAPI(
    title="Konexion AI Backend",
    description="AI model inference backend with multi-provider support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware using configuration
security_config = get_security_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("FastAPI application initialized with CORS middleware")
logger.info(f"CORS origins: {security_config.cors_origins_list}")




@app.get("/api/models")
async def get_models():
    """API endpoint to get available models for the frontend."""
    try:
        logger.info("Fetching available models from Groq and Ollama")
        all_models = model_registry.get_all_models()
        
        groq_count = len([m for m in all_models if m.client_type == "groq"])
        ollama_count = len([m for m in all_models if m.client_type == "ollama"])
        
        logger.info(f"Successfully fetched {len(all_models)} models "
                   f"({groq_count} from Groq, {ollama_count} from Ollama)")
        
        return {"models": all_models}
    except Exception as e:
        logger.error(f"Error fetching models: {e}", exc_info=True)
        return {"models": [], "error": "Failed to fetch models"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint for frontend connectivity testing."""
    logger.debug("Health check endpoint accessed")
    return {
        "status": "healthy",
        "message": "Konexion backend is running",
        "cors_enabled": True
    }


def validate_chat_input(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate incoming chat WebSocket data.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    user_message = data.get("message")
    selected_model = data.get("model")
    
    if not user_message:
        return False, "Message is required"
    
    if not selected_model:
        return False, "Model selection is required"
    
    return True, None


def normalize_user_message(user_message: Any) -> str:
    """
    Normalize user message to string format.
    
    Args:
        user_message: Message in various formats (string, dict, etc.)
        
    Returns:
        str: Normalized message string
    """
    if isinstance(user_message, dict):
        # If message is an object, try to extract content or convert properly
        message_str = user_message.get("content", str(user_message))
        logger.debug("Converted dict message to string")
    elif isinstance(user_message, str):
        message_str = user_message
    else:
        # For any other type, convert to string safely
        message_str = str(user_message)
        logger.debug(f"Converted {type(user_message)} message to string")
    
    return message_str


def prepare_base_messages() -> List[Dict[str, str]]:
    """Prepare base system message for AI models."""
    return [
        {
            "role": "system", 
            "content": "You are a helpful assistant."
        }
    ]


async def send_error_response(websocket: WebSocket, error_message: str, 
                            finish_reason: str = "error") -> None:
    """Send standardized error response via WebSocket."""
    try:
        await websocket.send_json({"error": error_message})
        await websocket.send_json({"finish_reason": finish_reason})
    except Exception as e:
        logger.error(f"Failed to send error response: {e}")


async def route_model_request(websocket: WebSocket, selected_model: str, 
                            messages: List[Dict[str, Any]], max_tokens: Optional[int]) -> None:
    """
    Route the request to the appropriate AI provider based on model type.
    
    Args:
        websocket: WebSocket connection
        selected_model: Selected model identifier
        messages: Prepared messages for the AI model
        max_tokens: Maximum tokens for generation
    """
    try:
        if model_registry.is_groq_model(selected_model):
            await stream_groq_chat(websocket, selected_model, messages, max_tokens)
        elif model_registry.is_ollama_model(selected_model):
            await stream_ollama_chat_websocket(websocket, selected_model, messages, max_tokens)
        else:
            # Model not found in either service
            error_msg = f"Model '{selected_model}' not found in available models."
            logger.error(error_msg)
            await send_error_response(websocket, error_msg)
            
    except Exception as e:
        logger.error(f"Error during model request routing: {e}", exc_info=True)
        await send_error_response(websocket, f"Error processing request: {str(e)}")


@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with AI models."""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive and validate data
            data = await websocket.receive_json()
            logger.debug(f"Received WebSocket data: {data}")
            
            # Validate input
            is_valid, error_message = validate_chat_input(data)
            if not is_valid:
                logger.warning(f"Invalid input: {error_message}")
                await send_error_response(websocket, f"Invalid input: {error_message}")
                continue
            
            # Extract and normalize data
            user_message_str = normalize_user_message(data["message"])
            selected_model = data["model"]
            images = data.get("images", [])
            max_tokens = data.get("max_tokens")
            
            logger.debug(f"Processing request - Model: {selected_model}, "
                        f"Message length: {len(user_message_str)}, Images: {len(images)}")
            
            # Process vision request
            vision_result = process_vision_request(selected_model, user_message_str, images)
            
            if not vision_result["success"]:
                logger.warning(f"Vision processing failed: {vision_result['error']}")
                await send_error_response(websocket, vision_result["error"])
                continue
            
            # Prepare messages
            messages = prepare_base_messages()
            
            if vision_result["data"]["has_images"]:
                # Use Groq format for all models - ollama.py will convert if needed
                vision_message = prepare_vision_message("user", user_message_str, images, "groq")
                messages.append(vision_message)
                logger.info(f"Processing {vision_result['image_count']} images for model: {selected_model}")
            else:
                messages.append({
                    "role": "user", 
                    "content": user_message_str
                })
            
            logger.debug(f"Prepared {len(messages)} messages for AI processing")
            logger.info(f"Processing chat request with model: {selected_model}")
            
            # Route to appropriate AI provider
            await route_model_request(websocket, selected_model, messages, max_tokens)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close()
        except RuntimeError:
            logger.warning("Failed to close WebSocket connection (may already be closed)")


@app.post("/api/models/refresh")
async def refresh_models():
    """Refresh the model cache by clearing cached data."""
    try:
        logger.info("Refreshing model cache")
        model_registry.refresh_cache()
        # Pre-load the models using the new method
        counts = await model_registry.preload_models()
        
        logger.info(f"Model cache refreshed - {counts['total']} models loaded "
                   f"({counts['groq']} Groq, {counts['ollama']} Ollama)")
        
        return {
            "status": "success",
            "message": "Model cache refreshed",
            "total_models": counts['total'],
            "groq_models": counts['groq'],
            "ollama_models": counts['ollama']
        }
    except Exception as e:
        logger.error(f"Error refreshing model cache: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to refresh model cache: {str(e)}"
        }


if __name__ == "__main__":
    server_config = get_server_config()
    logger.info(f"Starting server on {server_config.host}:{server_config.port} with reload={server_config.reload} and workers={server_config.workers}")
    logger.info(f"Debug mode: {server_config.debug}, Reload: {server_config.reload}")
    
    uvicorn.run(
        "main:app", 
        host=server_config.host, 
        port=server_config.port, 
        reload=server_config.reload, 
        workers=server_config.workers
    )
