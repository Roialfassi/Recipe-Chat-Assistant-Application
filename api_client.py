"""
api_client.py - Universal API Communication Layer
Handles API interactions with multiple AI providers
"""
import requests
import json
from typing import List, Dict, Any, Optional
from models import APIConfig, APIProvider, PROVIDER_INFO


class APIClient:
    """Universal API client supporting multiple AI providers"""
    
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
            # Route to appropriate provider method
            provider_methods = {
                APIProvider.OPENAI: self._send_openai_message,
                APIProvider.ANTHROPIC: self._send_anthropic_message,
                APIProvider.GOOGLE: self._send_google_message,
                APIProvider.HUGGINGFACE: self._send_huggingface_message,
                APIProvider.COHERE: self._send_cohere_message,
                APIProvider.LM_STUDIO: self._send_lm_studio_message,
                APIProvider.OLLAMA: self._send_ollama_message,
                APIProvider.CUSTOM: self._send_custom_message,
            }
            
            method = provider_methods.get(self.config.provider)
            if not method:
                raise Exception(f"Unsupported provider: {self.config.provider}")
            
            return method(message)
            
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection failed. Please check your internet connection.")
        except Exception as e:
            raise Exception(f"API Error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models for the provider"""
        provider_info = PROVIDER_INFO.get(self.config.provider)
        if provider_info:
            # For providers with fixed model lists
            if provider_info.default_models:
                return provider_info.default_models
            
            # For local providers, try to fetch models
            if self.config.provider == APIProvider.LM_STUDIO:
                return self._get_lm_studio_models()
            elif self.config.provider == APIProvider.OLLAMA:
                return self._get_ollama_models()
        
        return []
    
    def validate_connection(self) -> bool:
        """Test if the API connection is working"""
        try:
            if self.config.provider == APIProvider.OPENAI:
                response = requests.get(
                    f"{self.config.base_url}/models",
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                    timeout=5
                )
                return response.status_code == 200
            elif self.config.provider in [APIProvider.LM_STUDIO, APIProvider.OLLAMA]:
                response = requests.get(f"{self.config.base_url}/tags", timeout=5)
                return response.status_code == 200
            else:
                # Basic connectivity check for other providers
                return True
        except:
            return False
    
    # ============== Provider-specific implementations ==============
    
    def _send_openai_message(self, message: str) -> str:
        """Send message via OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.config.organization_id:
            headers["OpenAI-Organization"] = self.config.organization_id
        
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
            timeout=1000
        )
        
        self._handle_openai_errors(response)
        return response.json()['choices'][0]['message']['content']
    
    def _send_anthropic_message(self, message: str) -> str:
        """Send message via Anthropic Claude API"""
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "user", "content": f"{self.SYSTEM_PROMPT}\n\nUser: {message}"}
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{self.config.base_url}/messages",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f"Anthropic API error: {error_data.get('error', {}).get('message', 'Unknown error')}")
        
        return response.json()['content'][0]['text']
    
    def _send_google_message(self, message: str) -> str:
        """Send message via Google Gemini API"""
        url = f"{self.config.base_url}/models/{self.config.model}:generateContent?key={self.config.api_key}"
        
        data = {
            "contents": [{
                "parts": [{
                    "text": f"{self.SYSTEM_PROMPT}\n\nUser: {message}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2000,
            }
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Google API error: {response.text}")
        
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    
    def _send_huggingface_message(self, message: str) -> str:
        """Send message via HuggingFace Inference API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        # Construct model URL
        model_url = f"{self.config.base_url}/{self.config.model}"
        
        data = {
            "inputs": f"{self.SYSTEM_PROMPT}\n\nUser: {message}\n\nAssistant:",
            "parameters": {
                "temperature": 0.7,
                "max_new_tokens": 2000,
                "return_full_text": False
            }
        }
        
        response = requests.post(
            model_url,
            headers=headers,
            json=data,
            timeout=60  # HuggingFace can be slower
        )
        
        if response.status_code == 503:
            raise Exception("Model is loading. Please try again in a few moments.")
        elif response.status_code != 200:
            raise Exception(f"HuggingFace API error: {response.text}")
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '')
        return str(result)
    
    def _send_cohere_message(self, message: str) -> str:
        """Send message via Cohere API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "message": message,
            "preamble": self.SYSTEM_PROMPT,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            f"{self.config.base_url}/chat",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f"Cohere API error: {error_data.get('message', 'Unknown error')}")
        
        return response.json()['text']
    
    def _send_lm_studio_message(self, message: str) -> str:
        """Send message via LM Studio API (OpenAI compatible)"""
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
                timeout=30
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
        
        return response.json()['choices'][0]['message']['content']
    
    def _send_ollama_message(self, message: str) -> str:
        """Send message via Ollama API"""
        data = {
            "model": self.config.model,
            "prompt": f"{self.SYSTEM_PROMPT}\n\nUser: {message}\n\nAssistant:",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 2000
            }
        }
        
        try:
            response = requests.post(
                f"{self.config.base_url}/generate",
                json=data,
                timeout=60  # Ollama can be slow
            )
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Cannot connect to Ollama. Please ensure:\n"
                "1. Ollama is installed and running\n"
                "2. The model is pulled (ollama pull <model>)\n"
                "3. The service is accessible on port 11434"
            )
        
        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")
        
        return response.json()['response']
    
    def _send_custom_message(self, message: str) -> str:
        """Send message via custom API endpoint"""
        headers = {
            "Content-Type": "application/json",
            **self.config.custom_headers
        }
        
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        # Generic format that works with many APIs
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
            self.config.base_url,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Custom API error: {response.status_code} - {response.text}")
        
        # Try common response formats
        result = response.json()
        if 'choices' in result:
            return result['choices'][0]['message']['content']
        elif 'response' in result:
            return result['response']
        elif 'text' in result:
            return result['text']
        elif 'generated_text' in result:
            return result['generated_text']
        else:
            # Return the entire response as string
            return json.dumps(result, indent=2)
    
    # ============== Helper methods ==============
    
    def _handle_openai_errors(self, response):
        """Handle OpenAI-specific error responses"""
        if response.status_code == 401:
            raise Exception("Invalid API key. Please check your OpenAI API key.")
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded. Please wait a moment and try again.")
        elif response.status_code == 404:
            raise Exception(f"Model '{self.config.model}' not found. Please check the model name.")
        elif response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            raise Exception(error_msg)
    
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
        except:
            pass
        return []
    
    def _get_ollama_models(self) -> List[str]:
        """Get available models from Ollama"""
        try:
            response = requests.get(
                f"{self.config.base_url}/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                models_data = response.json()
                models = models_data.get('models', [])
                return [model['name'] for model in models if 'name' in model]
        except:
            pass
        return []
