import json
import os
import streamlit as st

DATA_FILE = "predictions.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"teams": {}, "predictions": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# --- CUSTOMIZE YOUR TITLE HERE ---
st.title("🏆 Top Of The League") 
st.write("Predict the final table! Every position (1-20) must be unique.")

menu = st.selectbox("Choose an action", ["View Standings", "Submit Predictions", "Set Actual Final Positions"])

teams_list = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton & Hove Albion",
    "Chelsea", "Coventry City", "Crystal Palace", "Everton", "Fulham",
    "Hull City", "Ipswich Town", "Leeds United", "Liverpool", "Manchester City",
    "Manchester United", "Newcastle United", "Nottingham Forest", "Sunderland", "Tottenham Hotspur"
]

if menu == "View Standings":
    st.header("Current Leaderboard")
    actuals = data.get("teams", {})
    predictions = data.get("predictions", {})

    leaderboard = []
    for player, preds in predictions.items():
        total_score = 0
        matched_teams = 0
        for team, predicted_pos in preds.items():
            if team in actuals:
                total_score += abs(predicted_pos - actuals[team])
                matched_teams += 1
        if matched_teams > 0:
            leaderboard.append({"Player": player, "Score": total_score})
        else:
            leaderboard.append({"Player": player, "Score": "Pending"})

    if leaderboard:
        # Sort by score (lowest first)
        leaderboard.sort(key=lambda x: x["Score"] if isinstance(x["Score"], int) else 999)
        st.table(leaderboard)
    else:
        st.write("No predictions submitted yet!")

elif menu == "Submit Predictions":
    st.header("Submit Your Predictions")
    player_name = st.text_input("Your Name")
    if player_name:
        new_preds = {}
        with st.form("prediction_form"):
            for team in teams_list:
                new_preds[team] = st.number_input(team, min_value=1, max_value=20, value=1, step=1)
            
            submitted = st.form_submit_button("Save Predictions")
            if submitted:
                # DATA INTEGRITY CHECK
                positions = list(new_preds.values())
                if len(set(positions)) != 20:
                    st.error("❌ Error: Each position (1-20) must be used exactly once. You have duplicates!")
                else:
                    data["predictions"][player_name] = new_preds
                    save_data(data)
                    st.success(f"Predictions saved successfully for {player_name}!")

elif menu == "Set Actual Final Positions":
    st.header("Admin: Set Actual Positions")
    password = st.text_input("Admin Password", type="password")
    if password == "football123":
        actuals = data.get("teams", {})
        with st.form("actuals_form"):
            new_actuals = {}
            for team in teams_list:
                new_actuals[team] = st.number_input(f"Actual pos for {team}", min_value=1, max_value=20, value=actuals.get(team, 1), step=1)
            if st.form_submit_button("Save Actuals"):
                data["teams"] = new_actuals
                save_data(data)
                st.success("Actual positions updated!")
    elif password:
        st.error("Incorrect password.")
