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
import numpy as np
from collections.abc import Iterable
from highcharts import Highchart


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

#this opens the final files
with open(f'./data/CCT-Online-Finals-1/2579089_state.json', 'r') as json_file:
    finals_file = json.load(json_file)

#this opens the semi-final files
with open(f'./data/CCT-Online-Finals-1/2579048_state.json', 'r') as json_file:
    semifinals_file1 = json.load(json_file)

#this opens the second semi-final files
with open(f'./data/CCT-Online-Finals-1/2578928_state.json', 'r') as json_file:
    semifinals_file2 = json.load(json_file)
 

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
            <h3 style="color:black;font-family:Source Sans Pro;">{final_teams[0]}</h3>
            <img style="height:50px;" src="{ecstatic_url}" />
        </div>
        
        <div style="text-align: center;">
            <h3 style="color:black;">{final_teams[1]}</h3>
            <img style="height:50px;" src="{forze_url}" />
        </div>
    </div>

    """
)

st.subheader("Predicted Winrate")




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
    <div style="padding-bottom:10px">
            <h3 style="color:black;font-family:Source Sans Pro;">{relevant_team} <img style="height:50px;" src="{ecstatic_url}" /></h3> 
        </div>
    <div style="height:200px; background-color:#F0F2F6;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
        <div style="text-align: center;">
            <h3 style="color:black;font-family:Source Sans Pro;">{list(col1_match_score)[0]}</h3>
        </div>

        <div style="text-align: left;">
            <p style="font-size:40px;color:black;font-family:Source Sans Pro;">{col1_match_score[list(col1_match_score)[0]]} - {col1_match_score[list(col1_match_score)[1]]}</p>
        </div>
        
        <div style="text-align: center;">
            <h3 style="color:black;">{list(col1_match_score)[1]}</h3>
        </div>
    </div>
	
    """
    ,height=250)
    
    st.subheader("Players")

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
            'text': 'Player Kill Death Ratio (KDR)'
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
                }
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
    <div style="padding-bottom:10px">
            <h3 style="color:black;font-family:Source Sans Pro;">{relevant_team}  <img style="height:50px;" src="{forze_url}" /></h3>
        
        </div>
    <div style="height:200px; background-color:#F0F2F6;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
        <div style="text-align: center;">
            <h3 style="color:black;font-family:Source Sans Pro;">{list(col2_match_score)[0]}</h3>
        </div>

        <div style="text-align: center;">
            <p style="font-size:40px;color:black;font-family:Source Sans Pro;">{col2_match_score[list(col2_match_score)[0]]} - {col2_match_score[list(col2_match_score)[1]]}</p>
        </div>
        
        <div style="text-align: center;">
            <h3 style="color:black;">{list(col2_match_score)[1]}</h3>
        </div>
    </div>
	
    """
    ,height=250)
    
    st.subheader("Players")
    #retrieve the list of teams in semi finals match and identify the team that has entered finals with player KDR info
    teams = list(match_result.keys())
    team1 = list(set(teams) & set(final_teams))[0]

    kills = get_match_result_per_player(semifinals_file1, key='kills')
    assists = get_match_result_per_player(semifinals_file1, key='killAssistsGiven')
    death = get_match_result_per_player(semifinals_file1, key='deaths')

    sum_of_kd = {}
    kdr={}
    for key, value in kills[team1].items():
        sum_of_kd[key] = value + assists[team1][key]

    for key, value in sum_of_kd.items():
        kdr[key] = round(value / death[team1][key],2)

    player_kdr = list(kdr.values())
    player_name = list(kdr.keys())

    # plotting the bar charts

    options = {
        'chart': {
            'type': 'bar',
            'inverted': 'false'
        },
        'title': {
            'text': 'Player Kill Death Ratio (KDR)'
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
                }
            }
        }
    }
    H = Highchart(height=500)
    H.set_dict_options(options)
    H.add_data_set(player_kdr, 'bar','KDR')
    components.html(H.htmlcontent,height=500)

