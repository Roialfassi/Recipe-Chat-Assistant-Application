"""
main.py - Main Application Window
The main Recipe Chat Assistant application
"""
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import Dict

# Import our modules
from models import AppTheme, ParsedRecipe
from api_client import APIClient
from response_parser import RecipeJSONParser
from widgets import (
    MessageBubble, LoadingWidget, ErrorWidget, ModernCard,
    IngredientCard, InstructionCard, TipCard, TagBadge,
    RecipeInfoCard, SettingsPanel
)


# ============== API Worker Thread ==============
class APIWorker(QThread):
    """Background thread for API calls"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_client: APIClient, message: str):
        super().__init__()
        self.api_client = api_client
        self.message = message

    def run(self):
        """Execute API call in background"""
        try:
            response = self.api_client.send_message(self.message)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))


# ============== Main Application Window ==============
class RecipeChatApp(QMainWindow):
    """Main application window with enhanced UI"""

    def __init__(self):
        super().__init__()
        self.api_client = None
        self.parser = RecipeJSONParser()
        self.current_worker = None

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🍳 Recipe Chat Assistant")
        self.setGeometry(100, 100, 1100, 800)
        self.setStyleSheet(f"QMainWindow {{ background-color: {AppTheme.COLORS['background']}; }}")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with margins
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        central_widget.setLayout(main_layout)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Settings panel
        self.settings_panel = SettingsPanel()
        self.settings_panel.refresh_models_requested.connect(self._refresh_models)
        self.settings_panel.save_settings_requested.connect(self._save_settings)
        main_layout.addWidget(self.settings_panel)

        # Chat area with modern styling
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {AppTheme.COLORS['card_bg']};
                border-radius: 12px;
            }}
            QScrollBar:vertical {{
                width: 12px;
                background: {AppTheme.COLORS['section_bg']};
                border-radius: 6px;
                margin: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {AppTheme.COLORS['border']};
                border-radius: 6px;
                min-height: 30px;
            }}
        """)
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(8)
        self.chat_layout.setContentsMargins(12, 12, 12, 12)
        self.chat_widget.setLayout(self.chat_layout)
        self.chat_scroll.setWidget(self.chat_widget)

        # Add shadow to chat area
        chat_shadow = QGraphicsDropShadowEffect()
        chat_shadow.setBlurRadius(20)
        chat_shadow.setColor(QColor(0, 0, 0, 30))
        chat_shadow.setOffset(0, 4)
        self.chat_scroll.setGraphicsEffect(chat_shadow)

        main_layout.addWidget(self.chat_scroll, 1)

        # Input area
        input_widget = self._create_input_area()
        main_layout.addWidget(input_widget)

        # Add welcome message
        self._add_welcome_message()

    def _create_header(self) -> QWidget:
        """Create application header"""
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {AppTheme.COLORS['primary']}, stop:1 {AppTheme.COLORS['primary_dark']});
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)

        # App title
        title = QLabel("🍳 Recipe Chat Assistant")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        layout.addStretch()

        # Clear chat button
        clear_button = QPushButton("🗑️ Clear Chat")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        clear_button.clicked.connect(self._clear_chat)
        layout.addWidget(clear_button)

        header.setLayout(layout)
        return header

    def _create_input_area(self) -> QWidget:
        """Create the input area"""
        input_widget = QWidget()
        input_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {AppTheme.COLORS['card_bg']};
                border-radius: 12px;
                padding: 12px;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Input field with enhanced styling
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me about any recipe, ingredient, or cooking technique...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {AppTheme.COLORS['border']};
                border-radius: 24px;
                padding: 12px 20px;
                font-size: 14px;
                background: {AppTheme.COLORS['section_bg']};
            }}
            QLineEdit:focus {{
                border-color: {AppTheme.COLORS['primary']};
                background: white;
            }}
        """)
        self.input_field.returnPressed.connect(self.send_message)

        # Send button with gradient
        self.send_button = QPushButton("Send 📤")
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {AppTheme.COLORS['primary_light']}, stop:1 {AppTheme.COLORS['primary']});
                color: white;
                border: none;
                border-radius: 24px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {AppTheme.COLORS['primary']}, stop:1 {AppTheme.COLORS['primary_dark']});
            }}
            QPushButton:pressed {{
                background: {AppTheme.COLORS['primary_dark']};
            }}
        """)
        self.send_button.clicked.connect(self.send_message)

        layout.addWidget(self.input_field)
        layout.addWidget(self.send_button)

        input_widget.setLayout(layout)

        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, -4)
        input_widget.setGraphicsEffect(shadow)

        return input_widget

    def _add_welcome_message(self):
        """Add welcome message to chat"""
        welcome_text = """Welcome to Recipe Chat Assistant! 👋

I can help you with:
• Creating delicious recipes from ingredients you have
• Step-by-step cooking instructions
• Dietary adaptations (vegan, gluten-free, etc.)
• Nutritional information and healthy alternatives
• Quick meal ideas and meal planning

Just ask me anything about cooking! 🍳"""

        welcome_bubble = MessageBubble(welcome_text, is_user=False)
        self.chat_layout.addWidget(welcome_bubble)

    def _clear_chat(self):
        """Clear all chat messages except welcome"""
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

    def _refresh_models(self):
        """Refresh available models"""
        config = self.settings_panel.get_config()
        if not config:
            return

        try:
            # Create temporary client
            temp_client = APIClient(config)
            models = temp_client.get_available_models()
            self.settings_panel.set_models(models)

            if models:
                QMessageBox.information(self, "Success", f"Found {len(models)} models")
            else:
                QMessageBox.warning(self, "No Models", "No models found. Make sure LM Studio is running.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh models: {str(e)}")

    def _save_settings(self):
        """Save API settings"""
        config = self.settings_panel.get_config()
        if not config:
            return

        self.api_client = APIClient(config)
        QMessageBox.information(self, "Success", "Settings saved successfully!")

        # Collapse settings panel
        self.settings_panel.setChecked(False)

    def send_message(self):
        """Send user message to AI"""
        message = self.input_field.text().strip()
        if not message:
            return

        if not self.api_client:
            QMessageBox.warning(self, "No API Configuration",
                               "Please configure API settings first")
            self.settings_panel.setChecked(True)
            return

        # Clear input
        self.input_field.clear()

        # Add user message to chat
        user_bubble = MessageBubble(message, is_user=True)
        self.chat_layout.addWidget(user_bubble)

        # Add loading indicator
        self.loading_widget = LoadingWidget()
        self.chat_layout.addWidget(self.loading_widget)

        # Scroll to bottom
        QTimer.singleShot(100, self._scroll_to_bottom)

        # Start API call in background
        self.current_worker = APIWorker(self.api_client, message)
        self.current_worker.response_ready.connect(self._handle_response)
        self.current_worker.error_occurred.connect(self._handle_error)
        self.current_worker.start()

    def _handle_response(self, response: str):
        """Handle AI response"""
        # Remove loading indicator
        if hasattr(self, 'loading_widget'):
            self.loading_widget.deleteLater()

        # Parse response
        recipe = self.parser.parse_response(response)

        # Create response widget
        response_widget = self._create_recipe_widget(recipe)
        self.chat_layout.addWidget(response_widget)

        # Scroll to bottom
        QTimer.singleShot(100, self._scroll_to_bottom)

    def _handle_error(self, error: str):
        """Handle API error"""
        # Remove loading indicator
        if hasattr(self, 'loading_widget'):
            self.loading_widget.deleteLater()

        # Create error widget
        error_widget = ErrorWidget(error)
        self.chat_layout.addWidget(error_widget)

        QTimer.singleShot(100, self._scroll_to_bottom)

    def _create_recipe_widget(self, recipe: ParsedRecipe) -> QWidget:
        """Create comprehensive recipe display widget"""
        container = ModernCard()
        container.set_card_style(AppTheme.COLORS['card_bg'])

        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Recipe info card (if we have metadata)
        if any([recipe.name, recipe.description, recipe.prep_time, recipe.cook_time]):
            info_card = RecipeInfoCard(recipe)
            layout.addWidget(info_card)

        # Tags
        if recipe.tags:
            tags_widget = QWidget()
            tags_layout = QHBoxLayout()
            tags_layout.setContentsMargins(0, 0, 0, 0)
            tags_layout.setSpacing(8)
            tags_layout.setAlignment(Qt.AlignLeft)

            for tag in recipe.tags[:8]:  # Limit tags
                badge = TagBadge(tag)
                tags_layout.addWidget(badge)

            tags_widget.setLayout(tags_layout)
            layout.addWidget(tags_widget)

        # Ingredients section
        if recipe.ingredients:
            section_label = self._create_section_label(AppTheme.EMOJIS['ingredients'], "Ingredients")
            layout.addWidget(section_label)

            for ingredient in recipe.ingredients[:20]:  # Limit ingredients
                ing_card = IngredientCard(ingredient)
                layout.addWidget(ing_card)

        # Instructions section
        if recipe.instructions:
            section_label = self._create_section_label(AppTheme.EMOJIS['instructions'], "Instructions")
            layout.addWidget(section_label)

            for i, instruction in enumerate(recipe.instructions[:20], 1):  # Limit instructions
                inst_card = InstructionCard(i, instruction)
                layout.addWidget(inst_card)

        # Tips section
        if recipe.tips:
            section_label = self._create_section_label(AppTheme.EMOJIS['tips'], "Tips & Notes")
            layout.addWidget(section_label)

            for tip in recipe.tips[:5]:  # Limit tips
                tip_card = TipCard(tip)
                layout.addWidget(tip_card)

        # Nutrition section
        if recipe.nutrition:
            section_label = self._create_section_label(AppTheme.EMOJIS['nutrition'], "Nutrition Information")
            layout.addWidget(section_label)

            nutrition_widget = self._create_nutrition_widget(recipe.nutrition)
            layout.addWidget(nutrition_widget)

        container.setLayout(layout)
        return container

    def _create_section_label(self, emoji: str, text: str) -> QLabel:
        """Create a section header label"""
        label = QLabel(f"{emoji} {text}")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        label.setStyleSheet(f"""
            color: {AppTheme.COLORS['primary_dark']};
            margin-top: 8px;
            margin-bottom: 4px;
        """)
        return label

    def _create_nutrition_widget(self, nutrition: Dict[str, str]) -> ModernCard:
        """Create nutrition information widget"""
        card = ModernCard()
        card.set_card_style(AppTheme.COLORS['section_bg'])

        layout = QGridLayout()
        layout.setSpacing(12)

        row = 0
        col = 0
        for key, value in nutrition.items():
            if col >= 3:  # Max 3 columns
                col = 0
                row += 1

            item_label = QLabel(f"<b>{key}:</b> {value}")
            item_label.setFont(QFont("Arial", 10))
            layout.addWidget(item_label, row, col)
            col += 1

        card.setLayout(layout)
        return card

    def _scroll_to_bottom(self):
        """Scroll chat to bottom"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


# ============== Main Entry Point ==============
def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application font
    app.setFont(QFont("Arial", 10))

    # Set application properties
    app.setApplicationName("Recipe Chat Assistant")
    app.setOrganizationName("RecipeAI")

    # Create and show main window
    window = RecipeChatApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
