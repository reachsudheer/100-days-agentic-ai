import json
import re
import streamlit as st
from agent import run_agent, OUTPUT_FILE

st.set_page_config(
    page_title="Smart Recipe Planner",
    page_icon="🍽️",
    layout="wide",
)

# ── Global styles ────────────────────────────────────────────────────────────
st.markdown("""
<style>
.day-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.day-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #f3f4f6;
}
.meal-row {
    background: #f9fafb;
    border-left: 3px solid #6366f1;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 8px;
}
.meal-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.meal-name {
    font-size: 0.95rem;
    font-weight: 500;
    color: #111827;
    margin-top: 2px;
}
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Smart Recipe Planner")
st.caption("Day 002 · 100 Days of Agentic AI · TheMealDB + DeepSeek via OpenRouter")
st.divider()


# ── Parsing helpers ──────────────────────────────────────────────────────────
def extract_meal_table(text: str) -> list[dict]:
    rows = []
    pattern = re.compile(
        r"Day\s*(\d)\s*[|:]\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+)",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        m = pattern.search(line)
        if m:
            rows.append({
                "Day": f"Day {m.group(1)}",
                "Breakfast": m.group(2).strip().strip("*"),
                "Lunch": m.group(3).strip().strip("*"),
                "Dinner": m.group(4).strip().strip("*"),
            })
    return rows


def extract_shopping_list(text: str) -> list[str]:
    items: list[str] = []
    in_section = False
    for line in text.splitlines():
        if re.search(r"shopping list", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            s = line.strip()
            if re.match(r"^[-*•]\s+", s):
                items.append(re.sub(r"^[-*•]\s+", "", s).strip())
            elif re.match(r"^\d+[.)]\s+", s):
                items.append(re.sub(r"^\d+[.)]\s+", "", s).strip())
            elif s == "" and items:
                break
    if not items:
        for line in text.splitlines():
            s = line.strip()
            if re.match(r"^[-*•]\s+", s):
                items.append(re.sub(r"^[-*•]\s+", "", s).strip())
            elif re.match(r"^\d+[.)]\s+", s):
                items.append(re.sub(r"^\d+[.)]\s+", "", s).strip())
    return items


def render_day_cards(rows: list[dict]):
    cols = st.columns(len(rows) or 3)
    meal_icons  = {"Breakfast": "🌅", "Lunch": "☀️", "Dinner": "🌙"}
    colors      = {"Breakfast": "#f59e0b", "Lunch": "#10b981", "Dinner": "#6366f1"}
    for col, row in zip(cols, rows):
        with col:
            meals_html = "".join(
                f"""<div class="meal-row" style="border-left-color:{colors[slot]}">
                        <div class="meal-label">{meal_icons[slot]} {slot}</div>
                        <div class="meal-name">{row.get(slot, '—')}</div>
                    </div>"""
                for slot in ("Breakfast", "Lunch", "Dinner")
            )
            st.markdown(
                f'<div class="day-card">'
                f'<div class="day-title">📅 {row["Day"]}</div>'
                f'{meals_html}</div>',
                unsafe_allow_html=True,
            )


def render_shopping_list(items: list[str]):
    st.markdown(
        f"<p style='color:#6b7280;font-size:0.85rem'>"
        f"{len(items)} item{'s' if len(items) != 1 else ''} to buy</p>",
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    mid = (len(items) + 1) // 2
    for i, item in enumerate(items):
        (col1 if i < mid else col2).checkbox(item, key=f"shop_{i}")


# ── UI Layout ────────────────────────────────────────────────────────────────
c1, c2 = st.columns([2, 1])
with c1:
    ingredients = st.text_area(
        "What ingredients do you have?",
        placeholder="e.g. chicken, garlic, tomatoes, pasta, onion",
        height=110,
    )
with c2:
    preferences = st.text_input(
        "Dietary preferences / restrictions",
        placeholder="e.g. vegetarian, gluten-free, none",
    )
    st.write("")
    generate = st.button("🍳 Generate Meal Plan", use_container_width=True, type="primary")

st.divider()

if generate:
    if not ingredients.strip():
        st.warning("Please enter at least one ingredient.")
        st.stop()

    st.markdown("#### 🧠 Progress")
    log_ph = st.empty()
    spinner_ph = st.empty()
    steps: list[str] = []

    def on_step(msg: str):
        steps.append(msg)
        log_ph.markdown("\n\n".join(steps))
        # show a spinner only during the slow LLM call
        if "Sending" in msg:
            spinner_ph.info("⏳ AI is building your meal plan… this takes ~20–40 seconds with a free model.")
        elif "Done" in msg:
            spinner_ph.empty()

    result = ""
    try:
        result = run_agent(ingredients.strip(), preferences.strip(), on_step=on_step)
        OUTPUT_FILE.write_text(result, encoding="utf-8")
    except ValueError as ve:
        st.error(str(ve))
        st.stop()
    except Exception as e:
        err = str(e)
        if "rate" in err.lower() or "429" in err:
            st.error("OpenRouter rate limit hit. Wait a moment then try again.")
        else:
            st.error(f"Unexpected error: {err}")
        st.stop()

    st.divider()

    # ── 3-Day Meal Plan ───────────────────────────────────────────────────────
    st.subheader("📅 Your 3-Day Meal Plan")
    rows = extract_meal_table(result)
    if rows:
        render_day_cards(rows)
    else:
        plan_lines = [
            ln for ln in result.splitlines()
            if re.search(r"day\s*[123]|breakfast|lunch|dinner", ln, re.IGNORECASE)
        ]
        st.markdown("\n".join(plan_lines) if plan_lines else result)

    st.divider()

    # ── Shopping List ─────────────────────────────────────────────────────────
    st.subheader("🛒 Shopping List")
    items = extract_shopping_list(result)
    if items:
        render_shopping_list(items)
    else:
        idx = result.lower().find("shopping list")
        st.markdown(result[idx:] if idx != -1 else "_No shopping list found in response._")

    st.divider()
    st.caption(f"Meal plan saved to `{OUTPUT_FILE}`")
    with st.expander("📄 Full AI Response (raw)"):
        st.text(result)
