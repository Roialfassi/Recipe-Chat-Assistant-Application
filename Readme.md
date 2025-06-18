# 🥘 Recipe Chat Assistant

A **modern, chat‑style desktop application** that lets you converse naturally with an AI about cooking, recipes, and food preparation.  Built with **Python3.8+** and **PyQt5**, it supports both **OpenAI** and **LM Studio** models and renders beautifully parsed, interactive answers.

---

## ✨ Key Features

| Category                    | Highlights                                                                                                               |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Conversational UI**       | Sleek chat interface with message bubbles, typing indicators, and rich recipe widgets                                    |
| **Dual Model Support**      | Seamlessly switch between OpenAI LMStudio — or type any custom LM Studio model name                                   |
| **Structured JSON Replies** | Prompts request recipes in JSON; the parser extracts & validates even if the LLM adds extra commentary                   |
| **Smart Parsing Engine**    | Handles wildly formatted ingredient lines, creates tags automatically, and falls back to plain‑text when JSON is missing |
| **Theme System**            | Centralised `AppTheme` guarantees a consistent dark/light look across all widgets                                        |
| **Threaded API Calls**      | Background threads keep the UI responsive while the LLM thinks                                                           |
| **Robust Error Handling**   | Connection checks, detailed pop‑ups, and graceful fallbacks throughout the stack                                         |


### Module Breakdown

| File                | Responsibility                                                                                                                                                                                                                                      |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`models.py`**     | • `APIConfig`, `ParsedRecipe`, and other data models  <br>• Central `AppTheme` (fonts, colours, spacing)  <br>• Enums / constants for message roles, cuisines, etc.                                                                                 |
| **`parser.py`**     | • Extracts JSON embedded in text  <br>• Validates & converts to `ParsedRecipe`  <br>• Accepts messy inputs ("2 Tbsp olive‑oil", "½ cup milk")  <br>• Auto‑generates keyword tags                                                                    |
| **`api_client.py`** | • One class, two engines: OpenAI/LM Studio  <br>• Adds system prompts requesting *strict JSON*  <br>• Timeout & retry logic, HTTP/WS support  <br>• `verify_connection()` utility                                                                 |
| **`widgets.py`**    | • `ModernCard` base with rounded corners & shadow  <br>• Recipe widgets: ingredients grid, step‑by‑step view, chef‑tips  <br>• Chat components: user/assistant bubbles, loading dots, error boxes  <br>• `SettingsPanel` with free‑text model field |
| **`main.py`**       | • Builds the window & navbar  <br>• Manages chat history & scrollbar  <br>• Spawns worker threads for each API call  <br>• Handles drag‑drop of ingredient lists                                                                                    |

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
$ git clone https://github.com/Roialfassi/Recipe-Chat-Assistant-Application.git
$ cd recipe‑chat‑assistant

# 2. Create & activate a virtual environment
$ python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. Run the app
$ python main.py

# add the api key the model and provider you want to use and start getting recipes
```

> **Tip:** In *SettingsModels* you can pick *gpt‑4o*, *phi‑3‑mini‑128k*, or type any custom LM Studio model identifier.


The UI’s *Settings Panel* updates these values live and writes back to the file.

---

## 🤖 Prompt Format

The assistant requests recipes in a strict JSON envelope to simplify parsing:

```jsonc
{
  "title": "Spaghetti Carbonara",
  "servings": 4,
  "ingredients": [
    "200 g spaghetti",
    "100 g pancetta, diced",
    "2 eggs",
    "50 g grated parmesan",
    "1 Tbsp olive oil",
    "Salt & freshly ground pepper"
  ],
  "instructions": [
    "Cook spaghetti until al dente.",
    "Fry pancetta until crispy.",
    "Whisk eggs and parmesan together.",
    "Combine drained pasta with pancetta, remove heat, stir in egg mixture.",
    "Season and serve immediately."
  ],
  "tags": ["italian", "quick", "comfort‑food"]
}
```

The *parser* falls back to free‑text rendering if valid JSON is absent.

---

## 🛣️ Roadmap

* [ ] Image support (inline step photos)
* [ ] Voice input & TTS cooking mode
* [ ] Cloud‑sync of favourite recipes
* [ ] Plugin system for grocery‑list export

---

## 👫 Contributing

1. **Fork** the repository and create a branch (`feat/awesome‑thing`).
2. Ensure code passes **ruff** / **black** style checks: `make format`.
3. Submit a **pull request** – describe what your change improves.

All contributors agree to follow the Contributor Covenant

---

## 📜 License

Distributed under the **MIT License**.  See `LICENSE` for details.

---

## 🙏 Acknowledgements

* [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework.
* [OpenAI Python SDK](https://github.com/openai/openai-python) for API access.
* [LM Studio](https://lmstudio.ai) for local model serving.

Bon appétit
