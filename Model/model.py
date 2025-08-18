from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    content: str

class TaskResponse(BaseModel):
    intent: str
    task_name: Optional[str] = None
    task_time: Optional[str] = None
    priority: Optional[str] = None
    raw_text: str