import streamlit as st
import pandas as pd
from highcharts_excentis import Highchart
import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import date
import pandas as pd
import numpy as np
from utils import utils


@st.cache_data  
def load_data():
    # simultaneously tracks inventory value per round while iterating to last state for performance optimization
    with open('../CCT-Online-Finals-1/2579089_events.jsonl', 'r') as jsonl_file:
        json_list = list(jsonl_file)
    economy_per_round = []
    for line_item in json_list:
        line_item = json.loads(line_item)
        for event in line_item["events"]:
            try:
                event_type = event["type"]
                if event_type == 'round-ended-freezetime':
                    game = event['seriesState']['games'][-1]
                    round = game['segments'][-1]
                    map_seq = int(game["sequenceNumber"])
                    round_seq = int(round["id"].split("-")[-1])
                    for team in game['teams']:
                        info = {
                            'game': map_seq,
                            'round': round_seq,
                            'name': team['name'],
                            'inventoryValue': team['inventoryValue']
                        }
                        economy_per_round.append(info)
                if event_type == 'tournament-ended-series':
                    return event, economy_per_round
            except Exception as e:
                print(e)
                continue


def get_round_results(event, return_df=False):
    round_wins = []
    for game in event['seriesState']['games']:
        map_seq = int(game["sequenceNumber"])
        for round in game['segments']:
            round_seq = int(round["id"].split("-")[-1])
            for team in round['teams']:
                info = {
                    'game': map_seq,
                    'round': round_seq,
                    'name': team['name'],
                    'won': team['won']
                }
                round_wins.append(info)

    if return_df:
        return pd.json_normalize(round_wins)
    return round_wins


def compute_round_type(row):
    if row['inventoryValue'] < 5000:
        return 'Eco'
    elif row['inventoryValue'] < 10000:
        return 'Light Buy'
    elif row['inventoryValue'] < 20000:
        return 'Half Buy'
    else:
        return 'Full Buy'


def compute_econ_winrate(df):
    df = df[['roundType', 'won']]
    df['lost'] = ~df['won']
    econ_win_rate = df.groupby('roundType').sum()
    econ_win_rate['winrate'] = econ_win_rate['won'] / (econ_win_rate['won'] + econ_win_rate['lost'])
    return econ_win_rate


st.title("Post Series Analysis")

event, economy = load_data()
result = event["seriesState"]
match_date = result["startedAt"].split("T")[0]


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


winning_team = teams_df[teams_df['score'] == 2]['name'].tolist()[0]
losing_team = teams_df[teams_df['score'] == 0]['name'].tolist()[0]


st.subheader(f"Date of Match: {match_date}")
st.write(f"Match format: {format}")

#add part to compute map score instead of hardcoding mapscore
forze_url = "https://preview.redd.it/new-forze-logo-v0-x31u5t3sg8ba1.png?width=600&format=png&auto=webp&s=041b6912e65d06e150219f63f79dc05b911e9c04"
ecstatic_url = "https://img-cdn.hltv.org/teamlogo/Ox1eFAB6o8VM6jwgPbQuks.svg?ixlib=java-2.1.0&s=66680f6d946ff4a93bc311f3bbab8d9e"

components.html(
    f"""
    <div style="height:200px; background-color:#F0F2F6;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
        <div style="text-align: right;">
            <h3 style="color:black; font-family:Segoe UI, Arial, sans-serif">{winning_team}</h3>
            <img style="height:50px;" src="{forze_url}" />
        </div>
        
        <h3 style="color:black;font-size:40px;;text-align: center;font-family:Segoe UI, Arial, sans-serif ">2 - 0</h3>
        <div style="text-align: left;">
            <h3 style="color:black;font-family:Segoe UI, Arial, sans-serif">{losing_team}</h3>
            <img style="height:50px;" src="{ecstatic_url}" />
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
team1_df, team2_df = game_player_stats[game_player_stats['teams.name'] == winning_team], game_player_stats[game_player_stats['teams.name'] == losing_team]
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
round_wins = get_round_results(event, return_df=True)

econ_df = pd.json_normalize(economy)
econ_df['roundType'] = econ_df.apply(compute_round_type, axis=1)
rounds_df = pd.merge(econ_df, round_wins)

team_1_df = rounds_df[rounds_df['name'] == winning_team]
team_1_econ_win_rate_df = compute_econ_winrate(team_1_df)
team_1_econ_win_rate_df['winrate'] = team_1_econ_win_rate_df['winrate'].apply(lambda x: round(x*100,2))
team1_winrate = list(team_1_econ_win_rate_df["winrate"])
team_1_econ_win_rate_df.reset_index(inplace=True)
roundType = list(team_1_econ_win_rate_df["roundType"])

team_2_df = rounds_df[rounds_df['name'] == losing_team]
team_2_econ_win_rate_df = compute_econ_winrate(team_2_df)
team_2_econ_win_rate_df['winrate'] = team_2_econ_win_rate_df['winrate'].apply(lambda x: round(x*100,2))
team2_winrate = list(team_2_econ_win_rate_df["winrate"])

H3 = Highchart(height=400)
h3_options = {
	'title': {
        'text': 'Economy Win rate'
    },

    'xAxis': {
        'categories':roundType,
        'title': {
            'text': None
        }
    },
    'yAxis': {
        'min': 0,
        'title': {
            'text': 'Win-rate Percentage',
            'align': 'high'
        },
        'labels': {
            'overflow': 'justify'
        }
    },
    'tooltip': {
        'valueSuffix': ' %'
    },
    'credits': {
        'enabled': False
    },
    'plotOptions': {
        'bar': {
            'dataLabels': {
                'enabled': True,
                'format': '{y}%'
            }
        }
    }
}

H3.set_dict_options(h3_options)

H3.add_data_set(team1_winrate, 'bar', winning_team)
H3.add_data_set(team2_winrate, 'bar', losing_team)
components.html(H3.htmlcontent,height=400)



#building ADR charts
team1_players = list(team1_df["name"])
team1_ADR = list(team1_df["ADR"])
neg_team1_ADR = []
for num in team1_ADR:
    neg_team1_ADR.append(-num)

team2_players = list(team2_df["name"])
team2_ADR = list(team2_df["ADR"])

H = Highchart(height=400)

options = {
	'chart': {
        'type': 'bar'
    },
    'title': {
        'text': 'Player Average Damage Per Round (ADR)'
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
# hct.streamlit_highcharts(combined_chart,400)
get_kda = utils.get_player_kdao(event,"game")
multikills_df = get_kda[["team","name","multikills"]]

team1_multikills = multikills_df[multikills_df['team'] == winning_team ].drop(["team"], axis=1)
team2_multikills = multikills_df[multikills_df['team'] == losing_team ].drop(["team"], axis=1)
team1_multikills = team1_multikills.groupby(['name']).agg({'multikills':'sum'})
team2_multikills = team2_multikills.groupby(['name']).agg({'multikills':'sum'})

team1_multikills.reset_index(inplace=True)
team2_multikills.reset_index(inplace=True)

t1_multikills_players =  list(team1_multikills["name"])
t1_multikills_kills =  list(team1_multikills["multikills"])

t2_multikills_players =  list(team2_multikills["name"])
t2_multikills_kills =  list(team2_multikills["multikills"])

H1 = Highchart(height=400)
st.subheader(f"Series Multikills - {winning_team}" )
options = {
	'title': {
        'text': 'Player Multikills'
    },
    'subtitle': {
        'text': 'Multikills are when a player kills 3 or more members from the opponent team'
    },
    'xAxis': {
        'categories':t1_multikills_players,
        'title': {
            'text': None
        }
    },
    'yAxis': {
        'min': 0,
        'title': {
            'text': 'Number of Multikills',
            'align': 'high'
        },
        'labels': {
            'overflow': 'justify'
        }
    },
    'tooltip': {
        'valueSuffix': ' multikills'
    },
    'credits': {
        'enabled': False
    },
    'plotOptions': {
        'bar': {
            'dataLabels': {
                'enabled': True
            }
        }
    }
}

H2 = Highchart(height=400)

h2_options = {
	'title': {
        'text': 'Player Multikills'
    },
    'subtitle': {
        'text': 'Multikills are when a player kills 3 or more members from the opponent team'
    },
    'xAxis': {
        'categories':t2_multikills_players,
        'title': {
            'text': None
        }
    },
    'yAxis': {
        'min': 0,
        'title': {
            'text': 'Number of Multikills',
            'align': 'high'
        },
        'labels': {
            'overflow': 'justify'
        }
    },
    'tooltip': {
        'valueSuffix': ' multikills'
    },

    'credits': {
        'enabled': False
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


H1.set_dict_options(options)

H1.add_data_set(t1_multikills_kills, 'bar', winning_team)
H2.set_dict_options(h2_options)

H2.add_data_set(t2_multikills_kills, 'bar', losing_team)

components.html(H1.htmlcontent,height=400)

st.subheader(f"Series Multikills - {losing_team}" )
components.html(H2.htmlcontent,height=400)

st.header("Player Statistics")

games_df = pd.DataFrame(result["games"])
maps = list(games_df["map"])
list_of_maps = ["All Maps"]
for i in range(len(maps)):
    map = (maps[i]['name']).capitalize()
    list_of_maps.append(map)

player_stats_per_round = pd.json_normalize(data=result["games"],
                               record_path=["segments", "teams", "players"],
                               meta=["sequenceNumber",["segments", "id"], ["segments","teams","name"]],meta_prefix="game_")

player_stats_per_round = player_stats_per_round.rename(columns={"game_sequenceNumber":"game", "game_segments.id":"round",'game_segments.teams.name':"teamName"})
player_stats_per_round = player_stats_per_round[["game", "round", "name","alive", "currentHealth", "currentArmor", "kills", "deaths", "damageDealt", "damageTaken"]]

player_stats_per_round = player_stats_per_round.drop(['round', 'alive','currentHealth','currentArmor','damageTaken'], axis=1)


team_stats_per_round = pd.json_normalize(data=result["games"],
                               record_path=["segments", "teams"],
                               meta=["sequenceNumber",["segments", "id"]],meta_prefix="game_")

team_stats_per_round = team_stats_per_round[["game_sequenceNumber", "game_segments.id", "name", "side", "won", "kills","damageDealt", "damageTaken"]]

map_tabs = st.tabs(list_of_maps)
for i in range(len(map_tabs)):
    with map_tabs[i]:
        if i==0:
            st.subheader(f"Team 1 - {winning_team}")
            team1_df = team1_df.drop(['teams.name'], axis=1)
            team1_df.rename(columns = {'name':'Player Name', 'kills':'Kills',
                              'deaths':'Deaths','killAssistsGiven':'Assists'}, inplace = True)
            st.table(team1_df)
            st.subheader(f"Team 2 - {losing_team}")
            team2_df = team2_df.drop(['teams.name'], axis=1)
            team2_df.rename(columns = {'name':'Player Name', 'kills':'Kills',
                              'deaths':'Deaths','killAssistsGiven':'Assists'}, inplace = True)
            st.table(team2_df)
        else:
            map_stats = team_stats_per_round[(team_stats_per_round.game_sequenceNumber==i) & ((team_stats_per_round.won==True))]
            map_score = map_stats['name'].value_counts()

            components.html(
                f"""
                <div style="height:300px;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
                    <div style="text-align: right;">
                        <h3 style="color:black; font-family: Cambria, Georgia, serif;">{winning_team}</h3>
                        <img style="height:50px;" src="{forze_url}" />
                    </div>
                    
                    <div style="display:inline-block;color:black;font-size:40px;;text-align: center;font-family: Cambria, Georgia, serif; ">
                        <span><span style="color:green;">{map_score[winning_team]}</span>
                        <span> - {map_score[losing_team]}</span></span>
                    </div>
                    <div style="text-align: left;">
                        <h3 style="color:black;font-family: Cambria, Georgia, serif;">{losing_team}</h3>
                        <img style="height:50px;" src="{ecstatic_url}" />
                    </div>
                </div>
                
                """
            )
            
            player_stats_per_game = pd.json_normalize(data=result["games"],
                               record_path=["teams","players"],
                               meta=["sequenceNumber", "map",["teams","name"]])
            
            player_stats_per_game = player_stats_per_game[player_stats_per_game['sequenceNumber']==i]
            game_player_stats = player_stats_per_game.groupby(['teams.name','name']).agg({'kills':'sum','deaths':'sum','killAssistsGiven':'sum'})
            game_player_stats['ADR'] = player_adr
            game_player_stats['KDA Ratio'] = (game_player_stats['kills'] + game_player_stats['killAssistsGiven']) / game_player_stats['deaths']
            game_player_stats.reset_index(inplace=True)
            map_team1_df, map_team2_df = game_player_stats[game_player_stats['teams.name'] == winning_team], game_player_stats[game_player_stats['teams.name'] == losing_team]
            

            st.subheader(f"Team 1 - {winning_team}")
            map_team1_df = map_team1_df.sort_values(['kills'], ascending=[False]).drop(["teams.name"],axis=1)
            map_team1_df.rename(columns = {'name':'Player Name', 'kills':'Kills',
                              'deaths':'Deaths','killAssistsGiven':'Assists'}, inplace = True)
            st.table(map_team1_df)

            st.subheader(f"Team 2 - {losing_team}")
            map_team2_df = map_team2_df.sort_values(['kills'], ascending=[False]).drop(["teams.name"],axis=1)
            map_team2_df.rename(columns = {'name':'Player Name', 'kills':'Kills',
                              'deaths':'Deaths','killAssistsGiven':'Assists'}, inplace = True)
            st.table(map_team2_df)
