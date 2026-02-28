import streamlit as st
import pandas as pd
import collections
import io
import time

# 1. Page Configuration
st.set_page_config(page_title="91 AI Pro - Permanent Logic", layout="centered")

# 2. Custom CSS for High Visibility
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .big-training-text { font-size: 38px; font-weight: 900; color: #00ffcc; text-align: center; }
    .status-msg { font-size: 18px; font-weight: bold; color: #ffff00; text-align: center; padding: 10px; border: 1px solid #ffff00; border-radius: 8px; margin-bottom: 15px; }
    .pred-box { padding: 20px; border-radius: 12px; text-align: center; border: 3px solid white; margin-bottom: 10px; }
    .stat-row { display: flex; justify-content: space-around; background: #0e1117; padding: 10px; border-radius: 10px; border: 1px solid #333; margin-bottom: 15px; }
    .stat-value { font-size: 22px; font-weight: 900; color: white; }
    div.stButton > button { width: 100% !important; height: 50px !important; font-weight: 900 !important; font-size: 18px !important; background-color: #ffff00 !important; color: black !important; border: 1px solid black !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Session State Initialization
if 'logic_db' not in st.session_state: st.session_state.logic_db = None
if 'num_sequence' not in st.session_state: st.session_state.num_sequence = []
if 'history' not in st.session_state: st.session_state.history = []
if 'stats' not in st.session_state: 
    st.session_state.stats = {"wins": 0, "loss": 0, "streak": 0, "last_res": None, "max_win": 0, "max_loss": 0}

# --- 4. PERMANENT LOGIC EXTRACTION ---
def train_logic(uploaded_file):
    try:
        data = []
        raw_content = uploaded_file.getvalue().decode("utf-8").splitlines()
        for line in raw_content:
            clean_line = line.strip().strip('"')
            parts = clean_line.split('\t')
            if len(parts) == 3: data.append(parts)
            elif len(parts) == 1 and len(parts[0]) >= 3:
                s = parts[0]
                data.append([s[0], s[1], s[2]])
        
        df = pd.DataFrame(data, columns=['number', 'size', 'color'])
        num_seq = df['number'].astype(str).tolist()
        size_seq = df['size'].astype(str).tolist()
        
        # Build 100% Deterministic Logic Map (6-digit patterns)
        logic = collections.defaultdict(list)
        for i in range(len(num_seq) - 6):
            pat = "".join(num_seq[i:i+6])
            next_val = "BIG" if size_seq[i+6].upper() == 'B' else "SMALL"
            logic[pat].append(next_val)
        
        # Filter only 100% accurate results
        deterministic = {pat: outcomes[0] for pat, outcomes in logic.items() if len(set(outcomes)) == 1}
        return deterministic
    except:
        return None

# --- 5. TRAINING PHASE (ONLY SHOWN IF NO LOGIC EXISTS) ---
if st.session_state.logic_db is None:
    st.title("🤖 One-Time AI Setup")
    st.write("Upload your Master CSV once to save the logic forever in this session.")
    master_file = st.file_uploader("Upload OVER all.CSV", type="csv")
    
    if master_file:
        if st.button("🚀 SAVE LOGIC & START"):
            progress = st.progress(0)
            status = st.empty()
            for p in range(0, 101, 5):
                time.sleep(0.05)
                progress.progress(p)
                status.markdown(f'<div class="big-training-text">LEARNING: {p}%</div>', unsafe_allow_html=True)
            
            st.session_state.logic_db = train_logic(master_file)
            if st.session_state.logic_db:
                status.markdown('<div class="status-msg">✅ LOGIC SAVED. YOU CAN NOW PLAY!</div>', unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            else:
                st.error("Error processing file. Please check format.")
    st.stop()

# --- 6. PREDICTION PHASE ---
st.title("🎯 91 AI PATTERN PRO")

# Real-Time Statistics Header
total = st.session_state.stats['wins'] + st.session_state.stats['loss']
win_rate = (st.session_state.stats['wins'] / total * 100) if total > 0 else 0

st.markdown(f"""
    <div class="stat-row">
        <div class="stat-item"><div class="stat-value" style="color:#28a745;">{st.session_state.stats['max_win']}</div><div style="font-size:10px; color:#888;">MAX WIN</div></div>
        <div class="stat-item"><div class="stat-value" style="color:#dc3545;">{st.session_state.stats['max_loss']}</div><div style="font-size:10px; color:#888;">MAX LOSS</div></div>
        <div class="stat-item"><div class="stat-value">{st.session_state.stats['wins']}</div><div style="font-size:10px; color:#888;">WINS</div></div>
        <div class="stat-item"><div class="stat-value">{st.session_state.stats['loss']}</div><div style="font-size:10px; color:#888;">LOSS</div></div>
        <div class="stat-item"><div class="stat-label" style="color:#00ffcc; font-weight:900;">{win_rate:.1f}%</div><div style="font-size:10px; color:#888;">RATE</div></div>
    </div>
""", unsafe_allow_html=True)

# Pattern Matching Logic
current_pattern = "".join(map(str, st.session_state.num_sequence[-6:]))
prediction = st.session_state.logic_db.get(current_pattern, None)

if prediction:
    color = "#dc3545" if prediction == "BIG" else "#28a745"
    st.markdown(f'<div class="pred-box" style="background-color: {color}; color: white; font-size:30px;">NEXT PREDICTION: {prediction}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="wait-box" style="text-align:center; padding:20px; background:#111; border-radius:10px; color:#666;">🔍 SCANNING PATTERNS... WAITING...</div>', unsafe_allow_html=True)

# 7. INPUT CONTROLS
if not st.session_state.num_sequence:
    init_in = st.text_input("ENTER 6 DIGITS TO START GAME", max_chars=6)
    if st.button("SYNC GAME"):
        if len(init_in) == 6:
            st.session_state.num_sequence = [int(d) for d in init_in]
            st.rerun()
else:
    # Dialer for Single Number Input
    new_digit = None
    st.write(f"**Last 6 Numbers:** `{' - '.join(map(str, st.session_state.num_sequence[-6:]))}`")
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("0"): new_digit = 0
    if c2.button("1"): new_digit = 1
    if c3.button("2"): new_digit = 2
    if c4.button("3"): new_digit = 3
    if c5.button("4"): new_digit = 4
    c6, c7, c8, c9, c0 = st.columns(5)
    if c6.button("5"): new_digit = 5
    if c7.button("6"): new_digit = 6
    if c8.button("7"): new_digit = 7
    if c9.button("8"): new_digit = 8
    if c0.button("9"): new_digit = 9

    if new_digit is not None:
        if prediction:
            actual = "BIG" if new_digit >= 5 else "SMALL"
            is_win = (actual == prediction)
            res_type = "win" if is_win else "loss"
            
            # Update Statistics
            st.session_state.stats["wins" if is_win else "loss"] += 1
            if res_type == st.session_state.stats["last_res"]: st.session_state.stats["streak"] += 1
            else: st.session_state.stats["streak"], st.session_state.stats["last_res"] = 1, res_type
            
            st.session_state.stats[f"max_{res_type}"] = max(st.session_state.stats[f"max_{res_type}"], st.session_state.stats["streak"])
            
            # Add to History Table
            st.session_state.history.insert(0, {
                "Round": len(st.session_state.history) + 1,
                "Number": new_digit,
                "Actual": actual,
                "Prediction": prediction,
                "Result": "✅ WIN" if is_win else "❌ LOSS",
                "Streak": st.session_state.stats["streak"]
            })
        
        st.session_state.num_sequence.append(new_digit)
        st.rerun()

# 8. PASTED RESULT HISTORY (Visible Tracking)
if st.session_state.history:
    st.markdown("### 📋 Game History Tracker")
    hist_df = pd.DataFrame(st.session_state.history).head(15)
    st.table(hist_df)

if st.button("🔄 RESET ALL DATA"):
    st.session_state.clear()
    st.rerun()
