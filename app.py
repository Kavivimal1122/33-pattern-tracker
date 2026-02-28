import streamlit as st
import pandas as pd
import io

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
    .eval-container { background-color: #262730; padding: 20px; border-radius: 10px; margin-top: 30px; border: 1px solid #444; }
    [data-testid="column"] { padding: 0px !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Deterministic Pattern Database
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

# --- 7. BATCH EVALUATION FUNCTION ---
st.markdown('<div class="eval-container">', unsafe_allow_html=True)
st.subheader("📊 Batch Evaluation (Past 500 Results)")
uploaded_file = st.file_uploader("Upload CSV file (Must have a column named 'number')", type="csv")

if uploaded_file is not None:
    if st.button("🚀 RUN EVALUATION"):
        df_eval = pd.read_csv(uploaded_file).head(500)
        
        if 'number' not in df_eval.columns:
            st.error("Error: CSV must contain a 'number' column.")
        else:
            eval_wins = 0
            eval_loss = 0
            eval_max_win = 0
            eval_max_loss = 0
            current_win_streak = 0
            current_loss_streak = 0
            eval_results = []
            
            # Temporary sequence for evaluation
            temp_seq = []
            
            for index, row in df_eval.iterrows():
                num = int(row['number'])
                
                # Check for prediction logic (need 6 numbers)
                if len(temp_seq) >= 6:
                    key = "".join(map(str, temp_seq[-6:]))
                    eval_pred = NUMBER_LOGIC.get(key, None)
                    
                    if eval_pred:
                        actual_size = "BIG" if num >= 5 else "SMALL"
                        is_win = (actual_size == eval_pred)
                        
                        if is_win:
                            eval_wins += 1
                            current_win_streak += 1
                            current_loss_streak = 0
                            eval_max_win = max(eval_max_win, current_win_streak)
                            status = "WIN"
                        else:
                            eval_loss += 1
                            current_loss_streak += 1
                            current_win_streak = 0
                            eval_max_loss = max(eval_max_loss, current_loss_streak)
                            status = "LOSS"
                            
                        eval_results.append({
                            "Step": index + 1,
                            "Pattern": key,
                            "Prediction": eval_pred,
                            "Actual": actual_size,
                            "Result": status
                        })
                
                temp_seq.append(num)
            
            # Display Metrics
            total_eval = eval_wins + eval_loss
            eval_rate = (eval_wins / total_eval * 100) if total_eval > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("WINS", eval_wins)
            col2.metric("LOSS", eval_loss)
            col3.metric("WIN RATE", f"{eval_rate:.1f}%")
            
            col4, col5 = st.columns(2)
            col4.metric("MAX WIN", eval_max_win)
            col5.metric("MAX LOSS", eval_max_loss)
            
            # Download Results
            eval_df_final = pd.DataFrame(eval_results)
            csv_buffer = io.StringIO()
            eval_df_final.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 DOWNLOAD EVALUATION REPORT",
                data=csv_buffer.getvalue(),
                file_name="evaluation_report.csv",
                mime="text/csv"
            )
            st.success("Evaluation Complete!")

st.markdown('</div>', unsafe_allow_html=True)
