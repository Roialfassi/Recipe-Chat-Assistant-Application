"""
parser.py - Recipe JSON Parser
Handles extraction and parsing of JSON recipe data from LLM responses
"""
import re
import json
from typing import Dict, Any
from models import ParsedRecipe


class RecipeJSONParser:
    """Extract and parse JSON recipe data from LLM responses"""

    def parse_response(self, text: str) -> ParsedRecipe:
        """Extract JSON from response text and parse into recipe object"""
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', text)

        if json_match:
            try:
                json_str = json_match.group(0)
                # Clean up common JSON issues
                json_str = self._clean_json(json_str)
                data = json.loads(json_str)
                return self._parse_json_to_recipe(data)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                # Continue to fallback parser

        # Fallback: parse as plain text
        return self._parse_plain_text(text)

    def _clean_json(self, json_str: str) -> str:
        """Clean common JSON formatting issues"""
        # Remove trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        # Remove comments (if any)
        json_str = re.sub(r'//.*?\n', '\n', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)

        return json_str

    def _parse_json_to_recipe(self, data: dict) -> ParsedRecipe:
        """Convert JSON data to ParsedRecipe object"""
        recipe = ParsedRecipe()

        # Basic info
        recipe.name = data.get('name', data.get('title', 'Untitled Recipe'))
        recipe.description = data.get('description', '')
        recipe.prep_time = str(data.get('prep_time', data.get('prepTime', '')))
        recipe.cook_time = str(data.get('cook_time', data.get('cookTime', '')))
        recipe.servings = str(data.get('servings', ''))
        recipe.difficulty = data.get('difficulty', '')

        # Ingredients - handle various formats
        ingredients_data = data.get('ingredients', [])
        if isinstance(ingredients_data, list):
            for ing in ingredients_data:
                if isinstance(ing, dict):
                    # Already in correct format
                    recipe.ingredients.append(ing)
                elif isinstance(ing, str):
                    # Parse string format "2 cups flour"
                    parsed_ing = self._parse_ingredient_string(ing)
                    recipe.ingredients.append(parsed_ing)

        # Instructions
        instructions_data = data.get('instructions', data.get('steps', []))
        if isinstance(instructions_data, list):
            recipe.instructions = [str(inst) for inst in instructions_data]

        # Tips
        tips_data = data.get('tips', data.get('notes', []))
        if isinstance(tips_data, list):
            recipe.tips = [str(tip) for tip in tips_data]

        # Tags
        tags_data = data.get('tags', data.get('categories', []))
        if isinstance(tags_data, list):
            recipe.tags = [str(tag) for tag in tags_data]

        # Nutrition
        nutrition_data = data.get('nutrition', {})
        if isinstance(nutrition_data, dict):
            recipe.nutrition = {k: str(v) for k, v in nutrition_data.items()}

        return recipe

    def _parse_ingredient_string(self, ing_str: str) -> Dict[str, str]:
        """Parse ingredient string into amount and item"""
        ing_str = ing_str.strip()

        # Common patterns for ingredient parsing
        patterns = [
            # "2 cups flour"
            r'^(\d+(?:\.\d+)?(?:/\d+)?)\s+(\w+(?:\s+\w+)?)\s+(.+)$',
            # "1/2 cup sugar"
            r'^(\d+/\d+)\s+(\w+(?:\s+\w+)?)\s+(.+)$',
            # "2-3 tablespoons oil"
            r'^(\d+-\d+)\s+(\w+(?:\s+\w+)?)\s+(.+)$',
            # "1 (15 oz) can tomatoes"
            r'^(\d+)\s*\(([^)]+)\)\s+(.+)$',
        ]

        for pattern in patterns:
            match = re.match(pattern, ing_str)
            if match:
                if len(match.groups()) == 3:
                    amount = f"{match.group(1)} {match.group(2)}"
                    item = match.group(3)
                    return {'amount': amount.strip(), 'item': item.strip()}

        # If no pattern matches, check if it starts with a number
        if re.match(r'^\d', ing_str):
            parts = ing_str.split(' ', 2)
            if len(parts) >= 2:
                return {
                    'amount': f"{parts[0]} {parts[1] if len(parts) > 1 else ''}".strip(),
                    'item': parts[2] if len(parts) > 2 else parts[1]
                }

        # Default: whole string as item
        return {'amount': '', 'item': ing_str}

    def _parse_plain_text(self, text: str) -> ParsedRecipe:
        """Fallback parser for non-JSON responses"""
        recipe = ParsedRecipe(name="Recipe")
        lines = text.split('\n')

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            line_lower = line.lower()
            if 'ingredient' in line_lower:
                current_section = 'ingredients'
                continue
            elif any(word in line_lower for word in ['instruction', 'direction', 'step']):
                current_section = 'instructions'
                continue
            elif 'tip' in line_lower or 'note' in line_lower:
                current_section = 'tips'
                continue

            # Add to appropriate section
            if current_section == 'ingredients' and line:
                # Clean common prefixes
                cleaned = re.sub(r'^[-•*]\s*', '', line)
                cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
                if cleaned:
                    parsed_ing = self._parse_ingredient_string(cleaned)
                    recipe.ingredients.append(parsed_ing)

            elif current_section == 'instructions' and line:
                # Clean common prefixes
                cleaned = re.sub(r'^[-•*]\s*', '', line)
                cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
                cleaned = re.sub(r'^Step\s+\d+:?\s*', '', cleaned, flags=re.IGNORECASE)
                if cleaned:
                    recipe.instructions.append(cleaned)

            elif current_section == 'tips' and line:
                cleaned = re.sub(r'^[-•*]\s*', '', line)
                if cleaned:
                    recipe.tips.append(cleaned)

        # Try to extract tags from the text
        tag_keywords = [
            'healthy', 'quick', 'easy', 'vegetarian', 'vegan', 'gluten-free',
            'dairy-free', 'low-carb', 'keto', 'paleo', 'budget-friendly',
            'family-friendly', 'meal-prep', 'one-pot', '30-minute', '15-minute'
        ]

        text_lower = text.lower()
        for keyword in tag_keywords:
            if keyword in text_lower:
                recipe.tags.append(keyword.title().replace('-', ' '))

        return recipe
