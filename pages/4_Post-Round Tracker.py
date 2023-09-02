import streamlit as st
import pandas as pd
# Import classes using precise module indications. For example:
from highcharts_core.chart import Chart
from highcharts_core.global_options.shared_options import SharedOptions
from highcharts_core.options import HighchartsOptions
from highcharts_core.options.plot_options.bar import BarOptions
from highcharts_core.options.series.bar import BarSeries
import streamlit as st
import streamlit.components.v1 as components
import streamlit_highcharts as hct
import json
from datetime import date
import pandas as pd
import plotly.express as px  # interactive charts
import time
from pandas.api.types import is_float_dtype
import numpy as np
from highcharts import Highchart
from copy import deepcopy


# Load events jsonl file
with open('../CCT-Online-Finals-1/2579089_events.jsonl', 'r') as jsonl_file:
    json_list = list(jsonl_file)

# Load state json file
with open(f'../CCT-Online-Finals-1/2578928_state.json', 'r') as json_file:
    state = json.load(json_file)

date = state["startedAt"].split("T")[0]
format =state["format"]

# Data Engineering
def get_player_state(event, return_df=True):
    """ Returns df of players' most updated state """

    # All weapons lists
    primary = ['mag7','nova','xm1014','mac10','mp9','ak47','aug','famas','galilar','m4a1','m4a1_silencer','ssg08','awp','m249','negev','scar20','g3sg1','sg553','ppbizon','mp7','ump45','p90','mp5_silencer','sawedoff']
    secondary = ['hkp2000','cz75a','deagle','fiveseven','glock','p250','tec9','usp_silencer', 'elite', 'revolver']
    melee = ['knife','knife_t']

    players = []
    event = deepcopy(event)
    teams = event["seriesState"]["games"][-1]["teams"]
    for team in teams:
        for _player in team["players"]:
            player = {}
            player["team"] = team["name"]

            # Flatten objectives
            objectives = {}
            for objective in _player["objectives"]:
                objectives[objective["id"]] = objective["completionCount"]

            # Flatten loadout
            player_loadout = {"loadout":
                              {
                                  "primary":None,
                                  "secondary":None,
                                  "melee":None,
                                  "helm":None,
                                  "kevlarVest":None,
                                  "bomb":None,
                                  "defuser":None,
                                  "decoy":None,
                                  "flashbang":None,
                                  "hegrenade":None,
                                  "incgrenade":None,
                                  "molotov":None,
                                  "smokeGrenade":None,
                                  "taser":None
                                  }
                              }

            for item in _player["items"]:
                item_id = item["id"]
                if item_id in primary:
                    player_loadout["loadout"]["primary"] = item_id
                elif item_id in secondary:
                    player_loadout["loadout"]["secondary"] = item_id
                elif item_id in melee:
                    player_loadout["loadout"]["melee"] = item_id
                else:
                    player_loadout["loadout"][item_id] = item_id

            # Remove useless fields
            redundant_fields = ["statePath", "character", "items", "externalLinks", "objectives"]
            for field in redundant_fields:
                _player.pop(field)

            player.update(_player)
            player.update(objectives)
            player.update(player_loadout)
            players.append(player)

    players = sorted(players, key=lambda x: (x["team"], x["name"]))
    if return_df:
        return pd.json_normalize(players)
    else:
        return players

def get_player_health_armor(event):
    """ Returns df of players' most updated health and armor values """

    required_fields = ["currentHealth", "currentArmor"]
    players = get_player_state(event).filter(items=(["team", "name"] + required_fields))
    return players

def get_player_economy(event):
    required_fields = ["money", "inventoryValue", "netWorth"]
    players = get_player_state(event).filter(items=(["team", "name"] + required_fields))
    return players

def get_player_kdao(event):
    required_fields = ["kills", "killAssistsGiven", "deaths", "beginDefuseWithKit", "beginDefuseWithoutKit", "defuseBomb", "explodeBomb", "plantBomb"]
    players = get_player_state(event).filter(items=(["team", "name"] + required_fields)).fillna(0)
    for col in ["beginDefuseWithKit", "beginDefuseWithoutKit", "defuseBomb", "explodeBomb", "plantBomb"]:
        players[col] = players[col].astype('Int64')
    return players

def get_loadout(event):
    required_fields = ["loadout.*"]
    players = get_player_state(event).filter(regex="|".join(["^team$", "^name$"] + required_fields))
    return players

event = json.loads(json_list[2443])["events"][-1]
# display(get_player_health_armor(event))
# display(get_player_economy(event))
# display(get_player_kdao(event))
# display(get_loadout(event))

pha = get_player_health_armor(event)
kda = get_player_kdao(event)

# Dummy Variables
team1='TeamA'
team2='TeamB'
round_num=2
team1player1='Player Tom'
team2player1='Player Jerry'
team2player2='Player Bugs Bunny'
event_action1='headshot'
event_action2='picked up'
item1='boom boom grenade'

#Sek Ee's code

def get_team_info(event, granularity):
    required_fields = ["name", "side", "score", "kills", "objectives"]
    if granularity == "game":
        games = event["seriesState"]["games"]
        games_info = []
        for game in games:
            map_seq = int(game["sequenceNumber"])
            map_name = game["map"]["name"]

            teams = game["teams"]
            for team in teams:
                # Flatten objectives
                objectives = {}
                for objective in team["objectives"]:
                    objectives[objective["id"]] = objective["completionCount"]

                team_info = {
                    "map_seq": map_seq,
                    "map": map_name,
                    "name": team["name"],
                    "side": team["side"],
                    "score": team["score"],
                    "kills": team["kills"],
                    "objectives": objectives
                }
                games_info.append(team_info)
        games_info = pd.json_normalize(sorted(games_info, key=lambda x: (x["map_seq"], x["name"])))
        for col in games_info.columns:
            if is_float_dtype(games_info[col]):
                games_info[col] = games_info[col].astype('Int64')
        return games_info
    elif granularity == "round":
        games = event["seriesState"]["games"]
        games_info = []
        for game in games:
            map_seq = int(game["sequenceNumber"])
            map_name = game["map"]["name"]

            rounds = game["segments"]
            for round in rounds:
                round_seq = int(round["id"].split("-")[-1])

                teams = round["teams"]
                for team in teams:
                    # Flatten objectives
                    objectives = {}
                    for objective in team["objectives"]:
                        objectives[objective["id"]] = objective["completionCount"]

                    team_info = {
                        "map_seq": map_seq,
                        "map": map_name,
                        "round_seq": round_seq,
                        "name": team["name"],
                        "won": team["won"],
                        "side": team["side"],
                        "kills": team["kills"],
                        "objectives": objectives
                    }
                    games_info.append(team_info)
        games_info = pd.json_normalize(sorted(games_info, key=lambda x: (x["map_seq"], x["round_seq"], x["name"])))
        for col in games_info.columns:
            if is_float_dtype(games_info[col]):
                games_info[col] = games_info[col].astype('Int64')
        return games_info
    else:
        return None

def get_player_state(teams):

    # All weapons lists
    primary = ['mag7','nova','xm1014','mac10','mp9','ak47','aug','famas','galilar','m4a1','m4a1_silencer','ssg08','awp','m249','negev','scar20','g3sg1','sg553','ppbizon','mp7','ump45','p90','mp5_silencer','sawedoff']
    secondary = ['hkp2000','cz75a','deagle','fiveseven','glock','p250','tec9','usp_silencer', 'elite', 'revolver']
    melee = ['knife','knife_t']

    players = []

    for team in teams:
        team_name = team["name"]
        team_side = team["side"] if "side" in team else None
        team_score = team["score"]
        team_total_kills = team["kills"]

        for _player in team["players"]:
            player = {}
            player["team"] = team_name
            player["team_side"] = team_side
            player["team_score"] = team_score
            player["team_total_kills"] = team_total_kills

            # Flatten objectives
            objectives = {}
            for objective in _player["objectives"]:
                objectives[objective["id"]] = objective["completionCount"]

            # Flatten loadout
            player_loadout = {"loadout":
                                {
                                    "primary":None,
                                    "secondary":None,
                                    "melee":None,
                                    "helm":None,
                                    "kevlarVest":None,
                                    "bomb":None,
                                    "defuser":None,
                                    "decoy":None,
                                    "flashbang":None,
                                    "hegrenade":None,
                                    "incgrenade":None,
                                    "molotov":None,
                                    "smokeGrenade":None,
                                    "taser":None
                                    }
                                }

            for item in _player["items"]:
                item_id = item["id"]
                if item_id in primary:
                    player_loadout["loadout"]["primary"] = item_id
                elif item_id in secondary:
                    player_loadout["loadout"]["secondary"] = item_id
                elif item_id in melee:
                    player_loadout["loadout"]["melee"] = item_id
                else:
                    player_loadout["loadout"][item_id] = item_id

            # Remove useless fields
            redundant_fields = ["statePath", "character", "items", "externalLinks", "objectives"]
            for field in redundant_fields:
                _player.pop(field)

            player.update(_player)
            player.update(objectives)
            player.update(player_loadout)
            players.append(player)

    players = sorted(players, key=lambda x: (x["team"], x["name"]))

    return players

def get_player_game_state(event, return_df=True):
    """ Returns df of players' most updated state """

    series_start = event["seriesState"]["startedAt"].split("T")[0]

    event = deepcopy(event)
    game = event["seriesState"]["games"][-1]

    map_seq = game["sequenceNumber"]
    map_name = game["map"]["name"]
    round_seq = game["segments"][-1]["sequenceNumber"]

    teams = game["teams"]
    players = get_player_state(teams)
    for player in players:
        player["seriesStart"] = series_start
        player["map_seq"] = f"Map {map_seq}"
        player["map_name"] = map_name
        player["round_seq"] = f"Round {round_seq}"

    if return_df:
        return pd.json_normalize(players)
    else:
        return players

def get_player_health_armor(event):
    """ Returns df of players' most updated health and armor values """

    required_fields = ["currentHealth", "currentArmor"]
    default_fields = ["team", "name"]
    players = get_player_game_state(event).filter(items=(default_fields + required_fields))
    return players

def get_player_economy(event):
    required_fields = ["money", "inventoryValue", "netWorth"]
    default_fields = ["team", "name"]
    players = get_player_game_state(event).filter(items=(default_fields + required_fields))
    return players

def get_player_kdao(event):
    required_fields = ["kills", "killAssistsGiven", "deaths", "beginDefuseWithKit", "beginDefuseWithoutKit", "defuseBomb", "explodeBomb", "plantBomb"]
    default_fields = ["team", "name"]
    players = get_player_game_state(event).filter(items=(default_fields + required_fields)).fillna(0)
    for col in ["beginDefuseWithKit", "beginDefuseWithoutKit", "defuseBomb", "explodeBomb", "plantBomb"]:
      if col in players.columns:
        players[col] = players[col].astype('Int64')
    return players

def get_loadout(event):
    required_fields = ["loadout.*"]
    default_fields = ["^team$", "^name$"]
    players = get_player_game_state(event).filter(regex="|".join(default_fields + required_fields))
    return players


    



# Streamlit Visuals
# Top Header Section
st.title("During Series")

st.subheader(f"Date of Match: {date}")
st.write(f"Match format: {format}")

components.html(
    f"""
    <div style="height:200px; background-color:#F0F2F6;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
        <div style="text-align: right;">
            <h3 style="color:black;font-family:Source Sans Pro;">{team1}</h3>
            <img style="height:50px;" src="https://img-cdn.hltv.org/teamlogo/Ox1eFAB6o8VM6jwgPbQuks.svg?ixlib=java-2.1.0&s=66680f6d946ff4a93bc311f3bbab8d9e" />
        </div>

        <h3 style="color:black;font-size:40px;;text-align: center; ">2 - 0</h3>
        <div style="text-align: left;">
            <h3 style="color:black;">{team2}</h3>
            <img style="height:50px;" src="https://preview.redd.it/new-forze-logo-v0-x31u5t3sg8ba1.png?width=600&format=png&auto=webp&s=041b6912e65d06e150219f63f79dc05b911e9c04" />
        </div>
    </div>

    """
)

# Tabs
pre_tab, during_tab, post_tab = st.tabs(["Pre-Round", "During Round", "Post-Round"])

# Pre-Round Tab
pre_tab.header(f"Round {round_num}")

# During Round Tab
during_tab.header(f"Round {round_num}")
during_tab.table(kda)
during_tab.table(pha)

# Post Round Tab
post_tab.header(f"Round {round_num}")

event = json.loads(json_list[2315])["events"][-1]

round_events = get_team_info(event, granularity="round")
line_chart_df = round_events.drop(["map_seq",'map','won','side','objectives.plantBomb','objectives.explodeBomb','objectives.beginDefuseWithKit','objectives.defuseBomb','objectives.beginDefuseWithoutKit'], axis=1)
with post_tab:
    # data prep for line chart - split df into teams
    line_chart_team1 = line_chart_df[line_chart_df['name'] == "ECSTATIC"].drop(["name"], axis=1)
    line_chart_team2 = line_chart_df[line_chart_df['name'] == "forZe"].drop(["name"], axis=1)
    round_tracker = 0
    live_data_team1 = pd.DataFrame()
    live_data_team2 = pd.DataFrame()
    live_data = pd.DataFrame()
    placeholder = st.empty()

    for seconds in range(40):
        with placeholder.container():
            latest_round = line_chart_df.iloc[[round_tracker]]
            live_data = pd.concat([live_data,latest_round ], ignore_index=True)
            round_tracker+=1
            fig2 = px.line(data_frame = live_data,y =live_data['kills'] , x =live_data['round_seq'], color=live_data['name'])
            st.write(fig2)
            time.sleep(1)
    