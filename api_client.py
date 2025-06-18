"""
api_client.py - API Communication Layer
Handles all API interactions with OpenAI and LM Studio
"""
import requests
from typing import List
from models import APIConfig, APIProvider


class APIClient:
    """API client with structured JSON response request"""

    # System prompt requesting JSON format
    SYSTEM_PROMPT = """You are a professional chef AI assistant. When users ask about recipes or cooking, provide a detailed response in the following JSON format:

{
  "name": "Recipe Name",
  "description": "Brief description of the dish",
  "prep_time": "15 minutes",
  "cook_time": "30 minutes",
  "servings": "4",
  "difficulty": "Easy/Medium/Hard",
  "ingredients": [
    {"amount": "2 cups", "item": "flour"},
    {"amount": "1 tsp", "item": "salt"}
  ],
  "instructions": [
    "Step 1 description",
    "Step 2 description"
  ],
  "tips": [
    "Helpful tip 1",
    "Helpful tip 2"
  ],
  "tags": ["healthy", "quick", "vegetarian"],
  "nutrition": {
    "calories": "250",
    "protein": "15g",
    "carbs": "30g",
    "fat": "10g"
  }
}

Important: Provide ONLY the JSON response, no additional text before or after."""

    def __init__(self, config: APIConfig):
        self.config = config

    def send_message(self, message: str) -> str:
        """Send message to AI and get response"""
        try:
            if self.config.provider == APIProvider.OPENAI:
                return self._send_openai_message(message)
            else:
                return self._send_lm_studio_message(message)
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection failed. Please check your internet connection.")
        except Exception as e:
            raise Exception(f"API Error: {str(e)}")

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            if self.config.provider == APIProvider.OPENAI:
                # Return common OpenAI models
                return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
            else:
                return self._get_lm_studio_models()
        except:
            return []

    def validate_connection(self) -> bool:
        """Test if the API connection is working"""
        try:
            if self.config.provider == APIProvider.OPENAI:
                # Test with a minimal request
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }
                response = requests.get(
                    f"{self.config.base_url}/models",
                    headers=headers,
                    timeout=5
                )
                return response.status_code == 200
            else:
                # Test LM Studio connection
                response = requests.get(
                    f"{self.config.base_url}/models",
                    timeout=5
                )
                return response.status_code == 200
        except:
            return False

    def _send_openai_message(self, message: str) -> str:
        """Send message via OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        response = requests.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 401:
            raise Exception("Invalid API key. Please check your OpenAI API key.")
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded. Please wait a moment and try again.")
        elif response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            raise Exception(error_msg)

        response_data = response.json()
        return response_data['choices'][0]['message']['content']

    def _send_lm_studio_message(self, message: str) -> str:
        """Send message via LM Studio API"""
        # Determine timeout for LM Studio
        timeout = self.config.lm_studio_timeout if self.config.lm_studio_timeout is not None else 120

        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.config.base_url}/chat/completions",
                json=data,
                timeout=timeout
            )
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Cannot connect to LM Studio. Please ensure:\n"
                "1. LM Studio is running\n"
                "2. Server is started (look for 'Server Started' in LM Studio)\n"
                "3. The port matches (default: 1234)"
            )

        if response.status_code == 404:
            raise Exception(
                f"Model '{self.config.model}' not found in LM Studio.\n"
                "Please check the model name or refresh the model list."
            )
        elif response.status_code != 200:
            raise Exception(f"LM Studio error: {response.status_code}")

        response_data = response.json()
        return response_data['choices'][0]['message']['content']

    def _get_lm_studio_models(self) -> List[str]:
        """Get available models from LM Studio"""
        try:
            response = requests.get(
                f"{self.config.base_url}/models",
                timeout=5
            )

            if response.status_code == 200:
                models_data = response.json()
                models = models_data.get('data', [])
                return [model['id'] for model in models if 'id' in model]
            else:
                return []
        except:
            return []
