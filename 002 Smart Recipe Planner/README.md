# 🍽️ Smart Recipe Planner

> **Day 002 of [100 Days of Agentic AI](https://github.com/100-days-agentic-ai)**

An agentic AI app that takes your available ingredients and dietary preferences, searches real recipes, and generates a personalised 3-day meal plan with a consolidated shopping list — all powered by free tools.

---

## ✨ Features

- 🔍 **Live recipe search** via [TheMealDB](https://www.themealdb.com/) (free, no API key needed)
- 🧠 **AI meal planning** using a single LLM call (DeepSeek via OpenRouter free tier)
- 📅 **3-day meal plan** displayed as visual day cards (Breakfast / Lunch / Dinner)
- 🛒 **Shopping list** as an interactive 2-column checklist
- ⚡ **Fast** — API lookups in Python (no agent loop), one LLM call (~20–40 sec total)
- 💰 **Zero cost** — free model, free recipe API, local Streamlit UI

---

## 🖥️ Demo

```
Ingredients:  chicken, butter
Preferences:  none

→ Searches TheMealDB for each ingredient
→ Fetches details for top recipes
→ Sends all recipes to DeepSeek in one call
→ Returns 3-day plan + shopping list
```

**Output:**

| Day | Breakfast | Lunch | Dinner |
|-----|-----------|-------|--------|
| Day 1 | Chicken Congee | Brown Stew Chicken | Butter Chicken |
| Day 2 | Chicken & Chorizo Rice Pot | Chicken Hotpot | Chicken Fajitas |
| Day 3 | Brown Stew Chicken | Butter Chicken | Chicken Congee |

---

## 🗂️ Project Structure

```
002 Smart Recipe Planner/
├── app.py            # Streamlit UI — inputs, progress log, day cards, shopping list
├── agent.py          # Pipeline — TheMealDB search → recipe collect → LLM plan
├── tools.py          # TheMealDB HTTP client + LangChain @tool wrappers
├── create_docs.py    # Generates Smart_Recipe_Planner_Docs.pdf
├── requirements.txt  # Pinned Python dependencies
├── .env              # Your API key (not committed)
├── .env.example      # Template to copy
└── meal_plan.txt     # Last generated meal plan (auto-saved)
```

---

## 🛠️ Tech Stack

| Layer | Tool | Cost |
|-------|------|------|
| UI | [Streamlit](https://streamlit.io/) | Free |
| LLM client | [LangChain](https://python.langchain.com/) + `langchain-openai` | Free |
| LLM gateway | [OpenRouter](https://openrouter.ai/) | Free tier |
| LLM model | `deepseek/deepseek-v4-flash:free` | Free |
| Recipe data | [TheMealDB API](https://www.themealdb.com/api.php) | Free, no key |
| Language | Python 3.11+ | Free |

---

## 🚀 Getting Started

### 1. Clone / navigate to the project

```powershell
cd "D:\100 Agents\002 Smart Recipe Planner"
```

### 2. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Set up your API key

Get a **free** OpenRouter key at <https://openrouter.ai> (takes ~2 minutes).

```powershell
copy .env.example .env
# Open .env and paste your key
```

`.env` contents:

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=deepseek/deepseek-v4-flash:free
```

### 5. Run the app

```powershell
streamlit run app.py
```

Open <http://localhost:8501> in your browser.

---

## 💡 Usage

1. Enter ingredients you have (comma-separated): `chicken, garlic, tomatoes`
2. Enter dietary preferences (or leave blank): `vegetarian` / `gluten-free` / `none`
3. Click **Generate Meal Plan**
4. Watch the progress steps appear live
5. View your 3-day meal plan cards and interactive shopping checklist

---

## ⚙️ How It Works

The app uses a **two-phase pipeline** instead of a slow ReAct agent loop:

```
Phase 1 — Recipe Collection (pure Python, no LLM)
  For each ingredient:
    → GET themealdb.com/filter.php?i={ingredient}   # search
    → GET themealdb.com/lookup.php?i={meal_id}      # fetch top 2 details

Phase 2 — AI Planning (single LLM call)
  → Send all collected recipes to DeepSeek
  → Receive: 3-day meal plan table + shopping list
  → Parse + render in Streamlit
```

This approach makes **one LLM call** instead of 6–12, cutting wait time from 3–5 minutes to under 40 seconds.

---

## 🔄 Switching Models

Edit `OPENROUTER_MODEL` in `.env` — no code change or restart needed:

```env
# Currently active free models on OpenRouter (May 2026):
OPENROUTER_MODEL=deepseek/deepseek-v4-flash:free
# OPENROUTER_MODEL=google/gemma-4-31b-it:free
# OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
# OPENROUTER_MODEL=google/gemma-4-26b-a4b-it:free
```

Check the live list: <https://openrouter.ai/models?q=:free>

---

## 🐛 Troubleshooting

| Error | Fix |
|-------|-----|
| `No endpoints found for <model>` | Model removed from OpenRouter — change `OPENROUTER_MODEL` in `.env` |
| `OPENROUTER_API_KEY is not set` | Create `.env` from `.env.example` and add your key |
| `No results for <ingredient>` | Use common English names: `chicken` not `pollo`, `pasta` not `spaghetti` |
| `Could not find any recipes` | All ingredients failed search — check internet connection |
| Rate limit / 429 | Wait 60 seconds; free tier allows ~20 req/min |
| Meal plan shows raw text | Model ignored format — click Generate again or switch model |

---

## 📄 Documentation

For a full in-depth code walkthrough, generate the PDF:

```powershell
pip install fpdf2
python create_docs.py
# Opens: Smart_Recipe_Planner_Docs.pdf
```

Covers: architecture, data flow diagram, every function explained, error reference.

---

## 🗺️ Roadmap / Ideas

- [ ] Cache TheMealDB results to avoid duplicate API calls
- [ ] Add cuisine filter (Italian / Indian / Mexican)
- [ ] Export meal plan as PDF or image
- [ ] Save favourite meal plans across sessions
- [ ] Add nutritional info from a nutrition API

---

## 📁 Part of 100 Days of Agentic AI

| Day | Project | Stack |
|-----|---------|-------|
| 001 | Personal Email Assistant | GPT-4o-mini + LangChain |
| **002** | **Smart Recipe Planner** | **DeepSeek + LangChain + TheMealDB + Streamlit** |
| 003 | Coming soon… | — |

---

## 📜 License

MIT — free to use, modify, and share.
