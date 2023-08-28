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


with open(f'./CCT-Online-Finals-1/2578928_state.json', 'r') as json_file:
    result = json.load(json_file)

date = result["startedAt"].split("T")[0]
format =result["format"]
st.subheader(f"Date of Match: {date}")
st.write(f"Match format: {format}")

components.html(
    """
    <div style="height:200px; background-color:#31333F;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
        <div style="text-align: right;">
            <h3 style="color:white;">ECSTATIC</h3>
            <img style="height:50px;" src="https://img-cdn.hltv.org/teamlogo/Ox1eFAB6o8VM6jwgPbQuks.svg?ixlib=java-2.1.0&s=66680f6d946ff4a93bc311f3bbab8d9e" />
        </div>
        
        <h3 style="color:white;font-size:40px;;text-align: center; ">2 - 0</h3>
        <div style="text-align: left;">
            <h3 style="color:white;">forZe</h3>
            <img style="height:50px;" src="https://preview.redd.it/new-forze-logo-v0-x31u5t3sg8ba1.png?width=600&format=png&auto=webp&s=041b6912e65d06e150219f63f79dc05b911e9c04" />
        </div>
    </div>
	
    """
)

st.subheader("Series MVP")

teams_df = pd.DataFrame(result["teams"])
team_objectives = pd.json_normalize(data=result["teams"],
                               record_path=["objectives"],
                               meta=["name"])

team_objectives = team_objectives.pivot_table('completionCount', ["name"], "type").reset_index()
teams_df = teams_df.merge(team_objectives, on="name")

teams_df[['name', 'score', 'won', 'kills',
       'killAssistsReceived', 'killAssistsGiven',
       'teamkills', 'teamkillAssistsReceived', 'teamkillAssistsGiven',
       'weaponTeamkills', 'selfkills',
       'deaths','headshots', 'teamHeadshots', "beginDefuseWithKit", "beginDefuseWithoutKit","defuseBomb","explodeBomb","plantBomb"]]

winning_team = teams_df[teams_df['score'] == 1]['name'].tolist()[0]
losing_team = teams_df[teams_df['score'] == 0]['name'].tolist()[0]


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


st.header("Player Statistics")

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
st.subheader(f"Team 1 - {winning_team}")
team1_df = team1_df.sort_values(['ADR'], ascending=[False])
st.table(team1_df)
st.subheader(f"Team 2 - {losing_team}")
team2_df = team2_df.sort_values(['ADR'], ascending=[False])
st.table(team2_df)

#building ADR charts
team1_players = list(team1_df["name"])
team1_ADR = list(team1_df["ADR"])

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
            'borderRadius': '90%',
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
            'borderRadius': '90%',
            'dataLabels': {
                'enabled': 'true'
            },
            'groupPadding': 0.1
        }
    },
  }

st.header("Team Comparison")

col1, col2 = st.columns(2)
with col1:
    hct.streamlit_highcharts(team1_chart,400)
with col2:
    hct.streamlit_highcharts(team2_chart,400)