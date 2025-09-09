from pydantic import BaseModel, Field


class AIModel(BaseModel):
    client_type: str = Field(..., description="Type of AI client, e.g., 'groq'")
    model_id: str = Field(..., description="ID of the AI model used")
    context_window: int = Field(default=0, description="Context window size of the model")
    owned_by: str = Field(default="unknown", description="Owner of the model")
