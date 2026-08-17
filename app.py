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

st.title("⚽ Football Prediction League")
st.write(
    "Predict where teams will finish! Lower score is better (absolute error"
    " from actual finish)."
)

menu = st.selectbox(
    "Choose an action",
    ["View Standings", "Submit Predictions", "Set Actual Final Positions"],
)

if menu == "View Standings":
  st.header("Current Leaderboard")
  actuals = data.get("teams", {})
  predictions = data.get("predictions", {})

  if not actuals:
    st.info(
        "ℹ️ Actual final positions haven't been entered yet by the admin. Check"
        " back at the end of the season!"
    )

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
    st.table(leaderboard)
  else:
    st.write("No predictions submitted yet!")

elif menu == "Submit Predictions":
  st.header("Submit Your Predictions")
  player_name = st.text_input("Your Name")

  if player_name:
    st.write(f"Entering predictions for **{player_name}**")
    player_preds = data["predictions"].get(player_name, {})

    # Current 2026/27 Premier League teams list
    default_teams = [
        "Arsenal",
        "Aston Villa",
        "Bournemouth",
        "Brentford",
        "Brighton & Hove Albion",
        "Chelsea",
        "Coventry City",
        "Crystal Palace",
        "Everton",
        "Fulham",
        "Hull City",
        "Ipswich Town",
        "Leeds United",
        "Liverpool",
        "Manchester City",
        "Manchester United",
        "Newcastle United",
        "Nottingham Forest",
        "Sunderland",
        "Tottenham Hotspur",
    ]

    new_preds = {}
    with st.form("prediction_form"):
      st.write("Enter your predicted position (1-20) for each team:")
      for team in default_teams:
        current_val = player_preds.get(team, 1)
        new_preds[team] = st.number_input(
            team, min_value=1, max_value=20, value=int(current_val), step=1
        )

      submitted = st.form_submit_button("Save Predictions")
      if submitted:
        data["predictions"][player_name] = new_preds
        save_data(data)
        st.success(f"Predictions saved successfully for {player_name}!")

elif menu == "Set Actual Final Positions":
  st.header("Admin: Set Actual Positions")
  password = st.text_input("Admin Password", type="password")
  if password == "football123":
    st.write(
        "Enter the final standings once the season ends to calculate scores."
    )
    actuals = data.get("teams", {})
    with st.form("actuals_form"):
      new_actuals = {}
      for team in [
          "Arsenal",
          "Aston Villa",
          "Bournemouth",
          "Brentford",
          "Brighton & Hove Albion",
          "Chelsea",
          "Coventry City",
          "Crystal Palace",
          "Everton",
          "Fulham",
          "Hull City",
          "Ipswich Town",
          "Leeds United",
          "Liverpool",
          "Manchester City",
          "Manchester United",
          "Newcastle United",
          "Nottingham Forest",
          "Sunderland",
          "Tottenham Hotspur",
      ]:
        current_val = actuals.get(team, 1)
        new_actuals[team] = st.number_input(
            f"Actual pos for {team}",
            min_value=1,
            max_value=20,
            value=int(current_val),
            step=1,
        )

      submitted = st.form_submit_button("Save Actuals")
      if submitted:
        data["teams"] = new_actuals
        save_data(data)
        st.success("Actual positions updated!")
  elif password:
    st.error("Incorrect password.")
