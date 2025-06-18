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
    LM_STUDIO = "LM Studio"


@dataclass
class APIConfig:
    """API configuration settings"""
    provider: APIProvider
    api_key: Optional[str] = None
    base_url: str = ""
    model: str = ""

    def __post_init__(self):
        """Set provider-specific default URLs"""
        if not self.base_url:
            if self.provider == APIProvider.OPENAI:
                self.base_url = "https://api.openai.com/v1"
            elif self.provider == APIProvider.LM_STUDIO:
                self.base_url = "http://localhost:1234/v1"


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
        'text_secondary': '#0a0a0a',
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
