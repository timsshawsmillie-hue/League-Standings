import base64
import json
import os
import streamlit as st
from streamlit_sortables import sort_items

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


# --- LOCAL BACKGROUND & MOBILE-RESPONSIVE CSS ---
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
        .left-container {{
            background-color: rgba(15, 23, 42, 0.90);
            color: white;
            padding: 1.5rem;
            border-radius: 1rem;
            margin-top: 2rem;
        }}
        .right-container {{
            background-color: rgba(15, 23, 42, 0.90);
            color: white;
            padding: 1.5rem;
            border-radius: 1rem;
            margin-top: 2rem;
        }}
        h1, h2, h3, p, label {{
            color: white !important;
        }}
        
        /* MOBILE OPTIMIZATION: Stack columns and make containers full width on phones */
        @media (max-width: 900px) {{
            [data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
            }}
            .left-container, .right-container {{
                margin-top: 1rem !important;
                padding: 1rem !important;
            }}
        }}

        /* Force sortable component into a single vertical column league table layout */
        .sortable-list, [data-testid="stVerticalBlock"] div div div div iframe {{
            display: flex !important;
            flex-direction: column !important;
        }}
        
        /* Style individual team items to look like clean table rows */
        .sortable-item {{
            width: 100% !important;
            margin-bottom: 5px !important;
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

# --- THREE-COLUMN LAYOUT (Desktop) / STACKED (Mobile) ---
left_col, middle_col, right_col = st.columns([1.2, 1.8, 1.2], gap="large")

with left_col:
  st.markdown('<div class="left-container">', unsafe_allow_html=True)
  st.title("🏆 Football Tipping League")
  st.write("Drag and drop the teams into your predicted 1st-20th order.")

  menu = st.radio(
      "Choose an action",
      menu_options,
      horizontal=True,
      label_visibility="collapsed",
  )
  st.write("")

  if menu == "Submit Predictions":
    player_name = st.text_input("Your Name")
    if player_name:
      user_saved_preds = data["predictions"].get(player_name, {})
      if user_saved_preds:
        sorted_teams_tuples = sorted(user_saved_preds.items(), key=lambda x: x[1])
        current_list = [team for team, pos in sorted_teams_tuples]
      else:
        current_list = teams_list

      sorted_list = sort_items(current_list, key=f"sort_{player_name}")

      if st.button("Save My Predictions"):
        new_preds = {
            team: index + 1 for index, team in enumerate(sorted_list)
        }
        data["predictions"][player_name] = new_preds
        save_data(data)
        st.success(f"Saved for {player_name}!")

  elif menu == "Set Actual Final Positions" and is_admin:
    st.header("Admin: Set Actuals")
    actuals = data.get("teams", {})
    with st.form("actuals_form"):
      new_actuals = {}
      for team in teams_list:
        new_actuals[team] = st.number_input(
            f"Actual {team}",
            min_value=1,
            max_value=20,
            value=actuals.get(team, 1),
            step=1,
        )
      if st.form_submit_button("Save Actuals"):
        data["teams"] = new_actuals
        save_data(data)
        st.success("Updated!")

  elif menu == "Admin Management" and is_admin:
    st.header("Admin: Manage")
    predictions = data.get("predictions", {})
    if not predictions:
      st.write("No entries yet.")
    else:
      for player in list(predictions.keys()):
        c1, c2 = st.columns([3, 1])
        c1.write(f"**{player}**")
        if c2.button(f"Del", key=f"del_{player}"):
          del data["predictions"][player]
          save_data(data)
          st.rerun()

  st.markdown("</div>", unsafe_allow_html=True)

with middle_col:
  st.write("")  # Keeps the middle open to reveal Hasbulla on desktop

with right_col:
  st.markdown('<div class="right-container">', unsafe_allow_html=True)
  st.header("📊 Standings")
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
