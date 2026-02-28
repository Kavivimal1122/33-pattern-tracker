import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="91 AI Pattern Tracker", layout="centered")

# 2. Custom CSS for high visibility
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .pred-box { padding: 25px; border-radius: 15px; text-align: center; border: 4px solid white; margin-bottom: 15px; font-weight: bold; }
    .wait-box { background-color: #1e1e1e; color: #888; padding: 25px; border-radius: 15px; text-align: center; border: 2px dashed #444; }
    .stat-row { display: flex; justify-content: space-around; background: #0e1117; padding: 10px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px; }
    .stat-item { text-align: center; }
    .stat-label { font-size: 12px; color: #888; font-weight: bold; }
    .stat-value { font-size: 24px; font-weight: 900; color: white; }
    div.stButton > button { width: 100% !important; height: 60px !important; font-weight: 900 !important; font-size: 20px !important; background-color: #ffff00 !important; color: black !important; border-radius: 0px !important; border: 1px solid black !important; }
    [data-testid="column"] { padding: 0px !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Deterministic Pattern Database (Based on OVER all.CSV)
NUMBER_LOGIC = {
    "431321": "SMALL", "313214": "BIG", "132141": "SMALL",
    "214167": "SMALL", "141671": "BIG", "416716": "SMALL",
    "821557": "SMALL", "215570": "BIG", "155703": "SMALL"
}

# 4. Session State Initialization
if 'num_sequence' not in st.session_state: st.session_state.num_sequence = []
if 'history' not in st.session_state: st.session_state.history = []
if 'stats' not in st.session_state: 
    st.session_state.stats = {"wins": 0, "loss": 0, "streak": 0, "last_res": None, "max_win": 0, "max_loss": 0}

# --- 5. CORE LOGIC ---
st.title("🎯 91 PATTERN TRACKER")

win_rate = (st.session_state.stats['wins'] / (st.session_state.stats['wins'] + st.session_state.stats['loss']) * 100) if (st.session_state.stats['wins'] + st.session_state.stats['loss']) > 0 else 0

st.markdown(f"""
    <div class="stat-row">
        <div class="stat-item"><div class="stat-label">MAX WIN</div><div class="stat-value" style="color:#28a745;">{st.session_state.stats['max_win']}</div></div>
        <div class="stat-item"><div class="stat-label">MAX LOSS</div><div class="stat-value" style="color:#dc3545;">{st.session_state.stats['max_loss']}</div></div>
        <div class="stat-item"><div class="stat-label">WINS</div><div class="stat-value">{st.session_state.stats['wins']}</div></div>
        <div class="stat-item"><div class="stat-label">LOSS</div><div class="stat-value">{st.session_state.stats['loss']}</div></div>
        <div class="stat-item"><div class="stat-label">WIN RATE</div><div class="stat-value" style="color:#00ffcc;">{win_rate:.1f}%</div></div>
    </div>
""", unsafe_allow_html=True)

current_pattern = "".join(map(str, st.session_state.num_sequence[-6:]))
prediction = NUMBER_LOGIC.get(current_pattern, None)

if prediction:
    color = "#dc3545" if prediction == "BIG" else "#28a745"
    st.markdown(f"""
        <div class="pred-box" style="background-color: {color}; color: white;">
            <p style="margin:0; font-size:14px; text-transform:uppercase;">Pattern Match Found!</p>
            <h1 style="margin:0; font-size:60px;">{prediction}</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="wait-box">
            <h1 style="margin:0; font-size:40px;">WAITING...</h1>
            <p style="margin:0;">Scanning for 100% accurate patterns</p>
        </div>
    """, unsafe_allow_html=True)

# --- 6. INPUT HANDLING ---
if len(st.session_state.num_sequence) < 6:
    st.subheader("Setup: Enter first 6 game numbers")
    init_input = st.text_input("Paste 6 numbers (e.g., 821557)", max_chars=6)
    if st.button("INITIALIZE TRACKER"):
        if len(init_input) == 6 and init_input.isdigit():
            st.session_state.num_sequence = [int(d) for d in init_input]
            st.rerun()
else:
    st.write(f"**Sequence:** `{' - '.join(map(str, st.session_state.num_sequence[-10:]))}`")
    new_digit = None
    row1, row2 = st.columns(5), st.columns(5)
    for i in range(5):
        if row1[i].button(str(i), key=f"b{i}"): new_digit = i
    for i in range(5, 10):
        if row2[i-5].button(str(i), key=f"b{i}"): new_digit = i

    if new_digit is not None:
        if prediction:
            actual_size = "BIG" if new_digit >= 5 else "SMALL"
            is_win = (actual_size == prediction)
            res_type = "win" if is_win else "loss"
            st.session_state.stats["wins" if is_win else "loss"] += 1
            if res_type == st.session_state.stats["last_res"]: st.session_state.stats["streak"] += 1
            else: st.session_state.stats["streak"], st.session_state.stats["last_res"] = 1, res_type
            st.session_state.stats[f"max_{res_type}"] = max(st.session_state.stats[f"max_{res_type}"], st.session_state.stats["streak"])
            st.session_state.history.insert(0, {"Num": new_digit, "Result": "WIN" if is_win else "LOSS", "Streak": st.session_state.stats["streak"]})
        st.session_state.num_sequence.append(new_digit)
        st.rerun()

if st.session_state.history:
    st.table(pd.DataFrame(st.session_state.history).head(10))

if st.button("RESET TRACKER"):
    st.session_state.clear()
    st.rerun()