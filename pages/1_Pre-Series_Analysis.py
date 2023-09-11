import streamlit as st
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import json
from datetime import date
import pandas as pd
import numpy as np
from highcharts_excentis import Highchart
import keras
import numpy as np
from utils import utils
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

st.set_page_config(page_title="CSGO Pre-Series Analysis", page_icon=":gun:", 
    layout="wide", initial_sidebar_state="auto", menu_items=None)

st.title("Upcoming Series")

def get_match_date(state_dict):
    return state_dict['startedAt']

def get_match_result(state_dict, key):
    teams = state_dict['teams']
    result_dict = {}
    for team in teams:
        team_name = team['name']
        value = team[key]
        result_dict[team_name] = value
    return result_dict

def get_winning_teams(result_dict_lst):
    # Pass in outputs from get_match_result() in a list
    winning_teams = []
    for result_dict in result_dict_lst:
        for team_name, won in result_dict.items():
            if won:
                winning_teams.append(team_name)
    return winning_teams



def get_match_result_per_player(state_dict, key):
    teams = state_dict['teams']
    result_dict = {}
    for team in teams:
        team_name = team['name']
        player_dict = {}
        for player in team['players']:
            player_name = player['name']
            value = player[key]
            player_dict[player_name] = value
        result_dict[team_name] = player_dict
    return result_dict

def get_match_score(state_dict):
    games_df = pd.DataFrame(state_dict["games"])
    maps = list(games_df["map"])
    match_score = {}
    team1_counter =0
    team2_counter = 0
    team_stats_per_round = pd.json_normalize(data=state_dict["games"],
                                record_path=["segments", "teams"],
                                meta=["sequenceNumber",["segments", "id"]],meta_prefix="game_")
    team_stats_per_round = team_stats_per_round[["game_sequenceNumber", "game_segments.id", "name", "side", "won", "kills","damageDealt", "damageTaken"]]
    for i in range(len(maps)):
        map_stats = team_stats_per_round[(team_stats_per_round.game_sequenceNumber==i+1) & ((team_stats_per_round.won==True))]
        map_score = map_stats['name'].value_counts()
        map_winner = map_score.idxmax()
        map_loser = map_score.idxmin()
        if map_winner in match_score:
            match_score[map_winner] +=1
        else:
            match_score[map_winner] = team1_counter + 1
        match_score[map_loser] = team2_counter 

    return match_score

@st.cache_data  # 👈 Add the caching decorator
def load_events():
    url = "https://github.com/grid-esports/datajam-2023/raw/master/data_files/csgo.zip?download="
    with urlopen(url) as zipresp:
        zip_file = ZipFile(BytesIO(zipresp.read()))
    files = zip_file.namelist()
    with zip_file.open("csgo/CCT-Online-Finals-1/2579089_state.json", "r") as json_file:
        finals_file = json.load(json_file)
    with zip_file.open("csgo/CCT-Online-Finals-1/2579048_state.json", "r") as json_file:
        semifinals_file1 = json.load(json_file)
    with zip_file.open("csgo/CCT-Online-Finals-1/2578928_state.json", "r") as json_file:
        semifinals_file2 = json.load(json_file)
    return [finals_file,semifinals_file1,semifinals_file2]


# #this opens the final files
# with open(f'./data/CCT-Online-Finals-1/2579089_state.json', 'r') as json_file:
#     finals_file = json.load(json_file)

# #this opens the semi-final files
# with open(f'./data/CCT-Online-Finals-1/2579048_state.json', 'r') as json_file:
#     semifinals_file1 = json.load(json_file)

# #this opens the second semi-final files
# with open(f'./data/CCT-Online-Finals-1/2578928_state.json', 'r') as json_file:
#     semifinals_file2 = json.load(json_file)

finals_file,semifinals_file1,semifinals_file2 = load_events()[0],load_events()[1],load_events()[2]

match_date = finals_file["startedAt"].split("T")[0]
st.subheader(f"Date of Match: {match_date}")
match_result = get_match_result(finals_file, key='score')
semis_match_result1 = get_match_result(semifinals_file1, key='score')
semis_match_result2 = get_match_result(semifinals_file2, key='score')

final_teams = list(match_result.keys())

forze_url = "https://preview.redd.it/new-forze-logo-v0-x31u5t3sg8ba1.png?width=600&format=png&auto=webp&s=041b6912e65d06e150219f63f79dc05b911e9c04"
ecstatic_url = "https://img-cdn.hltv.org/teamlogo/Ox1eFAB6o8VM6jwgPbQuks.svg?ixlib=java-2.1.0&s=66680f6d946ff4a93bc311f3bbab8d9e"

components.html(
    f"""
    <div style="height:200px; background-color:#F0F2F6;display: grid;column-gap: 2%;grid-template-columns: auto auto;padding: 10px;">
        <div style="text-align: center;">
            <h3 style="color:black;font-family:sans-serif">{final_teams[0]}</h3>
            <img style="height:50px;" src="{ecstatic_url}" />
        </div>
        
        <div style="text-align: center;">
            <h3 style="color:black;font-family:sans-serif">{final_teams[1]}</h3>
            <img style="height:50px;" src="{forze_url}" />
        </div>
    </div>

    """
)

st.subheader("Predicted Winrate")

team1 = final_teams[0]
team2 = final_teams[1]



game_1, game_2 = finals_file['games']

stats_df = pd.read_csv(f"./model/agg_player_stats.csv").set_index(['teamName', 'name', 'side'])

game1_features = utils.compute_features(stats_df, game_1['teams'])
game2_features = utils.compute_features(stats_df, game_2['teams'])
features = utils.combine_and_pivot([game1_features,game2_features])

model = keras.models.load_model(f"./model/csgo_game_prediction_model.h5")
probas = model.predict(features)
average_prob = np.average(probas, axis=0)

team1_wr = f"{average_prob[0]:.2%}"
team2_wr = f"{average_prob[1]:.2%}"


fig = go.Figure()
fig.add_trace(go.Bar(
    y=['Predicted Winrate'],
    x=[team1_wr],
    name=team1,
    orientation='h',
    text=f"{team1_wr}%",
    textposition="inside",
    hoverinfo='none',
    marker=dict(
        color='#7CB5EC',
        line=dict(color='#7CB5EC', width=1)
    )
))
fig.add_trace(go.Bar(
    y=['Predicted Winrate'],
    x=[team2_wr],
    name=team2,
    orientation='h',
    text=f"{team2_wr}%",
    hoverinfo='none',
    marker=dict(
        color='#434348',
        line=dict(color='#434348', width=1)
    )
))

fig.update_layout(
    height=70,
    font_family="Sans-serif",
    font_size = 15,
    margin=dict(l=0,r=0,b=0,t=0),
    xaxis=dict(showgrid=False,
        showline=False,
        showticklabels=False,
        zeroline=False,
        domain=[0.15, 1]),
        
    yaxis=dict(showgrid=False,
        showline=False,
        showticklabels=False,
        zeroline=False,
        domain=[0.15, 1]),
)

fig.update_layout(barmode='stack')
st.plotly_chart(fig, use_container_width=True)


st.subheader("Game History")

col1, col2 = st.columns(2)
with col1:
    col1_final_team = final_teams[0]
    semis_teams2 = list(semis_match_result2.keys())
    for team in semis_teams2:
        if team == col1_final_team:
            relevant_team = team
    
    #a function to retrieve match score
    col1_match_score = get_match_score(semifinals_file2)

    components.html(
    f"""
    <div style="padding-bottom:10px;text-align:center">
            <h3 style="color:black;font-family:sans-serif">{relevant_team} <img style="height:50px;" src="{ecstatic_url}" /></h3> 
        </div>
    <div style="height:200px; background-color:#F0F2F6;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
        <div style="text-align: center;">
            <h4 style="color:black;font-family:sans-serif">{list(col1_match_score)[0]}</h4>
        </div>

        <div style="text-align: left;">
            <p style="font-size:40px;color:black;font-family:sans-serif">{col1_match_score[list(col1_match_score)[0]]} - {col1_match_score[list(col1_match_score)[1]]}</p>
        </div>
        
        <div style="text-align: center;">
            <h4 style="color:black;font-family:sans-serif">{list(col1_match_score)[1]}</h4>
        </div>
    </div>
	
    """
    ,height=250)
    
    kills = get_match_result_per_player(semifinals_file2, key='kills')
    assists = get_match_result_per_player(semifinals_file2, key='killAssistsGiven')
    death = get_match_result_per_player(semifinals_file2, key='deaths')

    sum_of_kd = {}
    kdr={}
    for key, value in kills[relevant_team].items():
        sum_of_kd[key] = value + assists[relevant_team][key]

    for key, value in sum_of_kd.items():
        kdr[key] = round(value / death[relevant_team][key],2)

    player_kdr = list(kdr.values())
    player_name = list(kdr.keys())

    # plotting the bar charts

    options = {
        'chart': {
            'type': 'bar',
            'inverted': 'false'
        },
        'title': {
            'text': 'Player Kill Death Assist Ratio (KDR)'
        },
        'xAxis': {
            'categories': player_name,
            'title': {
                'text': None
            }
        },
        'yAxis': {
            'min': 0,
            'title': {
                'text': 'Kill Death Ratio',
                'align': 'high'
            },
            'labels': {
                'overflow': 'justify'
            }
        },
        'tooltip': {
            'valueSuffix': ''
        },


        'plotOptions': {
            'bar': {
                'dataLabels': {
                    'enabled': True
                },
                'color':'#434348'
            }
        }
    }
    H = Highchart(height=500)
    H.set_dict_options(options)
    H.add_data_set(player_kdr, 'bar','KDR')
    components.html(H.htmlcontent,height=500)



with col2:
    col2_final_team = final_teams[1]
    semis_teams1 = list(semis_match_result1.keys())
    for team in semis_teams1:
        if team == col2_final_team:
            relevant_team = team
    

    #a function to retrieve match score
    col2_match_score = get_match_score(semifinals_file1)

    components.html(
    f"""
    <div style="padding-bottom:10px; text-align:center">
            <h3 style="color:black; font-family:sans-serif;">{relevant_team}  <img style="height:50px;" src="{forze_url}" /></h3>
        
        </div>
    <div style="height:200px; background-color:#F0F2F6;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
        <div style="text-align: center;">
            <h4 style="color:black;font-family:sans-serif;">{list(col2_match_score)[0]}</h4>
        </div>

        <div style="text-align: center;">
            <p style="font-size:40px;color:black;font-family:sans-serif;">{col2_match_score[list(col2_match_score)[0]]} - {col2_match_score[list(col2_match_score)[1]]}</p>
        </div>
        
        <div style="text-align: center;">
            <h4 style="color:black;font-family:sans-serif;">{list(col2_match_score)[1]}</h4>
        </div>
    </div>
	
    """
    ,height=250)

    kills = get_match_result_per_player(semifinals_file1, key='kills')
    assists = get_match_result_per_player(semifinals_file1, key='killAssistsGiven')
    death = get_match_result_per_player(semifinals_file1, key='deaths')

    sum_of_kd = {}
    kdr={}
    for key, value in kills[relevant_team].items():
        sum_of_kd[key] = value + assists[relevant_team][key]

    for key, value in sum_of_kd.items():
        kdr[key] = round(value / death[relevant_team][key],2)

    player_kdr = list(kdr.values())
    player_name = list(kdr.keys())


    # plotting the bar charts

    options = {
        'chart': {
            'type': 'bar',
            'inverted': 'false'
        },
        'title': {
            'text': 'Player Kill Death Assist Ratio (KDR)'
        },
        'xAxis': {
            'categories': player_name,
            'title': {
                'text': None
            }
        },
        'yAxis': {
            'min': 0,
            'title': {
                'text': 'Kill Death Ratio',
                'align': 'high'
            },
            'labels': {
                'overflow': 'justify'
            }
        },
        'tooltip': {
            'valueSuffix': ''
        },


        'plotOptions': {
            'bar': {
                'dataLabels': {
                    'enabled': True
                },
                
            }
        }
    }
    H = Highchart(height=500)
    H.set_dict_options(options)
    H.add_data_set(player_kdr, 'bar','KDR')
    components.html(H.htmlcontent,height=500)

