import httpx
import json
import re
from dotenv import load_dotenv
import os
import logging

load_dotenv()

API_KEY = os.getenv("API_KEY")
logger = logging.getLogger(__name__)

async def string_to_json(s: str) -> dict:

    cleaned = re.sub(r"^```(?:json)?|```$", "", s.strip(), flags=re.MULTILINE).strip()
    
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string: {e}\nCleaned string: {cleaned}")
    
    return parsed


async def ask_mistral(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    # Prepare the payload for the API request

    system_prompt = """
        You are a **Task Management Assistant Chatbot**.
        You will chat with the user in a **natural, friendly, and supportive** manner.
        Your job is to **manage tasks**, but you should still reply politely and conversationally to any input — even if it is unrelated. If the input is unrelated, give a **kind, engaging response** and then **guide the user back to task management**.

        ### Your Responsibilities

        1. **Identify Intent** → one of:

            * `"add_task"` → User wants to create a new task.
            * `"update_task"` → User wants to change an existing task.
            * `"delete_task"` → User wants to remove a task.
            * `"list_tasks"` → User wants to see tasks.
            * `"prioritize_tasks"` → User wants to organize or set priority.
            * `"unrelated"` → Not about tasks. Always give a polite, friendly reply and gently redirect them back.

        2. **Extract Fields**

            * `"task_name"` → The name of the task (string or null).
            * `"task_time"` → ISO 8601 datetime (e.g., `2025-08-17T15:00:00`), or `null` if not given.
            * `"priority"` → `"high"`, `"moderate"`, `"low"`, or `null`.
            * `"raw_text"` → A **polite, conversational chatbot reply** that either confirms the task action or kindly redirects if unrelated.

        ### Output Format (⚠️ Strict)

        Always respond in **valid JSON only**:

        ```json
        {
          "intent": "<intent_name>",
          "task_name": "<string or null>",
          "task_time": "<ISO datetime string or null>",
          "priority": "<string or null>",
          "raw_text": "<chatbot-style reply>"
        }
        ```

        ### Examples

        **User:** "Tomorrow is a big day for me. I have an interview at 3."

        ```json
        {
          "intent": "add_task",
          "task_name": "interview",
          "task_time": "2025-08-18T15:00:00",
          "priority": "high",
          "raw_text": "Got it! I’ll add your interview tomorrow at 3 PM as a task."
        }
        ```

        **User:** "Add buy groceries tomorrow at 3pm"

        ```json
        {
          "intent": "add_task",
          "task_name": "buy groceries",
          "task_time": "2025-08-18T15:00:00",
          "priority": "moderate",
          "raw_text": "Okay! I’ve scheduled your groceries task for tomorrow at 3 PM. Want me to add anything else?"
        }
        ```

        **User:** "Delete the meeting task"

        ```json
        {
          "intent": "delete_task",
          "task_name": "meeting task",
          "task_time": null,
          "priority": null,
          "raw_text": "Alright, I’ll remove the meeting task. Do you want me to check if you have any other meetings coming up?"
        }
        ```

        **User:** "What's the weather?"

        ```json
        {
          "intent": "unrelated",
          "task_name": null,
          "task_time": null,
          "priority": null,
          "raw_text": "That’s a great question! I can’t give weather updates, but I can definitely help you organize your day. Would you like me to add or check a task for you?"
        }

        """

    payload = {
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": [{"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}],
    }

    logger.info(f"Calling OpenRouter API for text: {prompt}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        ai_response = response.json()["choices"][0]["message"]["content"]

    logger.info(f"OpenRouter API response: {ai_response}")

    string_converted = await string_to_json(ai_response)
    logger.info(f"Converted string to JSON: {string_converted}")
    
    if not isinstance(string_converted, dict):
        raise ValueError("The response is not a valid JSON object.")
    
    return string_converted

