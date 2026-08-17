import base64
import json
import os
import streamlit as st

# Set page to wide mode to give space for columns
st.set_page_config(layout="wide", page_title="Football Tipping League")

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


# --- LOCAL BACKGROUND IMAGE & STYLING ---
def set_local_background(image_file):
  if os.path.exists(image_file):
    with open(image_file, "rb") as f:
      encoded_string = base64.b64encode(f.read()).decode()
    css = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: local;
        }}
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}
        /* Main left box container */
        .left-container {{
            background-color: rgba(15, 23, 42, 0.88);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-top: 5rem;
        }}
        /* Standalone right leaderboard container */
        .right-container {{
            background-color: rgba(15, 23, 42, 0.88);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-top: 5rem;
        }}
        h1, h2, h3, p, label {{
            color: white !important;
        }}
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)


set_local_background("stadium.jpg")

# --- SIDEBAR ADMIN LOGIN ---
st.sidebar.header("Admin Area")
admin_password = st.sidebar.text_input("Admin Password", type="password")
is_admin = admin_password == "football123"
if is_admin:
  st.sidebar.success("Admin Unlocked!")

# Define available options based on admin status
menu_options = ["Submit Predictions"]
if is_admin:
  menu_options.extend(["Set Actual Final Positions", "Admin Management"])

teams_list = [
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

# --- TWO-COLUMN LAYOUT ---
left_col, right_col = st.columns([1.2, 0.8], gap="large")

# LEFT COLUMN: Title, horizontal buttons, and active forms
with left_col:
  st.markdown('<div class="left-container">', unsafe_allow_html=True)
  st.title("🏆 The Ultimate Football Tipping League")
  st.write("Predict the final table! Every position (1-20) must be unique.")

  menu = st.radio(
      "Choose an action",
      menu_options,
      horizontal=True,
      label_visibility="collapsed",
  )
  st.write("")

  if menu == "Submit Predictions":
    st.header("Submit Your Predictions")
    player_name = st.text_input("Your Name")
    if player_name:
      new_preds = {}
      with st.form("prediction_form"):
        for team in teams_list:
          new_preds[team] = st.number_input(
              team, min_value=1, max_value=20, value=1, step=1
          )

        submitted = st.form_submit_button("Save Predictions")
        if submitted:
          positions = list(new_preds.values())
          if len(set(positions)) != 20:
            st.error(
                "❌ Error: Each position (1-20) must be used exactly once. You"
                " have duplicates!"
            )
          else:
            data["predictions"][player_name] = new_preds
            save_data(data)
            st.success(f"Predictions saved successfully for {player_name}!")

  elif menu == "Set Actual Final Positions" and is_admin:
    st.header("Admin: Set Actual Positions")
    actuals = data.get("teams", {})
    with st.form("actuals_form"):
      new_actuals = {}
      for team in teams_list:
        new_actuals[team] = st.number_input(
            f"Actual pos for {team}",
            min_value=1,
            max_value=20,
            value=actuals.get(team, 1),
            step=1,
        )
      if st.form_submit_button("Save Actuals"):
        data["teams"] = new_actuals
        save_data(data)
        st.success("Actual positions updated!")

  elif menu == "Admin Management" and is_admin:
    st.header("Admin: Manage Player Entries")
    predictions = data.get("predictions", {})
    if not predictions:
      st.write("No player entries found to manage.")
    else:
      st.write(
          "Here are all current submissions. Click 'Delete' to remove a player"
          " entry."
      )
      for player in list(predictions.keys()):
        c1, c2 = st.columns([3, 1])
        c1.write(f"**{player}** ({len(predictions[player])} teams predicted)")
        if c2.button(f"Delete", key=f"del_{player}"):
          del data["predictions"][player]
          save_data(data)
          st.success(f"Deleted entry for {player}!")
          st.rerun()

  st.markdown("</div>", unsafe_allow_html=True)

# RIGHT COLUMN: Standalone Leaderboard Box
with right_col:
  st.markdown('<div class="right-container">', unsafe_allow_html=True)
  st.header("📊 Live Standings")
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
    leaderboard.sort(
        key=lambda x: x["Score"] if isinstance(x["Score"], int) else 999
    )
    st.table(leaderboard)
  else:
    st.write("No predictions submitted yet!")

  st.markdown("</div>", unsafe_allow_html=True)
