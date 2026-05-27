import requests
import json
from config import OLLAMA_URL, OLLAMA_MODEL, SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

class LLMEngine:
    def __init__(self):
        self.url     = f"{OLLAMA_URL}/api/chat"
        self.model   = OLLAMA_MODEL
        logger.info(f"LLM engine ready — model: {self.model}")

    def chat(self, user_message: str,
             conversation_history: list) -> str:
        """
        Takes user message + conversation history
        Returns ZYRA's response as string
        """
        try:
            # Build message array with system prompt
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

            # Add conversation history for context
            messages.extend(conversation_history[-10:])  # last 10 turns

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            payload = {
                "model":    self.model,
                "messages": messages,
                "stream":   False,
                "options": {
                    "temperature": 0.7,
                    "top_p":       0.9,
                    "num_predict": 150  # keep responses concise
                }
            }

            response = requests.post(
                self.url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result  = response.json()
            content = result["message"]["content"].strip()

            logger.info(f"LLM response: '{content}'")
            return content

        except requests.exceptions.Timeout:
            logger.error("LLM timeout")
            return "I'm taking too long to think. Please try again."

        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "I encountered an error. Please try again."