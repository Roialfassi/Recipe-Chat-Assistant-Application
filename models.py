"""
models.py - Data Models and Structures
Contains all data classes and enums used throughout the application
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class APIProvider(Enum):
    """Supported API providers"""
    OPENAI = "OpenAI"
    ANTHROPIC = "Anthropic (Claude)"
    GOOGLE = "Google (Gemini)"
    HUGGINGFACE = "HuggingFace"
    COHERE = "Cohere"
    LM_STUDIO = "LM Studio (Local)"
    OLLAMA = "Ollama (Local)"
    CUSTOM = "Custom API"


@dataclass
class APIConfig:
    """API configuration settings"""
    provider: APIProvider
    api_key: Optional[str] = None
    base_url: str = ""
    model: str = ""

    # Additional settings for specific providers
    organization_id: Optional[str] = None  # For OpenAI
    project_id: Optional[str] = None  # For Google
    custom_headers: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Set provider-specific default URLs"""
        if not self.base_url:
            defaults = {
                APIProvider.OPENAI: "https://api.openai.com/v1",
                APIProvider.ANTHROPIC: "https://api.anthropic.com/v1",
                APIProvider.GOOGLE: "https://generativelanguage.googleapis.com/v1beta",
                APIProvider.HUGGINGFACE: "https://api-inference.huggingface.co/models",
                APIProvider.COHERE: "https://api.cohere.ai/v1",
                APIProvider.LM_STUDIO: "http://localhost:1234/v1",
                APIProvider.OLLAMA: "http://localhost:11434/api",
                APIProvider.CUSTOM: ""
            }
            self.base_url = defaults.get(self.provider, "")


@dataclass
class ParsedRecipe:
    """Structured recipe data from JSON response"""
    name: str = ""
    description: str = ""
    prep_time: str = ""
    cook_time: str = ""
    servings: str = ""
    difficulty: str = ""
    ingredients: List[Dict[str, str]] = field(default_factory=list)  # {"item": "...", "amount": "..."}
    instructions: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    nutrition: Dict[str, str] = field(default_factory=dict)


# ============== Provider Configurations ==============
@dataclass
class ProviderInfo:
    """Information about an API provider"""
    name: str
    requires_api_key: bool
    supports_streaming: bool
    supports_json_mode: bool
    default_models: List[str]
    api_key_help: str
    setup_instructions: str


PROVIDER_INFO = {
    APIProvider.OPENAI: ProviderInfo(
        name="OpenAI",
        requires_api_key=True,
        supports_streaming=True,
        supports_json_mode=True,
        default_models=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        api_key_help="Get your API key from https://platform.openai.com/api-keys",
        setup_instructions="Enter your OpenAI API key and select a model."
    ),
    APIProvider.ANTHROPIC: ProviderInfo(
        name="Anthropic",
        requires_api_key=True,
        supports_streaming=True,
        supports_json_mode=False,
        default_models=["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        api_key_help="Get your API key from https://console.anthropic.com/",
        setup_instructions="Enter your Anthropic API key and select a Claude model."
    ),
    APIProvider.GOOGLE: ProviderInfo(
        name="Google Gemini",
        requires_api_key=True,
        supports_streaming=True,
        supports_json_mode=False,
        default_models=["gemini-pro", "gemini-pro-vision"],
        api_key_help="Get your API key from https://makersuite.google.com/app/apikey",
        setup_instructions="Enter your Google AI API key and select a Gemini model."
    ),
    APIProvider.HUGGINGFACE: ProviderInfo(
        name="HuggingFace",
        requires_api_key=True,
        supports_streaming=False,
        supports_json_mode=False,
        default_models=["mistralai/Mixtral-8x7B-Instruct-v0.1", "meta-llama/Llama-2-70b-chat-hf", "google/flan-t5-xxl"],
        api_key_help="Get your API token from https://huggingface.co/settings/tokens",
        setup_instructions="Enter your HuggingFace API token and model name."
    ),
    APIProvider.COHERE: ProviderInfo(
        name="Cohere",
        requires_api_key=True,
        supports_streaming=True,
        supports_json_mode=False,
        default_models=["command", "command-light", "command-nightly"],
        api_key_help="Get your API key from https://dashboard.cohere.ai/api-keys",
        setup_instructions="Enter your Cohere API key and select a model."
    ),
    APIProvider.LM_STUDIO: ProviderInfo(
        name="LM Studio",
        requires_api_key=False,
        supports_streaming=True,
        supports_json_mode=False,
        default_models=[],
        api_key_help="No API key required for local models",
        setup_instructions="Start LM Studio server and enter your model name."
    ),
    APIProvider.OLLAMA: ProviderInfo(
        name="Ollama",
        requires_api_key=False,
        supports_streaming=True,
        supports_json_mode=False,
        default_models=["llama2", "mistral", "codellama", "vicuna"],
        api_key_help="No API key required for local models",
        setup_instructions="Start Ollama and enter a model name (e.g., 'llama2')."
    ),
    APIProvider.CUSTOM: ProviderInfo(
        name="Custom API",
        requires_api_key=True,
        supports_streaming=False,
        supports_json_mode=False,
        default_models=[],
        api_key_help="Enter credentials as required by your custom API",
        setup_instructions="Configure base URL, API key, and model as needed."
    ),
}


# ============== Theme Configuration ==============
class AppTheme:
    """Application theme colors and emojis"""

    # Modern color palette
    COLORS = {
        # Primary colors
        'primary': '#2E7D32',
        'primary_light': '#4CAF50',
        'primary_dark': '#1B5E20',

        # Accent colors
        'accent': '#FF6F00',
        'accent_light': '#FFA726',
        'accent_dark': '#E65100',

        # Message bubbles
        'user_start': '#5C6BC0',
        'user_end': '#3F51B5',
        'ai_start': '#26A69A',
        'ai_end': '#00897B',

        # Cards and sections
        'card_bg': '#FFFFFF',
        'card_shadow': 'rgba(0, 0, 0, 0.1)',
        'section_bg': '#FAFAFA',

        # Recipe elements
        'ingredient_bg': '#FFF3E0',
        'ingredient_accent': '#FF9800',
        'instruction_bg': '#E8F5E9',
        'instruction_accent': '#4CAF50',
        'tip_bg': '#E3F2FD',
        'tip_accent': '#2196F3',

        # Tags and badges
        'tag_healthy': '#66BB6A',
        'tag_quick': '#AB47BC',
        'tag_easy': '#42A5F5',
        'tag_tasty': '#EC407A',
        'tag_diet': '#26C6DA',
        'tag_default': '#78909C',

        # UI elements
        'background': '#F5F5F5',
        'text_primary': '#212121',
        'text_secondary': '#757575',
        'border': '#E0E0E0',
        'error': '#F44336',
        'success': '#4CAF50',
        'warning': '#FF9800'
    }

    # Enhanced emojis
    EMOJIS = {
        'recipe': '👨‍🍳',
        'ingredients': '🥘',
        'instructions': '📝',
        'tips': '💡',
        'time': '⏱️',
        'servings': '🍽️',
        'difficulty': '📊',
        'nutrition': '📊',
        'healthy': '🥗',
        'quick': '⚡',
        'easy': '👌',
        'tasty': '😋',
        'vegetarian': '🌱',
        'protein': '💪',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }

    @classmethod
    def get_tag_style(cls, tag: str) -> tuple:
        """Get color and emoji for a tag"""
        tag_lower = tag.lower()

        if any(word in tag_lower for word in ['healthy', 'nutritious', 'vitamin']):
            return cls.COLORS['tag_healthy'], cls.EMOJIS['healthy']
        elif any(word in tag_lower for word in ['quick', 'fast', 'minute']):
            return cls.COLORS['tag_quick'], cls.EMOJIS['quick']
        elif any(word in tag_lower for word in ['easy', 'simple', 'beginner']):
            return cls.COLORS['tag_easy'], cls.EMOJIS['easy']
        elif any(word in tag_lower for word in ['tasty', 'delicious', 'flavor']):
            return cls.COLORS['tag_tasty'], cls.EMOJIS['tasty']
        elif any(word in tag_lower for word in ['vegetarian', 'vegan', 'plant']):
            return cls.COLORS['tag_diet'], cls.EMOJIS['vegetarian']
        elif any(word in tag_lower for word in ['protein', 'muscle', 'strength']):
            return cls.COLORS['tag_default'], cls.EMOJIS['protein']
        else:
            return cls.COLORS['tag_default'], '🏷️'
