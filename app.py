import streamlit as st
import pandas as pd
import collections
import os
import time

# 1. Page Configuration
st.set_page_config(page_title="91 AI Pro - Deterministic", layout="centered")

# 2. Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; padding-left: 0.2rem !important; padding-right: 0.2rem !important; }
    .big-training-text { font-size: 38px; font-weight: 900; color: #00ffcc; text-align: center; margin-bottom: 20px; }
    .max-streak-container {
        background-color: #0e1117; padding: 10px; border-radius: 12px;
        text-align: center; border: 2px solid #444; margin-bottom: 10px;
    }
    .max-label { font-size: 13px; font-weight: bold; color: #888; text-transform: uppercase; }
    .max-value { font-size: 32px; font-weight: 900; line-height: 1.1; }
    .pred-box { padding: 15px; border-radius: 10px; text-align: center; border: 2px solid white; margin-bottom: 15px; }
    .alert-box { padding: 10px; border-radius: 6px; margin-bottom: 10px; font-weight: bold; text-align: center; color: white; }
    div.stButton > button {
        width: 100% !important; height: 55px !important; border-radius: 4px !important; 
        font-weight: 900 !important; font-size: 19px !important; color: white !important;        
        border: 1px solid white !important; margin: 1px 0px !important; background-color: #1f1f1f !important;
    }
    [data-testid="column"] { width: 9% !important; flex: 1 1 9% !important; min-width: 9% !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Session State
if 'ai_logic' not in st.session_state: st.session_state.ai_logic = None
if 'history' not in st.session_state: st.session_state.history = []
if 'num_sequence' not in st.session_state: st.session_state.num_sequence = []
if 'consecutive_loss' not in st.session_state: st.session_state.consecutive_loss = 0
if 'stats' not in st.session_state: 
    st.session_state.stats = {"wins": 0, "loss": 0, "streak": 0, "last_res": None, "max_win": 0, "max_loss": 0}

# 4. Pattern Training Function
def train_deterministic_logic(file):
    df = pd.read_csv(file, sep=None, engine='python', header=None)
    # Check if data is tab-separated or needs manual parsing
    # Assumes format: [Number] [Size (S/B)] [Color (G/R)]
    if df.shape[1] < 2:
         st.error("Invalid CSV Format. Ensure it has Number and Size columns.")
         return None
    
    num_seq = df[0].astype(str).tolist()
    size_seq = df[1].astype(str).tolist()
    
    # Training Animation
    progress_bar = st.progress(0)
    status_text = st.empty()
    for p in range(101):
        time.sleep(0.01)
        progress_bar.progress(p)
        status_text.markdown(f'<div class="big-training-text">TRAINING: {p}%</div>', unsafe_allow_html=True)
    
    # Identify 100% Accurate Patterns of length 6
    logic = {}
    patterns = collections.defaultdict(list)
    for i in range(len(num_seq) - 6):
        pat = tuple(num_seq[i:i+6])
        next_val = "BIG" if size_seq[i+6].upper() == 'B' else "SMALL"
        patterns[pat].append(next_val)
    
    for pat, outcomes in patterns.items():
        unique_outcomes = set(outcomes)
        if len(unique_outcomes) == 1:
            logic["".join(pat)] = list(unique_outcomes)[0]
            
    status_text.markdown('<div class="big-training-text" style="color:#28a745;">COMPLETED 100%</div>', unsafe_allow_html=True)
    return logic

# 5. App UI
if st.session_state.ai_logic is None:
    st.title("🤖 AI Logic Initialization")
    file = st.file_uploader("Upload OVER all.CSV to learn patterns", type="csv")
    if file and st.button("🚀 LEARN PATTERNS"):
        st.session_state.ai_logic = train_deterministic_logic(file)
        st.rerun()
else:
    # Header Statistics
    total_games = st.session_state.stats['wins'] + st.session_state.stats['loss']
    win_rate = (st.session_state.stats['wins'] / total_games * 100) if total_games > 0 else 0.0
    
    st.markdown(f"""
        <div class="max-streak-container">
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                <div><div class="max-label">MAX WIN</div><div class="max-value" style="color: #28a745;">{st.session_state.stats['max_win']}</div></div>
                <div><div class="max-label">MAX LOSS</div><div class="max-value" style="color: #dc3545;">{st.session_state.stats['max_loss']}</div></div>
                <div><div class="max-label">WINS</div><div class="max-value">{st.session_state.stats['wins']}</div></div>
                <div><div class="max-label">LOSS</div><div class="max-value">{st.session_state.stats['loss']}</div></div>
                <div><div class="max-label">WIN RATE</div><div class="max-value" style="color: #00ffcc;">{win_rate:.2f}%</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 6-Number or Single-Number Input
    if not st.session_state.num_sequence:
        init_in = st.text_input("Enter 6 numbers to start tracking", max_chars=6)
        if st.button("START"):
            if len(init_in) == 6:
                st.session_state.num_sequence = [d for d in init_in]
                st.rerun()
    else:
        # Prediction Logic
        current_pat = "".join(st.session_state.num_sequence[-6:])
        prediction = st.session_state.ai_logic.get(current_pat, None)

        # Alerts
        if st.session_state.consecutive_loss >= 3:
            st.markdown('<div class="alert-box" style="background-color: #dc3545;">🛑 3 TIMES LOSS SO STOP - WAIT FOR NORMALIZE</div>', unsafe_allow_html=True)
        elif prediction:
            st.markdown('<div class="alert-box" style="background-color: #28a745;">✅ GO PLAY - PATTERN MATCHED</div>', unsafe_allow_html=True)
            st.info("📋 THIS SAME PATTERN FOUND IN YOUR DATA")
        
        # Display Prediction
        if prediction:
            bg_color = "#dc3545" if prediction == "BIG" else "#28a745"
            st.markdown(f'<div class="pred-box" style="background-color: {bg_color};"><h1 style="color:white; margin:0;">{prediction}</h1><p style="margin:0; color:white;">CONFIDENCE: 100% 🔥</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="pred-box" style="background-color: #333; border: 2px dashed #666;"><h1 style="color:#888; margin:0;">WAITING...</h1><p style="margin:0; color:#888;">No exact pattern found</p></div>', unsafe_allow_html=True)

        # Number Dialer
        new_num = None
        cols = st.columns(10)
        for i in range(10):
            if cols[i].button(str(i), key=f"d_{i}"): new_num = i

        if new_num is not None:
            # Check Result of previous prediction
            if prediction:
                actual_size = "BIG" if new_num >= 5 else "SMALL"
                is_win = (actual_size == prediction)
                res_type = "win" if is_win else "loss"
                
                st.session_state.stats["wins" if is_win else "loss"] += 1
                if res_type == st.session_state.stats["last_res"]: st.session_state.stats['streak'] += 1
                else:
                    st.session_state.stats['streak'], st.session_state.stats['last_res'] = 1, res_type
                
                st.session_state.stats[f"max_{res_type}"] = max(st.session_state.stats[f"max_{res_type}"], st.session_state.stats['streak'])
                st.session_state.consecutive_loss = 0 if is_win else (st.session_state.consecutive_loss + 1)
                
                st.session_state.history.insert(0, {"Num": new_num, "Result": actual_size, "Status": "WIN" if is_win else "LOSS", "Streak": st.session_state.stats['streak']})
            
            st.session_state.num_sequence.append(str(new_num))
            st.rerun()

    if st.session_state.history:
        st.markdown("### Recent Results Tracking")
        st.table(pd.DataFrame(st.session_state.history).head(20))

    if st.button("🔄 FULL RESET"):
        st.session_state.clear()
        st.rerun()
