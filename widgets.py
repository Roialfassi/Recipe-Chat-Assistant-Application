"""
widgets.py - Custom UI Components
All custom PyQt5 widgets for the recipe chat interface
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import Dict, List, Optional
from models import AppTheme, ParsedRecipe, APIProvider, APIConfig


# ============== Base Components ==============
class ModernCard(QFrame):
    """Base class for modern card-style widgets"""

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

    def set_card_style(self, bg_color: str, border_color: str = None):
        """Apply modern card styling with shadow"""
        style = f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 12px;
                padding: 12px;
                margin: 4px;
            }}
        """
        if border_color:
            style = style.replace("}", f"    border: 2px solid {border_color};\n}}")

        self.setStyleSheet(style)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


# ============== Recipe Display Widgets ==============
class IngredientCard(ModernCard):
    """Enhanced ingredient display card"""

    def __init__(self, ingredient: dict):
        super().__init__()
        self.set_card_style(AppTheme.COLORS['ingredient_bg'], AppTheme.COLORS['ingredient_accent'])

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(AppTheme.EMOJIS['ingredients'])
        icon_label.setFont(QFont("Segoe UI Emoji", 18))
        layout.addWidget(icon_label)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        # Item name
        item_label = QLabel(ingredient.get('item', ''))
        item_label.setFont(QFont("Arial", 11, QFont.Bold))
        item_label.setStyleSheet(f"color: {AppTheme.COLORS['text_primary']};")
        content_layout.addWidget(item_label)

        # Amount
        amount = ingredient.get('amount', '')
        if amount:
            amount_label = QLabel(amount)
            amount_label.setFont(QFont("Arial", 10))
            amount_label.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']};")
            content_layout.addWidget(amount_label)

        layout.addLayout(content_layout, 1)
        self.setLayout(layout)


class InstructionCard(ModernCard):
    """Enhanced instruction card with checkbox"""

    def __init__(self, step_number: int, instruction: str):
        super().__init__()
        self.set_card_style(AppTheme.COLORS['instruction_bg'])

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Checkbox with custom style
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border-radius: 12px;
                border: 2px solid #4CAF50;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjUgNC41TDYgMTJMMi41IDguNSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
        """)
        self.checkbox.stateChanged.connect(self._on_check_changed)
        layout.addWidget(self.checkbox)

        # Step number badge
        step_badge = QLabel(f"{step_number}")
        step_badge.setFixedSize(30, 30)
        step_badge.setAlignment(Qt.AlignCenter)
        step_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {AppTheme.COLORS['instruction_accent']};
                color: white;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        layout.addWidget(step_badge)

        # Instruction text
        self.text_label = QLabel(instruction)
        self.text_label.setWordWrap(True)
        self.text_label.setFont(QFont("Arial", 11))
        self.text_label.setStyleSheet(f"color: {AppTheme.COLORS['text_primary']};")
        layout.addWidget(self.text_label, 1)

        self.setLayout(layout)

    def _on_check_changed(self, state):
        """Handle checkbox state change"""
        if state == Qt.Checked:
            self.text_label.setStyleSheet(f"""
                color: {AppTheme.COLORS['text_secondary']};
                text-decoration: line-through;
            """)
            self.setWindowOpacity(0.7)
        else:
            self.text_label.setStyleSheet(f"color: {AppTheme.COLORS['text_primary']};")
            self.setWindowOpacity(1.0)


class TipCard(ModernCard):
    """Card for displaying tips"""

    def __init__(self, tip: str):
        super().__init__()
        self.set_card_style(AppTheme.COLORS['tip_bg'])

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(AppTheme.EMOJIS['tips'])
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        layout.addWidget(icon_label)

        # Tip text
        tip_label = QLabel(tip)
        tip_label.setWordWrap(True)
        tip_label.setFont(QFont("Arial", 10))
        tip_label.setStyleSheet(f"color: {AppTheme.COLORS['text_primary']};")
        layout.addWidget(tip_label, 1)

        self.setLayout(layout)


class TagBadge(QFrame):
    """Modern tag badge"""

    def __init__(self, tag: str):
        super().__init__()

        color, emoji = AppTheme.get_tag_style(tag)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 16px;
                padding: 6px 12px;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Emoji
        emoji_label = QLabel(emoji)
        emoji_label.setFont(QFont("Segoe UI Emoji", 12))
        layout.addWidget(emoji_label)

        # Text
        text_label = QLabel(tag)
        text_label.setFont(QFont("Arial", 10, QFont.Bold))
        text_label.setStyleSheet("color: white;")
        layout.addWidget(text_label)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


class RecipeInfoCard(ModernCard):
    """Card displaying recipe metadata"""

    def __init__(self, recipe: ParsedRecipe):
        super().__init__()
        self.set_card_style(AppTheme.COLORS['card_bg'])

        layout = QGridLayout()
        layout.setSpacing(12)

        # Recipe name
        if recipe.name:
            name_label = QLabel(recipe.name)
            name_label.setFont(QFont("Arial", 16, QFont.Bold))
            name_label.setStyleSheet(f"color: {AppTheme.COLORS['primary_dark']};")
            layout.addWidget(name_label, 0, 0, 1, 2)

        # Description
        if recipe.description:
            desc_label = QLabel(recipe.description)
            desc_label.setWordWrap(True)
            desc_label.setFont(QFont("Arial", 11))
            desc_label.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']};")
            layout.addWidget(desc_label, 1, 0, 1, 2)

        # Metadata row
        row = 2
        if recipe.prep_time:
            self._add_info_item(layout, row, 0, AppTheme.EMOJIS['time'], "Prep", recipe.prep_time)
        if recipe.cook_time:
            self._add_info_item(layout, row, 1, AppTheme.EMOJIS['time'], "Cook", recipe.cook_time)

        row = 3
        if recipe.servings:
            self._add_info_item(layout, row, 0, AppTheme.EMOJIS['servings'], "Servings", recipe.servings)
        if recipe.difficulty:
            self._add_info_item(layout, row, 1, AppTheme.EMOJIS['difficulty'], "Level", recipe.difficulty)

        self.setLayout(layout)

    def _add_info_item(self, layout: QGridLayout, row: int, col: int, emoji: str, label: str, value: str):
        """Add an info item to the grid"""
        container = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(6)

        # Emoji
        emoji_label = QLabel(emoji)
        emoji_label.setFont(QFont("Segoe UI Emoji", 14))
        item_layout.addWidget(emoji_label)

        # Label and value
        text_label = QLabel(f"<b>{label}:</b> {value}")
        text_label.setFont(QFont("Arial", 10))
        item_layout.addWidget(text_label)

        container.setLayout(item_layout)
        layout.addWidget(container, row, col)


# ============== Chat Components ==============
class MessageBubble(ModernCard):
    """Enhanced message bubble with gradient"""

    def __init__(self, message: str, is_user: bool = True):
        super().__init__()

        if is_user:
            gradient_start = AppTheme.COLORS['user_start']
            gradient_end = AppTheme.COLORS['user_end']
        else:
            gradient_start = AppTheme.COLORS['ai_start']
            gradient_end = AppTheme.COLORS['ai_end']

        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {gradient_start}, stop:1 {gradient_end});
                border-radius: 18px;
                padding: 12px 16px;
                margin: 4px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Message text
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Arial", 11))
        self.message_label.setStyleSheet("color: white;")
        self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.message_label)

        self.setLayout(layout)

        # Set maximum width
        self.setMaximumWidth(600)


class LoadingWidget(QWidget):
    """Animated loading indicator"""

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)

        loading_label = QLabel("🔄 Cooking up a response...")
        loading_label.setFont(QFont("Arial", 11))
        loading_label.setStyleSheet(f"color: {AppTheme.COLORS['text_secondary']};")

        layout.addWidget(loading_label)
        layout.addStretch()

        self.setLayout(layout)


class ErrorWidget(ModernCard):
    """Error message widget"""

    def __init__(self, error: str):
        super().__init__()
        self.set_card_style('#FFEBEE', '#F44336')

        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Error icon
        icon_label = QLabel(AppTheme.EMOJIS['error'])
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        layout.addWidget(icon_label)

        # Error message
        error_label = QLabel(f"<b>Error:</b> {error}")
        error_label.setWordWrap(True)
        error_label.setFont(QFont("Arial", 11))
        error_label.setStyleSheet(f"color: {AppTheme.COLORS['error']};")
        layout.addWidget(error_label, 1)

        self.setLayout(layout)


# ============== Settings Components ==============
class SettingsPanel(QGroupBox):
    """Enhanced collapsible settings panel"""

    # Signals
    refresh_models_requested = pyqtSignal()
    save_settings_requested = pyqtSignal()

    def __init__(self):
        super().__init__("⚙️ API Settings")
        self.setCheckable(True)
        self.setChecked(False)

        self.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #424242;
            }
            QGroupBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)

        # Animation for smooth collapse/expand
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.toggled.connect(self._on_toggled)
        self.setMaximumHeight(40)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the settings UI"""
        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Provider selection
        layout.addWidget(self._create_label("Provider:"), 0, 0)
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([p.value for p in APIProvider])
        self.provider_combo.setStyleSheet(self._get_input_style())
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        layout.addWidget(self.provider_combo, 0, 1, 1, 2)

        # API Key
        layout.addWidget(self._create_label("API Key:"), 1, 0)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your OpenAI API key")
        self.api_key_input.setStyleSheet(self._get_input_style())
        layout.addWidget(self.api_key_input, 1, 1, 1, 2)

        # Model selection
        layout.addWidget(self._create_label("Model:"), 2, 0)
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Enter model name or select from list")
        self.model_input.setStyleSheet(self._get_input_style())
        layout.addWidget(self.model_input, 2, 1)

        # Model dropdown (for suggestions)
        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet(self._get_input_style())
        self.model_combo.currentTextChanged.connect(lambda text: self.model_input.setText(text) if text else None)
        layout.addWidget(self.model_combo, 2, 2)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.refresh_button = QPushButton("🔄 Refresh Models")
        self.refresh_button.setStyleSheet(self._get_button_style(AppTheme.COLORS['accent']))
        self.refresh_button.clicked.connect(self.refresh_models_requested)
        button_layout.addWidget(self.refresh_button)

        self.save_button = QPushButton("💾 Save Settings")
        self.save_button.setStyleSheet(self._get_button_style(AppTheme.COLORS['primary']))
        self.save_button.clicked.connect(self.save_settings_requested)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout, 3, 0, 1, 3)

        self.setLayout(layout)

        # Initialize with OpenAI defaults
        self._on_provider_changed("OpenAI")

    def _create_label(self, text: str) -> QLabel:
        """Create a styled label"""
        label = QLabel(text)
        label.setFont(QFont("Arial", 11))
        label.setStyleSheet(f"color: {AppTheme.COLORS['text_primary']};")
        return label

    def _get_input_style(self) -> str:
        """Get input field style"""
        return f"""
            QLineEdit, QComboBox {{
                border: 2px solid {AppTheme.COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {AppTheme.COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {AppTheme.COLORS['text_secondary']};
                width: 0;
                height: 0;
                margin-right: 5px;
            }}
        """

    def _get_button_style(self, color: str) -> str:
        """Get button style"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """

    def _on_toggled(self, checked):
        """Handle expand/collapse animation"""
        if checked:
            self.animation.setStartValue(40)
            self.animation.setEndValue(self.sizeHint().height())
        else:
            self.animation.setStartValue(self.maximumHeight())
            self.animation.setEndValue(40)

        self.animation.start()

    def _on_provider_changed(self, provider_name: str):
        """Handle provider change"""
        if provider_name == "OpenAI":
            self.api_key_input.setEnabled(True)
            self.api_key_input.setPlaceholderText("Enter your OpenAI API key")
            self.model_combo.clear()
            self.model_combo.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"])
            self.model_input.setText("gpt-3.5-turbo")
        else:  # LM Studio
            self.api_key_input.setEnabled(False)
            self.api_key_input.setPlaceholderText("Not required for LM Studio")
            self.model_combo.clear()
            self.model_combo.addItem("Click 'Refresh Models' to load")
            self.model_input.setPlaceholderText("Enter model name or refresh to see available")
            self.model_input.clear()

    def get_config(self) -> Optional[APIConfig]:
        """Get current configuration"""
        provider = APIProvider(self.provider_combo.currentText())
        api_key = self.api_key_input.text() if provider == APIProvider.OPENAI else None
        model = self.model_input.text().strip()

        if provider == APIProvider.OPENAI and not api_key:
            QMessageBox.warning(self, "Missing API Key", "Please enter your OpenAI API key")
            return None

        if not model:
            QMessageBox.warning(self, "No Model Selected", "Please enter or select a model")
            return None

        return APIConfig(provider=provider, api_key=api_key, model=model)

    def set_models(self, models: List[str]):
        """Set available models in dropdown"""
        self.model_combo.clear()
        if models:
            self.model_combo.addItems(models)
            if not self.model_input.text() and models:
                self.model_input.setText(models[0])
        else:
            self.model_combo.addItem("No models found")
