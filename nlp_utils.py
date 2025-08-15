import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# OpenRouter API Configuration
API_KEY = "sk-or-v1-your-openrouter-api-key-here"  # Replace with your actual API key
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "mistralai/mistral-small-3.2-24b-instruct:free"

# Configure logging
logger = logging.getLogger(__name__)

def call_openrouter_api(text: str) -> Dict[str, Any]:
    """Call OpenRouter API for intent recognition and entity extraction"""
    
    # Detailed prompt for consistent JSON output
    system_prompt = """You are a task management assistant. Analyze user input and determine their intent regarding task management.

ALWAYS respond with valid JSON in exactly this format:
{
  "intent": "<intent_name>",
  "task_name": "<string or null>",
  "task_time": "<ISO datetime string or null>",
  "raw_text": "<original user text>"
}

Intent types:
- "add_task": User wants to create a new task
- "update_task": User wants to modify an existing task
- "delete_task": User wants to remove a task
- "list_tasks": User wants to see their tasks
- "prioritize_tasks": User wants to organize/prioritize tasks
- "unrelated": User is asking about something not task-related

For task_time, extract any time/date mentions and convert to ISO format (YYYY-MM-DDTHH:MM:SS). If no specific time is mentioned, use null.

Examples:
- "Add buy groceries tomorrow at 3pm" → {"intent": "add_task", "task_name": "buy groceries", "task_time": "2024-01-15T15:00:00", "raw_text": "Add buy groceries tomorrow at 3pm"}
- "Delete the meeting task" → {"intent": "delete_task", "task_name": "meeting task", "task_time": null, "raw_text": "Delete the meeting task"}
- "What's the weather?" → {"intent": "unrelated", "task_name": null, "task_time": null, "raw_text": "What's the weather?"}"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.1,
        "max_tokens": 300
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"Calling OpenRouter API for text: {text}")
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if 'choices' not in result or not result['choices']:
            raise Exception("Invalid API response format")
        
        ai_response = result['choices'][0]['message']['content'].strip()
        logger.info(f"OpenRouter API response: {ai_response}")
        
        # Parse JSON response
        try:
            parsed_result = json.loads(ai_response)
            
            # Ensure all required fields exist
            required_fields = ['intent', 'task_name', 'task_time', 'raw_text']
            for field in required_fields:
                if field not in parsed_result:
                    parsed_result[field] = None
            
            # Set raw_text to original input
            parsed_result['raw_text'] = text
            
            return parsed_result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {ai_response}")
            # Fallback response
            return {
                "intent": "unrelated",
                "task_name": None,
                "task_time": None,
                "raw_text": text
            }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API request failed: {str(e)}")
        raise Exception(f"API request failed: {str(e)}")
    except Exception as e:
        logger.error(f"OpenRouter API call failed: {str(e)}")
        raise Exception(f"AI processing failed: {str(e)}")

def process_text_input(text: str) -> Dict[str, Any]:
    """Process text input for intent recognition"""
    if not text or not text.strip():
        return {
            "intent": "unrelated",
            "task_name": None,
            "task_time": None,
            "raw_text": text
        }
    
    try:
        # Process the text through OpenRouter API
        result = call_openrouter_api(text.strip())
        
        # Handle unrelated intents with friendly message
        if result.get('intent') == 'unrelated':
            result['message'] = "I can only help with tasks right now."
            
        return result
    except Exception as e:
        logger.error(f"Error processing text input: {str(e)}")
        return {
            "intent": "unrelated",
            "task_name": None,
            "task_time": None,
            "raw_text": text
        }
