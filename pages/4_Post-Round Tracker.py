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

@st.cache_data  # 👈 Add the caching decorator
def load_data():
    with open('../CCT-Online-Finals-1/2579089_events.jsonl', 'r') as jsonl_file:
        json_list = list(jsonl_file)
    return json_list


full_events = load_data()



def get_series_start_date(event):
    series_start = event["seriesState"]["startedAt"].split("T")[0]
    return series_start

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
                        "side": team["side"],
                        "won": team["won"],
                        "win_type": team["winType"],
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

def get_player_state(event, granularity):

    def flatten_lists(loadout=False):
        # Flatten objectives
        objectives = {}
        for objective in _player["objectives"]:
            objectives[objective["id"]] = objective["completionCount"]

        # Flatten killAssistsReceivedFromPlayer
        assisted_by = {}
        for _assisted_by in _player["killAssistsReceivedFromPlayer"]:
            assister_name = player_name_id_map[_assisted_by["playerId"]]
            assisted_by[assister_name] = _assisted_by["killAssistsReceived"]

        # Flatten teamkillAssistsReceivedFromPlayer
        team_kill_assisted_by = {}
        for _assisted_by in _player["teamkillAssistsReceivedFromPlayer"]:
            assister_name = player_name_id_map[_assisted_by["playerId"]]
            assisted_by[assister_name] = _assisted_by["teamkillAssistsReceived"]

        if loadout:
            # Flatten loadout
            player_loadout = {
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

            for item in _player["items"]:
                item_id = item["id"]
                if item_id in primary:
                    player_loadout["primary"] = item_id
                elif item_id in secondary:
                    player_loadout["secondary"] = item_id
                elif item_id in melee:
                    player_loadout["melee"] = item_id
                else:
                    player_loadout[item_id] = item_id

            return objectives, assisted_by, team_kill_assisted_by, player_loadout
        else:
            return objectives, assisted_by, team_kill_assisted_by

    def sort_and_change_dtype(players, sort_key):
        players = sorted(players, key=sort_key)
        players = pd.json_normalize(players)
        cols = players.columns

        rearranged_cols = []
        if "map_seq" in cols:
            rearranged_cols.extend(["map_seq", "map_name"])
        if "round_seq" in cols:
            rearranged_cols.extend(["round_seq"])
        rearranged_cols.extend(["team", "name"])
        for col in cols:
            if col not in rearranged_cols:
                rearranged_cols.append(col)
        players = players[rearranged_cols]
        for col in cols:
            if is_float_dtype(players[col]) and col != "adr":
                players[col] = players[col].astype('Int64')
        return players

    # All weapons lists
    primary = ['mag7','nova','xm1014','mac10','mp9','ak47','aug','famas','galilar','m4a1','m4a1_silencer','ssg08','awp','m249','negev','scar20','g3sg1','sg553','ppbizon','mp7','ump45','p90','mp5_silencer','sawedoff']
    secondary = ['hkp2000','cz75a','deagle','fiveseven','glock','p250','tec9','usp_silencer', 'elite', 'revolver']
    melee = ['knife','knife_t']

    player_name_id_map = {}
    for team in event["seriesState"]["teams"]:
        for _player in team["players"]:
            player_name_id_map[_player["id"]] = _player["name"]

    players = []
    if granularity == "series":
        teams = event["seriesState"]["teams"]
        for team in teams:
            team_name = team["name"]

            for _player in team["players"]:
                player_info = deepcopy(_player)
                objectives, assisted_by, team_kill_assisted_by = flatten_lists()

                # Remove useless fields
                redundant_fields = [
                    "statePath",
                    "participationStatus",
                    "structuresDestroyed",
                    "structuresCaptured",
                    "killAssistsReceivedFromPlayer",
                    "teamkillAssistsReceivedFromPlayer",
                    "externalLinks"
                ]
                for field in redundant_fields:
                    player_info.pop(field)

                for _updates in [
                    {"objectives": objectives},
                    {"killAssistsReceivedFromPlayer": assisted_by},
                    {"teamkillAssistsReceivedFromPlayer": team_kill_assisted_by},
                    {"team": team_name}]:
                    player_info.update(_updates)

                players.append(player_info)
        players = sort_and_change_dtype(players, sort_key=lambda x: (x["team"], x["name"]))
        return players

    elif granularity == "game":
        games = event["seriesState"]["games"]
        for game in games:
            map_seq = game["sequenceNumber"]
            map_name = game["map"]["name"]
            num_rounds = int(game["segments"][-1]["id"].split("-")[-1])
            teams = game["teams"]

            multikills = {}
            for round in game["segments"]:
                for team in round["teams"]:
                    for _player in team["players"]:
                        player_name = _player["name"]
                        player_kills = _player["kills"]
                        if player_kills > 2:
                            if player_name in multikills:
                                multikills[player_name] += 1
                            else:
                                multikills[player_name] = 1

            for team in teams:
                team_name = team["name"]

                for _player in team["players"]:
                    player_info = deepcopy(_player)
                    player_name = player_info["name"]
                    objectives, assisted_by, team_kill_assisted_by, player_loadout = flatten_lists(loadout=True)

                    adr = player_info["damageDealt"]/num_rounds
                    multikill = multikills[player_name] if player_name in multikills else 0

                    # Remove useless fields
                    redundant_fields = [
                        "statePath",
                        "character",
                        "participationStatus",
                        "structuresDestroyed",
                        "structuresCaptured",
                        "items",
                        "position",
                        "killAssistsReceivedFromPlayer",
                        "teamkillAssistsReceivedFromPlayer",
                        "externalLinks"
                    ]
                    for field in redundant_fields:
                        player_info.pop(field)

                    for _updates in [
                        {"multikills": multikill},
                        {"adr": adr},
                        {"map_seq": map_seq},
                        {"map_name": map_name},
                        {"objectives": objectives},
                        {"killAssistsReceivedFromPlayer": assisted_by},
                        {"teamkillAssistsReceivedFromPlayer": team_kill_assisted_by},
                        {"team": team_name},
                        {"loadout": player_loadout}]:
                        player_info.update(_updates)

                    players.append(player_info)
        players = sort_and_change_dtype(players, sort_key=lambda x: (x["map_seq"], x["team"], x["name"]))

        return players

    elif granularity == "round":
        games = event["seriesState"]["games"]
        for game in games:
            map_seq = game["sequenceNumber"]
            map_name = game["map"]["name"]
            for round in game["segments"]:
                round_seq = int(round["id"].split("-")[-1])
                teams = round["teams"]

                for team in teams:
                    team_name = team["name"]

                    for _player in team["players"]:
                        player_info = deepcopy(_player)
                        objectives, assisted_by, team_kill_assisted_by = flatten_lists()

                        # Remove useless fields
                        redundant_fields = [
                            "statePath",
                            "killAssistsReceivedFromPlayer",
                            "teamkillAssistsReceivedFromPlayer",
                            "externalLinks"
                        ]
                        for field in redundant_fields:
                            player_info.pop(field)

                        for _updates in [
                            {"round_seq": round_seq},
                            {"map_seq": map_seq},
                            {"map_name": map_name},
                            {"objectives": objectives},
                            {"killAssistsReceivedFromPlayer": assisted_by},
                            {"teamkillAssistsReceivedFromPlayer": team_kill_assisted_by},
                            {"team": team_name}]:
                            player_info.update(_updates)

                        players.append(player_info)
        players = sort_and_change_dtype(players, sort_key=lambda x: (x["map_seq"], x["round_seq"], x["team"], x["name"]))

        return players

def get_player_health_armor(event):
    """ Returns df of players' most updated health and armor values """

    required_fields = ["currentHealth", "currentArmor"]
    default_fields = ["team", "name"]
    players = get_player_state(event, granularity="game").filter(items=(default_fields + required_fields))
    return players.tail(10).reset_index(drop=True)

def get_player_economy(event):
    required_fields = ["money", "inventoryValue", "netWorth"]
    default_fields = ["team", "name"]
    players = get_player_state(event, granularity="game").filter(items=(default_fields + required_fields))
    return players.tail(10).reset_index(drop=True)

def get_player_kdao(event, granularity):
    if granularity == "game":
        required_fields = ["^adr$", "^kills$", "^killAssistsGiven$", "^deaths$", "^multikills$", "objectives.*"]
    else:
        required_fields = ["^kills$", "^killAssistsGiven$", "^deaths$", "objectives.*"]
    default_fields = ["^map_seq$", "^map_name$", "^team$", "^name$"]
    players = get_player_state(event, granularity).filter(regex="|".join(default_fields + required_fields)).fillna(0)
    return players

def get_loadouts(event):
    required_fields = ["loadout.*"]
    default_fields = ["^map_seq$", "^map_name$", "^team$", "^name$"]
    players = get_player_state(event, granularity="game").filter(regex="|".join(default_fields + required_fields))
    return players.tail(10).reset_index(drop=True)

def pkp(event):
    player_name_id_map = {}
    for team in event["seriesState"]["teams"]:
        for _player in team["players"]:
            player_name_id_map[_player["id"]] = _player["name"]
    actor = player_name_id_map[event["actor"]["id"]]
    target = player_name_id_map[event["target"]["id"]]
    action = event["action"]
    weapon = list(event["actor"]["stateDelta"]["series"]["weaponKills"].keys())[0]
    round_time = event["seriesState"]["games"][-1]["clock"]["currentSeconds"]
    minutes = int(round_time/60)
    seconds = round_time % 60
    action_str = f"{minutes}:{seconds:02}     {actor} {action} {target} with {weapon}"
    return actor, target, action, weapon, action_str


    



# Streamlit Visuals
# Top Header Section
event = json.loads(full_events[3315])["events"][-1]


st.title("During Series")
match_date = event["seriesState"]["startedAt"].split("T")[0]
format =event["seriesState"]["format"]

st.subheader(f"Date of Match: {match_date}")
st.write(f"Match format: {format}")
round_num=2

team1 = "ECSTATIC"
team2 = "forZe"

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

# Post Round Tab
post_tab.header(f"Round {round_num}")
round_events = get_team_info(event, granularity="round")
line_chart_df = round_events.drop(["map_seq",'map','won','side','objectives.plantBomb','objectives.explodeBomb','objectives.beginDefuseWithKit','objectives.defuseBomb','objectives.beginDefuseWithoutKit'], axis=1)
with post_tab:
    # data prep for line chart - split df into teams
    line_chart_team1 = line_chart_df[line_chart_df['name'] == "ECSTATIC"].drop(["name"], axis=1)
    line_chart_team2 = line_chart_df[line_chart_df['name'] == "forZe"].drop(["name"], axis=1)
    live_data_team1 = pd.DataFrame()
    live_data_team2 = pd.DataFrame()
    live_data = pd.DataFrame()
    placeholder = st.empty()
    placeholder2 = st.empty()
    json_row_counter = 0
    counter_list = [100,238,357,476,595,714,833,952,1071,1190,1309,1428,1547,1666,1785,1904,2023,2142,2261,2380,2499,2618,2737,
    2856,2975,3094,3213,3332,3451,3570,3689,3808,3927,4046,4165,4284,4403,4522,4641,4760,4879,4998,
    5117,5236,5355,5474,5593,5712,5831,5993]
    round_tracker = 0
    for seconds in range(50):
        row = counter_list[seconds]
        event = json.loads(full_events[row])["events"][-1]

        with placeholder.container():
            st.write(counter_list)
            try:
                map = get_team_info(event, granularity="game").iloc[[-1]]["map"]
            except KeyError:
                event = json.loads(full_events[row])["events"][-2]
                map = get_team_info(event, granularity="game").iloc[[-1]]["map"]

            st.write(map)
            latest_round = line_chart_df.iloc[[round_tracker]]
            round_tracker +=1
            live_data = pd.concat([live_data,latest_round ], ignore_index=True)
            fig2 = px.line(data_frame = live_data,y =live_data['kills'] , x =live_data['round_seq'], color=live_data['name'])
            st.write(fig2)
            time.sleep(0.5)
            # in one loop, grab a random number of lines in the jsonl (e.g 7 lines), get series state of last even of last line.
        
        with placeholder2.container():  
            player_kda = get_player_kdao(event, granularity="game")
            st.write(player_kda)
    