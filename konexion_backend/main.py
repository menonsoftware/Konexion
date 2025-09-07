from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn
import re
import asyncio
import time
import logging
from starlette.websockets import WebSocketDisconnect
from ai_models.groq import get_groq_client, get_groq_models
from ai_models.ollama import get_ollama_models, stream_ollama_chat
from config import get_security_config, get_server_config, get_logging_config, get_vision_config

# Setup logging
logging_config = get_logging_config()
log_level = getattr(logging, logging_config.level.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format=logging_config.format,
    filename=logging_config.file if logging_config.file else None
)
logger = logging.getLogger(__name__)

app = FastAPI()

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
    """API endpoint to get available models for the frontend"""
    try:
        logger.info("Fetching available models from Groq and Ollama")
        # Fetch models from both Groq and Ollama
        groq_models = get_groq_models()
        ollama_models = get_ollama_models()
        total_models = len(groq_models["models"]) + len(ollama_models["models"])
        logger.info(f"Successfully fetched {total_models} models ({len(groq_models['models'])} from Groq, {len(ollama_models['models'])} from Ollama)")
        return {
            "models": groq_models["models"] + ollama_models["models"]
        }
    except Exception as e:
        logger.error(f"Error fetching models: {e}", exc_info=True)
        return {"models": []}


@app.get("/api/health")
async def health_check():
    """Health check endpoint for frontend connectivity testing"""
    logger.debug("Health check endpoint accessed")
    return {
        "status": "healthy",
        "message": "WebKonexion backend is running",
        "cors_enabled": True
    }


@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    # use websockets for chat functionality
    await websocket.accept()
    logger.info("WebSocket connection established")
    try:
        while True:
            data = await websocket.receive_json()
            logger.debug(f"Received WebSocket data: {data}")
            logger.debug(f"Message type: {type(data.get('message'))}, Message: {data.get('message')}")
            user_message = data.get("message")
            selected_model = data.get("model")
            images = data.get("images", [])
            max_tokens = data.get("max_tokens")  # Get max_tokens from frontend

            if not user_message or not selected_model:
                logger.warning("Received incomplete data: missing message or model")
                await websocket.send_json(
                    {"error": "Please enter a message and select a model."}
                )
                continue

            # Ensure user_message is a string and handle potential objects
            if isinstance(user_message, dict):
                # If message is an object, try to extract content or convert properly
                user_message_str = user_message.get("content", str(user_message))
                logger.debug("Converted dict message to string")
            elif isinstance(user_message, str):
                user_message_str = user_message
            else:
                # For any other type, convert to string safely
                user_message_str = str(user_message)
                logger.debug(f"Converted {type(user_message)} message to string")

            # Prepare messages for both Groq and Ollama
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant."
                }
            ]
            
            # Check if the selected model supports vision (using configuration)
            vision_config = get_vision_config()
            supports_vision = vision_config.supports_vision(selected_model)
            
            # Handle message with images based on model capabilities
            if images and supports_vision:
                logger.info(f"Processing {len(images)} images for vision-enabled model: {selected_model}")
                
                # Prepare user message content for vision models
                user_content = []
                
                # Add text if present
                if user_message_str.strip():
                    user_content.append({
                        "type": "text",
                        "text": user_message_str
                    })
                else:
                    user_content.append({
                        "type": "text",
                        "text": "What's in this image?"
                    })
                
                # Add images using Groq vision schema
                for image in images:
                    if image.get("data"):
                        # Extract base64 data from data URL format: data:image/jpeg;base64,base64_string
                        if "," in image["data"]:
                            base64_data = image["data"].split(",")[1]
                            image_type = image.get("type", "image/jpeg")
                            
                            user_content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{image_type};base64,{base64_data}"
                                }
                            })
                            logger.debug(f"Added image to vision content: {image.get('name', 'Unknown')}")
                
                messages.append({
                    "role": "user",
                    "content": user_content  # type: ignore
                })
                
            elif images and not supports_vision:
                logger.info(f"Model {selected_model} does not support vision. Converting {len(images)} images to text descriptions.")
                
                # Fallback to text descriptions for non-vision models
                final_message = user_message_str
                image_descriptions = []
                for i, image in enumerate(images, 1):
                    image_descriptions.append(f"[Image {i}: {image.get('name', 'Unknown')} ({image.get('type', 'Unknown type')})]")
                
                if final_message.strip():
                    final_message = f"{final_message}\n\nAttached images: {', '.join(image_descriptions)}"
                else:
                    final_message = f"Please analyze these images: {', '.join(image_descriptions)}"
                
                messages.append({
                    "role": "user", 
                    "content": final_message
                })
                
            else:
                # No images, simple text message
                messages.append({
                    "role": "user", 
                    "content": user_message_str
                })
            
            logger.debug(f"Prepared messages for AI: {messages}")
            logger.info(f"Processing chat request with model: {selected_model}")

            try:
                # Get available models to determine the client type
                groq_models_data = get_groq_models()
                ollama_models_data = get_ollama_models()
                
                # Check if the model is in Groq models
                is_groq_model = any(model.model_id == selected_model for model in groq_models_data.get("models", []))
                is_ollama_model = any(model.model_id == selected_model for model in ollama_models_data.get("models", []))
                
                if is_groq_model:
                    logger.info(f"Using Groq client for model: {selected_model}")
                    # Use Groq streaming with optimized batching
                    # Prepare chat completion parameters
                    completion_params = {
                        "model": str(selected_model),
                        "messages": messages,  # type: ignore
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
                    logger.info(f"Completed Groq chat response for model: {selected_model}")
                    
                elif is_ollama_model:
                    # Use Ollama streaming with optimized batching
                    logger.info(f"Using Ollama client for model: {selected_model}")
                    
                    chunk_buffer = ""
                    last_send_time = time.time()
                    BATCH_SIZE = 20  # Characters to batch
                    BATCH_TIMEOUT = 0.05  # 50ms max delay
                    
                    for chunk in stream_ollama_chat(selected_model, messages, max_tokens):
                        if chunk:  # Only process non-empty chunks
                            chunk_buffer += chunk
                            
                            current_time = time.time()
                            should_send = (
                                len(chunk_buffer) >= BATCH_SIZE or
                                current_time - last_send_time >= BATCH_TIMEOUT or
                                not chunk.strip()  # Send immediately for whitespace/punctuation
                            )
                            
                            if should_send:
                                logger.debug(f"Sending Ollama batched chunk of {len(chunk_buffer)} characters")
                                await websocket.send_json({"chunk": chunk_buffer})
                                chunk_buffer = ""
                                last_send_time = current_time
                                await asyncio.sleep(0.001)  # Small delay to prevent overwhelming frontend
                    
                    # Send any remaining content
                    if chunk_buffer:
                        logger.debug(f"Sending final Ollama chunk of {len(chunk_buffer)} characters")
                        await websocket.send_json({"chunk": chunk_buffer})
                        
                    await websocket.send_json({"finish_reason": "completed"})
                    logger.info(f"Completed Ollama chat response for model: {selected_model}")
                    
                else:
                    # Model not found in either service
                    logger.error(f"Model '{selected_model}' not found in available models")
                    await websocket.send_json({"error": f"Model '{selected_model}' not found in available models."})
                    await websocket.send_json({"finish_reason": "error"})
                    
            except Exception as e:
                logger.error(f"Error during chat processing: {str(e)}", exc_info=True)
                bot_reply = f"Error: {str(e)}"
                await websocket.send_json({"error": bot_reply})
                await websocket.send_json({"finish_reason": "error"})

    except WebSocketDisconnect:
        # Client disconnected, no need to close the connection
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        # Only try to close if it wasn't a disconnect error
        try:
            await websocket.close()
        except RuntimeError:
            # Connection might already be closed
            logger.warning("Failed to close WebSocket connection (may already be closed)")


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
