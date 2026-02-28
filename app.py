import streamlit as st
import pandas as pd
import io

# 1. Page Configuration
st.set_page_config(page_title="91 Pattern Tracker Pro", layout="centered")

# 2. Custom CSS (Visual Reference Style)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .pred-box { padding: 25px; border-radius: 15px; text-align: center; border: 4px solid white; margin-bottom: 15px; font-weight: bold; }
    .wait-box { background-color: #1e1e1e; color: #888; padding: 25px; border-radius: 15px; text-align: center; border: 2px dashed #444; }
    .stat-row { display: flex; justify-content: space-around; background: #0e1117; padding: 10px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px; }
    .stat-item { text-align: center; }
    .stat-label { font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase; }
    .stat-value { font-size: 24px; font-weight: 900; color: white; }
    div.stButton > button { width: 100% !important; height: 60px !important; font-weight: 900 !important; font-size: 20px !important; background-color: #ffff00 !important; color: black !important; border: 1px solid black !important; }
    .eval-section { background-color: #111; padding: 20px; border-radius: 10px; border: 1px solid #444; margin-top: 30px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Pattern Logic (Exact 100% Deterministic Matches)
NUMBER_LOGIC = {
    "431321": "SMALL", "313214": "BIG", "132141": "SMALL",
    "214167": "SMALL", "141671": "BIG", "416716": "SMALL",
    "821557": "SMALL", "215570": "BIG", "155703": "SMALL"
}

# 4. Session State
if 'num_sequence' not in st.session_state: st.session_state.num_sequence = []
if 'history' not in st.session_state: st.session_state.history = []
if 'stats' not in st.session_state: 
    st.session_state.stats = {"wins": 0, "loss": 0, "streak": 0, "last_res": None, "max_win": 0, "max_loss": 0}

# --- 5. MAIN TRACKER UI ---
st.title("🎯 91 PATTERN TRACKER")

total = st.session_state.stats['wins'] + st.session_state.stats['loss']
win_rate = (st.session_state.stats['wins'] / total * 100) if total > 0 else 0

st.markdown(f"""
    <div class="stat-row">
        <div class="stat-item"><div class="stat-label">MAX WIN</div><div class="stat-value" style="color:#28a745;">{st.session_state.stats['max_win']}</div></div>
        <div class="stat-item"><div class="stat-label">MAX LOSS</div><div class="stat-value" style="color:#dc3545;">{st.session_state.stats['max_loss']}</div></div>
        <div class="stat-item"><div class="stat-label">WINS</div><div class="stat-value">{st.session_state.stats['wins']}</div></div>
        <div class="stat-item"><div class="stat-label">LOSS</div><div class="stat-value">{st.session_state.stats['loss']}</div></div>
        <div class="stat-item"><div class="stat-label">WIN RATE</div><div class="stat-value" style="color:#00ffcc;">{win_rate:.1f}%</div></div>
    </div>
""", unsafe_allow_html=True)

# Prediction Logic
current_pattern = "".join(map(str, st.session_state.num_sequence[-6:]))
prediction = NUMBER_LOGIC.get(current_pattern, None)

if prediction:
    color = "#dc3545" if prediction == "BIG" else "#28a745"
    st.markdown(f'<div class="pred-box" style="background-color: {color}; color: white;">NEXT: {prediction}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="wait-box">WAITING FOR PATTERN...</div>', unsafe_allow_html=True)

# Input
if len(st.session_state.num_sequence) < 6:
    init_input = st.text_input("Enter first 6 digits to start", max_chars=6)
    if st.button("INITIALIZE"):
        if len(init_input) == 6:
            st.session_state.num_sequence = [int(d) for d in init_input]
            st.rerun()
else:
    new_digit = None
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
            st.session_state.stats["wins" if is_win else "loss"] += 1
            if res_type == st.session_state.stats["last_res"]: st.session_state.stats["streak"] += 1
            else: st.session_state.stats["streak"], st.session_state.stats["last_res"] = 1, res_type
            st.session_state.stats[f"max_{res_type}"] = max(st.session_state.stats[f"max_{res_type}"], st.session_state.stats["streak"])
            st.session_state.history.insert(0, {"Num": new_digit, "Pred": prediction, "Result": "WIN" if is_win else "LOSS"})
        st.session_state.num_sequence.append(new_digit)
        st.rerun()

# Download Tracker History
if st.session_state.history:
    hist_df = pd.DataFrame(st.session_state.history)
    st.table(hist_df.head(10))
    st.download_button("📥 DOWNLOAD TRACKER HISTORY", hist_df.to_csv(index=False), "tracker_history.csv", "text/csv")

if st.button("RESET TRACKER"):
    st.session_state.clear()
    st.rerun()

# --- 6. BATCH EVALUATION SECTION ---
st.markdown('<div class="eval-section">', unsafe_allow_html=True)
st.subheader("📊 Batch Evaluation (Past 500 Results)")
up_file = st.file_uploader("Upload CSV (Header: 'number')", type="csv")

if up_file and st.button("🚀 START EVALUATION"):
    df_ev = pd.read_csv(up_file).head(500)
    if 'number' in df_ev.columns:
        e_wins, e_loss, e_max_w, e_max_l, cur_w, cur_l, e_results, t_seq = 0, 0, 0, 0, 0, 0, [], []
        for i, row in df_ev.iterrows():
            n = int(row['number'])
            if len(t_seq) >= 6:
                key = "".join(map(str, t_seq[-6:]))
                p = NUMBER_LOGIC.get(key, None)
                if p:
                    act = "BIG" if n >= 5 else "SMALL"
                    if act == p:
                        e_wins += 1; cur_w += 1; cur_l = 0; e_max_w = max(e_max_w, cur_w)
                        res = "WIN"
                    else:
                        e_loss += 1; cur_l += 1; cur_w = 0; e_max_l = max(e_max_l, cur_l)
                        res = "LOSS"
                    e_results.append({"Step": i+1, "Pattern": key, "Pred": p, "Actual": act, "Result": res})
            t_seq.append(n)
        
        # Display Stats
        tot_ev = e_wins + e_loss
        rate_ev = (e_wins / tot_ev * 100) if tot_ev > 0 else 0
        st.write(f"**WINS:** {e_wins} | **LOSS:** {e_loss} | **WIN RATE:** {rate_ev:.1f}%")
        st.write(f"**MAX WIN:** {e_max_w} | **MAX LOSS:** {e_max_l}")
        
        # Download Report
        report_csv = pd.DataFrame(e_results).to_csv(index=False)
        st.download_button("📥 DOWNLOAD BATCH REPORT", report_csv, "batch_evaluation.csv", "text/csv")
    else: st.error("CSV must have 'number' column.")
st.markdown('</div>', unsafe_allow_html=True)
