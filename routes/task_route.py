from fastapi import APIRouter, HTTPException, status
from control.control import ask_mistral
from Model.model import Message, TaskResponse
import logging
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/task", tags=["Task Management"])

NODE_API_BASE = os.getenv("NODE_API_BASE", "http://localhost:3000")

@router.post("/chat",response_model=TaskResponse,
             status_code=status.HTTP_200_OK)

async def chat( request: Message):

    user_message = request.content.strip()
        
    if not user_message:
        raise HTTPException(status_code=400,
                             detail="Message content cannot be empty")

    try:
        logger.info(f"Processing text input: {request.content}")
        result = await ask_mistral(request.content)
        logger.info(f"Text processing result: {result}")

        intent = result.get("intent")
    
        required_keys = {"intent", "task_name", "task_time", "priority", "raw_text"}
        if not required_keys.issubset(set(result.keys())):
            logger.warning("LLM response missing some expected keys")

        async with httpx.AsyncClient() as client:
            if intent == "add_task":
               
                payload = {
                    "name": result.get("task_name"),
                    "time": result.get("task_time"),
                    "priority": result.get("priority")
                }
                
                resp = await client.post(f"{NODE_API_BASE}/tasks", json=payload, timeout=10.0)
                resp.raise_for_status()
                logger.info(f"Created task in Node backend: {resp.json()}")

            elif intent == "update_task":
                task_name = result.get("task_name")
                if not task_name:
                    raise HTTPException(status_code=400, detail="Task name required for update")

                # 1. Get all tasks
                resp = await client.get(f"{NODE_API_BASE}/tasks", timeout=10.0)
                resp.raise_for_status()
                tasks = resp.json()

                task_to_update = next((t for t in tasks if t["name"] == task_name), None)
                if not task_to_update:
                    raise HTTPException(status_code=404, detail="Task not found")

                task_id = task_to_update["id"]
                payload = {
                    "name": result.get("task_name"),
                    "time": result.get("task_time"),
                    "priority": result.get("priority")
                }

                resp = await client.put(f"{NODE_API_BASE}/tasks/{task_id}", json=payload, timeout=10.0)
                resp.raise_for_status()
                logger.info(f"Updated task in Node backend: {resp.json()}")

            elif intent == "delete_task":
                
                task_name = result.get("task_name")
                if not task_name:
                    raise HTTPException(status_code=400, detail="Task name required for deletion")

                resp = await client.get(f"{NODE_API_BASE}/tasks", timeout=10.0)
                resp.raise_for_status()
                tasks = resp.json()

                task_to_delete = next((t for t in tasks if t["name"] == task_name), None)
                if not task_to_delete:
                    raise HTTPException(status_code=404, detail="Task not found")

                task_id = task_to_delete["id"]
                resp = await client.delete(f"{NODE_API_BASE}/tasks/{task_id}", timeout=10.0)
                resp.raise_for_status()
                logger.info(f"Deleted task in Node backend: {resp.json()}")

            else:
                logger.info(f"No backend action required for intent: {intent}")

        return result

    except httpx.HTTPStatusError as hx:
        logger.error(f"Node backend error: {str(hx)}")
        raise HTTPException(status_code=502, detail=f"Backend error: {hx.response.text}")

    except Exception as e:
        logger.error(f"Error processing text input: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")
