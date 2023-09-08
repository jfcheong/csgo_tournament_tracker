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
import altair as alt
import json
from datetime import date
import pandas as pd
from copy import deepcopy
import utils


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

event_time1 = '00:59'
event_log1 = 'FaZe Player A planted a bomb at Theta site'
event_time2 = '01:23'
event_log2 = 'FaZe Player B picked up a Deagle'
events_df = pd.DataFrame(columns=['event_time', 'event_log'])
events_df.loc[0] = [event_time1, event_log1]
events_df.loc[1] = [event_time2, event_log2]

kill_time1 = '00:27'
kill_actor1 = 'FaZe Player C + D'
weapon1 = 'https://static.wikia.nocookie.net/cswikia/images/8/80/CSGO_AK-47_Inventory.png/revision/latest?cb=20130813201911'
killed_actor1 = 'Navi Player A'
kill_time2 = '00:49'
weapon2 = 'https://static.wikia.nocookie.net/cswikia/images/f/f3/CSGO_Desert_Eagle_Inventory.png/revision/latest?cb=20130903115839'
kill_actor2 = 'FaZe Player B'
killed_actor2 = 'Navi Player E'
kills_df = pd.DataFrame(columns=['kill_time', 'kill_actor', 'weapon', 'killed_actor'])
kills_df.loc[0] = [kill_time1, kill_actor1, weapon1, killed_actor1]
kills_df.loc[1] = [kill_time2, kill_actor2, weapon2, killed_actor2]

# Streamlit Visuals
# Top Header Section
st.title("During Series")

st.subheader(f"Date of Match: {date}")
st.write(f"Match format: {format}")

components.html(
    f"""
    <div style="height:200px; background-color:#31333F;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
        <div style="text-align: right;">
            <h3 style="color:white;font-family:courier;">{team1}</h3>
            <img style="height:50px;" src="https://img-cdn.hltv.org/teamlogo/Ox1eFAB6o8VM6jwgPbQuks.svg?ixlib=java-2.1.0&s=66680f6d946ff4a93bc311f3bbab8d9e" />
        </div>

        <h3 style="color:white;font-size:40px;font-family:courier;text-align: center; ">2 - 0</h3>
        <div style="text-align: left;">
            <h3 style="color:white;font-family:courier;">{team2}</h3>
            <img style="height:50px;" src="https://preview.redd.it/new-forze-logo-v0-x31u5t3sg8ba1.png?width=600&format=png&auto=webp&s=041b6912e65d06e150219f63f79dc05b911e9c04" />
        </div>
    </div>

    """
)

# Tabs
preround_tab, duringround_tab, postround_tab = st.tabs(["Pre-Round", "During Round", "Post-Round"])

# Pre-Round Tab
with preround_tab:
    st.header(f"Round {round_num}")

# During Round Tab
with (duringround_tab):
    pha = utils.get_player_health_armor(last_event)
    kda = utils.get_player_kdao(last_event, 'game')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Kills", divider='rainbow')

        kill_log_list = []
        for line in full_events[:1000]:
            content = json.loads(line)
            for event in content["events"]:
                if event["type"] == "player-killed-player":
                    event_str = utils.pkp(event)[-1]
                    kill_list = [event_str]
                    kill_log_list.append(kill_list)

        kill_log_list.sort(reverse=True)
        kills_df = pd.DataFrame(kill_log_list, columns=['kill_log'])
        st.dataframe(kills_df, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Objectives", divider='rainbow')

        # obj_log_list = []
        # for line in full_events[:1000]:
        #     content = json.loads(line)
        #     for event in content["events"]:
        #         if event["action"] == "completed":
        #             event_str = utils.pkp(event)[-1]
        #             obj_list = [event_str]
        #             obj_log_list.append(obj_list)
        #
        # obj_log_list.sort(reverse=True)
        # obj_df = pd.DataFrame(obj_log_list, columns=['objective_log'])
        # st.dataframe(obj_df, hide_index=True, use_container_width=True)

    st.subheader("Players' Info", divider='rainbow')

    col_terror, col_counter = st.columns(2)

    with (col_terror):
        st.markdown("#### Terrorists")
        pha_filtered = pha.loc[pha['team'] == 'ECSTATIC'].reset_index()
        df_t = pha_filtered.set_index('name')
        df_t = pha_filtered.pivot(index="name", columns="team", values=['currentHealth', 'currentArmor']).reset_index()
        bar_chart_day = alt.Chart(df_t).transform_fold(['currentHealth', 'currentArmor']) \
            .mark_bar(clip=True).encode(x=alt.X('value:Q', stack='zero', scale=alt.Scale(domain=(0, 100)), title=''),
                                        y=alt.Y('name', title=''),
                                        color=alt.Color('key:N').legend(None),
                                        ).properties(width=300, height=200)
        bar_chart_day
        st.table(df_t)

        terror_players = []
        for i in range(len(pha_filtered)):
            terror_players.append(pha_filtered.loc[i, 'name'])

        st.markdown(f"##### Player 1: {terror_players[0]}")
        st.text(
            f"{kda.loc[(kda['name'] == terror_players[0]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

        st.markdown(f"##### Player 2: {terror_players[1]}")
        st.text(
            f"{kda.loc[(kda['name'] == terror_players[1]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

        st.markdown(f"##### Player 3: {terror_players[2]}")
        st.text(
            f"{kda.loc[(kda['name'] == terror_players[2]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

        st.markdown(f"##### Player 4: {terror_players[3]}")
        st.text(
            f"{kda.loc[(kda['name'] == terror_players[3]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

        st.markdown(f"##### Player 5: {terror_players[4]}")
        st.text(
            f"{kda.loc[(kda['name'] == terror_players[4]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

    with (col_counter):
        st.markdown("#### Counter Terrorists")
        pha_filtered = pha.loc[pha['team'] == 'forZe'].reset_index()
        df_t = pha_filtered.set_index('name')
        df_t = pha_filtered.pivot(index="name", columns="team", values=['currentHealth', 'currentArmor']).reset_index()
        bar_chart_day = alt.Chart(df_t).transform_fold(['currentHealth', 'currentArmor']) \
            .mark_bar(clip=True).encode(x=alt.X('value:Q', stack='zero', scale=alt.Scale(domain=(0, 100)), title=''),
                                        y=alt.Y('name', title=''),
                                        color=alt.Color('key:N').legend(None),
                                        ).properties(width=300, height=200)
        bar_chart_day
        st.table(df_t)

        counter_players = []
        for i in range(len(pha_filtered)):
            counter_players.append(pha_filtered.loc[i, 'name'])

        # kda['kda'] = kda.loc[:, ['kills', 'deaths', 'killAssistsGiven']].apply(lambda x: '/'.join(x.dropna().values.tolist()), axis=1)
        # st.dataframe(kda)

        st.markdown(f"##### Player 1: {counter_players[0]}")
        st.text(
            f"{kda.loc[(kda['name'] == counter_players[0]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

        st.markdown(f"##### Player 2: {counter_players[1]}")
        st.text(
            f"{kda.loc[(kda['name'] == counter_players[1]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

        st.markdown(f"##### Player 3: {counter_players[2]}")
        st.text(
            f"{kda.loc[(kda['name'] == counter_players[2]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

        st.markdown(f"##### Player 4: {counter_players[3]}")
        st.text(
            f"{kda.loc[(kda['name'] == counter_players[3]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

        st.markdown(f"##### Player 5: {counter_players[4]}")
        st.text(
            f"{kda.loc[(kda['name'] == counter_players[4]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

    # # Dummy Variables
    # team1='TeamA'
    # team2='TeamB'
    # round_num=2
    #
    # event_time1 = '00:59'
    # event_log1 = 'FaZe Player A planted a bomb at Theta site'
    # event_time2 = '01:23'
    # event_log2 = 'FaZe Player B picked up a Deagle'
    # events_df = pd.DataFrame(columns=['event_time', 'event_log'])
    # events_df.loc[0] = [event_time1, event_log1]
    # events_df.loc[1] = [event_time2, event_log2]
    #
    kill_time1 = '00:27'
    kill_actor1 = 'FaZe Player C + D'
    weapon1 = 'https://static.wikia.nocookie.net/cswikia/images/8/80/CSGO_AK-47_Inventory.png'
    killed_actor1 = 'Navi Player A'
    kill_time2 = '00:49'
    weapon2 = 'https://static.wikia.nocookie.net/cswikia/images/f/f3/CSGO_Desert_Eagle_Inventory.png'
    kill_actor2 = 'FaZe Player B'
    killed_actor2 = 'Navi Player E'
    kills_df = pd.DataFrame(columns=['kill_time', 'kill_actor', 'weapon', 'killed_actor'])
    kills_df.loc[0] = [kill_time1, kill_actor1, weapon1, killed_actor1]
    kills_df.loc[1] = [kill_time2, kill_actor2, weapon2, killed_actor2]
    #
    #
    # # Round Status
    # st.markdown(f"## Round {round_num}")
    #
    # # Events Log
    # st.subheader("Latest Events", divider='rainbow')
    # st.dataframe(events_df, hide_index=True)
    #
    # # Kills Log
    st.subheader("All Kills", divider='rainbow')
    st.dataframe(kills_df, column_config={"weapon": st.column_config.ImageColumn(label="weapon", width='small')},
                 hide_index=True)
    #
    # # Player Health Log
    # st.subheader("Players' Stats", divider='rainbow')
    # col1, col2 = st.columns(2)
    # col1.markdown("### Terrorists")
    # df_t = pha.set_index('name')
    # df_t = pha.pivot(index="name", columns="team", values=['currentHealth', 'currentArmor']).reset_index()
    # bar_chart_day = alt.Chart(df_t).transform_fold(['currentHealth', 'currentArmor']) /
    #     .mark_bar(clip=True).encode(x=alt.X('value:Q', stack='zero', scale=alt.Scale(domain=(0, 100))),
    #                                 y=alt.Y('name'), color='key:N')
    # bar_chart_day
    # st.table(df_t)
    # col2.markdown("### Counter Terrorists")


# Post Round Tab
with postround_tab:
    st.header(f"Round {round_num}")
