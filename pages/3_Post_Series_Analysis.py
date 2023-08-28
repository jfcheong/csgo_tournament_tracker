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


st.title("Post Series Analysis")


with open(f'../CCT-Online-Finals-1/2578928_state.json', 'r') as json_file:
    result = json.load(json_file)

date = result["startedAt"].split("T")[0]
format =result["format"]

teams_df = pd.DataFrame(result["teams"])
team_objectives = pd.json_normalize(data=result["teams"],
                               record_path=["objectives"],
                               meta=["name"])

team_objectives = team_objectives.pivot_table('completionCount', ["name"], "type").reset_index()
teams_df = teams_df.merge(team_objectives, on="name")

teams_df = teams_df[['name', 'score', 'won', 'kills',
       'killAssistsReceived', 'killAssistsGiven',
       'teamkills', 'teamkillAssistsReceived', 'teamkillAssistsGiven',
       'weaponTeamkills', 'selfkills',
       'deaths','headshots', 'teamHeadshots', "beginDefuseWithKit", "beginDefuseWithoutKit","defuseBomb","explodeBomb","plantBomb"]]

winning_team = teams_df[teams_df['score'] == 1]['name'].tolist()[0]
losing_team = teams_df[teams_df['score'] == 0]['name'].tolist()[0]

st.subheader(f"Date of Match: {date}")
st.write(f"Match format: {format}")

components.html(
    f"""
    <div style="height:200px; background-color:#31333F;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
        <div style="text-align: right;">
            <h3 style="color:white;font-family:Source Sans Pro;">{winning_team}</h3>
            <img style="height:50px;" src="https://img-cdn.hltv.org/teamlogo/Ox1eFAB6o8VM6jwgPbQuks.svg?ixlib=java-2.1.0&s=66680f6d946ff4a93bc311f3bbab8d9e" />
        </div>
        
        <h3 style="color:white;font-size:40px;;text-align: center; ">2 - 0</h3>
        <div style="text-align: left;">
            <h3 style="color:white;">{losing_team}</h3>
            <img style="height:50px;" src="https://preview.redd.it/new-forze-logo-v0-x31u5t3sg8ba1.png?width=600&format=png&auto=webp&s=041b6912e65d06e150219f63f79dc05b911e9c04" />
        </div>
    </div>
	
    """
)

players_df = pd.json_normalize(data=result["teams"],
                               record_path=["players"],
                               meta=["name"],
                               meta_prefix='team_')
player_objectives = pd.json_normalize(data=result["teams"],
                               record_path=["players", "objectives"],
                               meta=["name", ["players", "name"]])

player_objectives = player_objectives.pivot_table('completionCount', ["name", "players.name"], "type").reset_index()\
                                    .rename(columns={"name":"team_name", "players.name":"name"})

players_df = players_df.merge(player_objectives, on=['name','team_name'])
players_df[["team_name","name" ,"kills","teamkillAssistsGiven", "teamkills", "selfkills", "deaths", "headshots","beginDefuseWithKit", "beginDefuseWithoutKit","defuseBomb","explodeBomb","plantBomb"]]\
    .sort_values(by="kills", ascending=False)

player_stats_per_round = pd.json_normalize(data=result["games"],
                               record_path=["segments", "teams", "players"],
                               meta=["sequenceNumber",["segments", "id"], ["segments","teams","name"]],meta_prefix="game_")
player_stats_per_round = player_stats_per_round.rename(columns={"game_sequenceNumber":"game", "game_segments.id":"round",'game_segments.teams.name':"teamName"})

player_adr = player_stats_per_round.groupby(['teamName','name']).agg({'damageDealt':'mean'})
player_adr.rename(columns={'damageDealt':'ADR'})

player_stats_per_game = pd.json_normalize(data=result["games"],
                               record_path=["teams","players"],
                               meta=["sequenceNumber", "map",["teams","name"]])

game_player_stats = player_stats_per_game.groupby(['teams.name','name']).agg({'kills':'sum','deaths':'sum','killAssistsGiven':'sum'})
game_player_stats['ADR'] = player_adr

game_player_stats['KDA Ratio'] = (game_player_stats['kills'] + game_player_stats['killAssistsGiven']) / game_player_stats['deaths']
game_player_stats.reset_index(inplace=True)

team1_df, team2_df = game_player_stats[game_player_stats['teams.name'] == "ECSTATIC"], game_player_stats[game_player_stats['teams.name'] == "forZe"]
team1_df = team1_df.sort_values(['ADR'], ascending=[False])
team2_df = team2_df.sort_values(['ADR'], ascending=[False])

st.header("Series MVP")
mvp_info = list(team1_df.iloc[0])
mvp_name,mvp_kills,mvp_death,mvp_assist,mvp_adr,mvp_kdr=mvp_info[1],mvp_info[2],mvp_info[3],mvp_info[4],round(mvp_info[5],2),round(mvp_info[6],2)
col1, col2 = st.columns([2, 3])
with col1:
    st.image("data:image/jpeg;base64,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")
    
with col2:
    st.subheader(mvp_name)
    kd_diff = int(mvp_kills-mvp_death)
    st.write(f'ADR - {mvp_adr}   |   KDR - {mvp_kdr}')
    st.metric(label="Kills / Death / Assists", value=f"{mvp_kills} / {mvp_death} / {mvp_assist}", delta=kd_diff)

st.header("Economy Winrate")


st.header("Player Statistics")
st.subheader(f"Team 1 - {winning_team}")
st.table(team1_df)
st.subheader(f"Team 2 - {losing_team}")

st.table(team2_df)

#building ADR charts
team1_players = list(team1_df["name"])
team1_ADR = list(team1_df["ADR"])
neg_team1_ADR = []
for num in team1_ADR:
    neg_team1_ADR.append(-num)

team2_players = list(team2_df["name"])
team2_ADR = list(team2_df["ADR"])

team1_data = []
team2_data = []


for i in range(len(team1_players)):
    t1_oneplayer = {}
    t2_oneplayer = {}
    t1_oneplayer["name"] = team1_players[i]
    t1_oneplayer["y"] = round(team1_ADR[i],2)
    t2_oneplayer["name"] = team2_players[i]
    t2_oneplayer["y"] = round(team2_ADR[i],2)

    team1_data.append(t1_oneplayer)
    team2_data.append(t2_oneplayer)

team1_chart={ 'accessibility': { 'announceNewData': { 'enabled': True}},
  'chart': {'type': 'bar'},
  'legend': {'enabled': False},
  'series': [ { 'colorByPoint': True,
                'data': team1_data,
                'name': 'ADR'}],
  'title': { 'align': 'left',
             'text': f"{winning_team} Players Match Average Damage Per Round (ADR)"},
  'xAxis': {'type': 'category'},
  'yAxis': { 'title': { 'text': 'ADR'}},
  'plotOptions': {
        'bar': {
            'dataLabels': {
                'enabled': 'true'
            },
            'groupPadding': 0.1
        }
    },
  }

team2_chart={ 'accessibility': { 'announceNewData': { 'enabled': True}},
  'chart': {'type': 'bar'},
  'legend': {'enabled': False},
  'series': [ { 'colorByPoint': True,
                'data': team2_data,
                'name': 'ADR'}],
  'title': { 'align': 'left',
             'text': f"{losing_team} Players Match Average Damage Per Round (ADR)"},
  'xAxis': {'type': 'category'},
  'yAxis': { 'title': { 'text': 'ADR'}},
  'plotOptions': {
        'bar': {
            'dataLabels': {
                'enabled': 'true'
            },
            'groupPadding': 0.1
        }
    },
  }

#trying side by side chart
from collections.abc import Iterable
from highcharts import Highchart
combined_chart={ 'accessibility': { 'announceNewData': { 'enabled': True}},
  'chart': {'type': 'bar'},
  'legend': {'enabled': True},
  'series': [ { 
                'data': neg_team1_ADR,
                'name': winning_team},
                
                { 
                'data': team2_ADR,
                'name': losing_team}],

  'title': { 'align': 'left',
             'text': "Players Match Average Damage Per Round (ADR)"},
  'xAxis': [{'categories': team1_players,'reversed': 'false', 'labels':{'step':1},'accessibility':{'description':'losing team'}},
            {'opposite': 'true','reversed': 'false','categories': team2_players, 'linkedTo': 0,'labels':{'step':1}, 'accessibility':{'description':'winning team'}}],
  'yAxis': { 'title': { 'text': 'ADR'}},
  'plotOptions': {
        'series': {
            'stacking': 'normal',
            'borderRadius': '100%'
        },
        'bar': {
            'dataLabels': {
                'enabled': 'true',
                'format':'<b>{point.y:.2f}</b> '
            },
            'groupPadding': 0.1
        }
    },
    
    
  }

from highcharts import Highchart
H = Highchart(height=400)

options = {
	'chart': {
        'type': 'bar'
    },
    'title': {
        'text': 'Players Match Average Damage Per Round (ADR)'
    },

    'xAxis': [{
        'categories': team1_players,
        'reversed': False,
        'labels': {
            'step': 1
        }
    }, { 
        'opposite': True,
        'reversed': False,
        'categories': team2_players,
        'linkedTo': 0,
        'labels': {
            'step': 1
        }
    }],
    'yAxis': {
        'title': {
            'text': None
        },
        'labels': {
            'formatter': "function () {\
                                    return (Math.abs(this.value));\
                                }"
        },
    },

    'plotOptions': {
        'series': {
            'stacking': 'normal'
        }
    },

    'tooltip': {
        'formatter': "function () {\
                            return '<b>' + this.series.name + '</b><br> ' + this.point.category + '<br/>' +\
                                'ADR: ' + Highcharts.numberFormat(Math.abs(this.point.y), 2);\
                        }"
    },
}

H.set_dict_options(options)
H.add_data_set(neg_team1_ADR, 'bar', f'{winning_team}')
H.add_data_set(team2_ADR, 'bar', f'{losing_team}')

st.header("Team Comparison")
components.html(H.htmlcontent,height=400)
hct.streamlit_highcharts(combined_chart,400)

