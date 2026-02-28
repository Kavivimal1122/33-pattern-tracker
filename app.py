import streamlit as st
import pandas as pd
import collections
import io
import os
import time

# 1. Page Configuration
st.set_page_config(page_title="91 AI Pattern Tracker", layout="centered")

# 2. Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .big-training-text { font-size: 40px; font-weight: 900; color: #00ffcc; text-align: center; margin-bottom: 10px; }
    .action-call { font-size: 20px; font-weight: bold; color: #ffff00; text-align: center; padding: 10px; border: 2px solid #ffff00; border-radius: 10px; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .pred-box { padding: 25px; border-radius: 15px; text-align: center; border: 4px solid white; margin-bottom: 15px; font-weight: bold; }
    .stat-row { display: flex; justify-content: space-around; background: #0e1117; padding: 10px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px; }
    .stat-value { font-size: 24px; font-weight: 900; color: white; }
    div.stButton > button { width: 100% !important; height: 60px !important; font-weight: 900 !important; font-size: 20px !important; background-color: #ffff00 !important; color: black !important; border: 1px solid black !important; }
    .history-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Session State Initialization
if 'logic_db' not in st.session_state: st.session_state.logic_db = {}
if 'num_sequence' not in st.session_state: st.session_state.num_sequence = []
if 'history' not in st.session_state: st.session_state.history = []
if 'stats' not in st.session_state: 
    st.session_state.stats = {"wins": 0, "loss": 0, "streak": 0, "last_res": None, "max_win": 0, "max_loss": 0}

# --- 4. DATA PROCESSING ---
def extract_logic_from_csv(uploaded_file):
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
        if not data: return None, "Error: No valid data."
        df = pd.DataFrame(data, columns=['number', 'size', 'color'])
        num_seq = df['number'].astype(str).tolist()
        size_seq = df['size'].astype(str).tolist()
        logic = collections.defaultdict(list)
        for i in range(len(num_seq) - 6):
            pat = "".join(num_seq[i:i+6])
            next_val = "BIG" if size_seq[i+6].upper() == 'B' else "SMALL"
            logic[pat].append(next_val)
        deterministic = {pat: outcomes[0] for pat, outcomes in logic.items() if len(set(outcomes)) == 1}
        return deterministic, None
    except Exception as e: return None, str(e)

# --- 5. TRAINING PHASE ---
if not st.session_state.logic_db:
    st.title("🤖 AI Pattern Training")
    master_file = st.file_uploader("Upload Master CSV", type="csv")
    if master_file:
        if st.button("🚀 START TRAINING"):
            window = st.empty()
            progress_bar = st.progress(0)
            for p in range(0, 101, 5):
                time.sleep(0.02); progress_bar.progress(p)
                window.markdown(f'<div class="big-training-text">LEARNING: {p}%</div>', unsafe_allow_html=True)
            db, err = extract_logic_from_csv(master_file)
            if err: st.error(err)
            else:
                st.session_state.logic_db = db
                window.markdown('<div class="big-training-text" style="color:#28a745;">COMPLETED!</div>', unsafe_allow_html=True)
                st.rerun()
    st.stop()

# --- 6. PREDICTION PHASE ---
st.title("🎯 91 PATTERN TRACKER")

# Statistics
total = st.session_state.stats['wins'] + st.session_state.stats['loss']
win_rate = (st.session_state.stats['wins'] / total * 100) if total > 0 else 0
st.markdown(f"""
    <div class="stat-row">
        <div class="stat-item"><div class="stat-value" style="color:#28a745;">{st.session_state.stats['max_win']}</div><div style="font-size:10px; color:#888;">MAX WIN</div></div>
        <div class="stat-item"><div class="stat-value" style="color:#dc3545;">{st.session_state.stats['max_loss']}</div><div style="font-size:10px; color:#888;">MAX LOSS</div></div>
        <div class="stat-item"><div class="stat-value" style="color:#00ffcc;">{win_rate:.1f}%</div><div style="font-size:10px; color:#888;">WIN RATE</div></div>
    </div>
""", unsafe_allow_html=True)

# Pattern Logic
current_pattern = "".join(map(str, st.session_state.num_sequence[-6:]))
prediction = st.session_state.logic_db.get(current_pattern, None)

if prediction:
    color = "#dc3545" if prediction == "BIG" else "#28a745"
    st.markdown(f'<div class="pred-box" style="background-color: {color}; color: white; font-size:40px;">NEXT: {prediction}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="wait-box" style="text-align:center; padding:20px; background:#111; border-radius:10px; color:#555; font-size:20px; font-weight:bold;">🔍 WAITING FOR PATTERN...</div>', unsafe_allow_html=True)

# Input Controls
if len(st.session_state.num_sequence) < 6:
    init_input = st.text_input("ENTER 6 DIGITS TO START", max_chars=6)
    if st.button("INITIALIZE"):
        if len(init_input) == 6:
            st.session_state.num_sequence = [int(d) for d in init_input]
            st.rerun()
else:
    new_digit = None
    cols1 = st.columns(5)
    for i in range(5):
        if cols1[i].button(str(i), key=f"btn_{i}"): new_digit = i
    cols2 = st.columns(5)
    for i in range(5, 10):
        if cols2[i-5].button(str(i), key=f"btn_{i}"): new_digit = i

    if new_digit is not None:
        actual = "BIG" if new_digit >= 5 else "SMALL"
        result_status = "-"
        
        # Update Stats if there was a prediction
        if prediction:
            is_win = (actual == prediction)
            res_type = "win" if is_win else "loss"
            result_status = "✅ WIN" if is_win else "❌ LOSS"
            st.session_state.stats["wins" if is_win else "loss"] += 1
            if res_type == st.session_state.stats["last_res"]: st.session_state.stats["streak"] += 1
            else: st.session_state.stats["streak"], st.session_state.stats["last_res"] = 1, res_type
            st.session_state.stats[f"max_{res_type}"] = max(st.session_state.stats[f"max_{res_type}"], st.session_state.stats["streak"])
        
        # ADD TO HISTORY (Every time a button is pressed)
        st.session_state.history.insert(0, {
            "Round": len(st.session_state.history) + 1,
            "Number": new_digit,
            "Actual": actual,
            "AI Prediction": prediction if prediction else "WAIT",
            "Result": result_status
        })
        
        st.session_state.num_sequence.append(new_digit)
        st.rerun()

# --- 7. GAME HISTORY TABLE ---
if st.session_state.history:
    st.markdown("### 📋 LIVE GAME HISTORY")
    # Display as a clean table
    df_history = pd.DataFrame(st.session_state.history)
    st.table(df_history.head(15)) # Shows last 15 entries

# --- 8. BATCH EVALUATION ---
st.markdown("---")
st.subheader("📊 BATCH ANALYSIS")
up_file = st.file_uploader("Upload CSV for 500 Round Report", type="csv")
if up_file and st.button("🚀 RUN BATCH"):
    df_ev = pd.read_csv(up_file).head(500)
    if 'number' in df_ev.columns:
        e_results, t_seq = [], []
        for i, row in df_ev.iterrows():
            n = str(row['number'])
            if len(t_seq) >= 6:
                key = "".join(t_seq[-6:])
                p = st.session_state.logic_db.get(key, None)
                if p:
                    act = "BIG" if int(n) >= 5 else "SMALL"
                    res = "WIN" if act == p else "LOSS"
                    e_results.append({"Round": i+1, "Pattern": key, "Pred": p, "Actual": act, "Status": res})
            t_seq.append(n)
        if e_results:
            st.success("Analysis Complete")
            st.download_button("📥 DOWNLOAD REPORT", pd.DataFrame(e_results).to_csv(index=False), "report.csv", "text/csv")
    else: st.error("CSV must have 'number' column")

if st.button("🔄 FULL SYSTEM RESET"):
    st.session_state.clear()
    st.rerun()
