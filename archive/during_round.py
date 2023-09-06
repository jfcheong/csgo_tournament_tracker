import sys
import json
import pandas as pd
from datetime import date
import pandas as pd

import streamlit as st
import streamlit.components.v1 as components
import streamlit_highcharts as hct

from highcharts_core.chart import Chart
from highcharts_core.global_options.shared_options import SharedOptions
from highcharts_core.options import HighchartsOptions
from highcharts_core.options.plot_options.bar import BarOptions
from highcharts_core.options.series.bar import BarSeries

import altair as alt

sys.path.append('../')
from utils import utils


def load_state():
    with open('C:/Users/jfche/Downloads/grid/csgo/CCT-Online-Finals-1/2578928_state.json', 'r') as jsonl_file:
        json_list = list(jsonl_file)
    return json_list

def load_events():
    with open('C:/Users/jfche/Downloads/grid/csgo/CCT-Online-Finals-1/2579089_events.jsonl', 'r') as jsonl_file:
        json_list = list(jsonl_file)
    return json_list

full_events = load_events()
last_event = json.loads(full_events[5346])["events"][-1]

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
    st.text(f"{kda.loc[(kda['name'] == terror_players[0]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

    st.markdown(f"##### Player 2: {terror_players[1]}")
    st.text(f"{kda.loc[(kda['name'] == terror_players[1]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

    st.markdown(f"##### Player 3: {terror_players[2]}")
    st.text(f"{kda.loc[(kda['name'] == terror_players[2]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

    st.markdown(f"##### Player 4: {terror_players[3]}")
    st.text(f"{kda.loc[(kda['name'] == terror_players[3]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

    st.markdown(f"##### Player 5: {terror_players[4]}")
    st.text(f"{kda.loc[(kda['name'] == terror_players[4]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

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
    st.text(f"{kda.loc[(kda['name'] == counter_players[0]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

    st.markdown(f"##### Player 2: {counter_players[1]}")
    st.text(f"{kda.loc[(kda['name'] == counter_players[1]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

    st.markdown(f"##### Player 3: {counter_players[2]}")
    st.text(f"{kda.loc[(kda['name'] == counter_players[2]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

    st.markdown(f"##### Player 4: {counter_players[3]}")
    st.text(f"{kda.loc[(kda['name'] == counter_players[3]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")

    st.markdown(f"##### Player 5: {counter_players[4]}")
    st.text(f"{kda.loc[(kda['name'] == counter_players[4]) & (kda['map_name'] == 'inferno'), ['kills', 'deaths', 'killAssistsGiven']].values[0]}")


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
st.dataframe(kills_df, column_config={"weapon": st.column_config.ImageColumn(label="weapon", width='small')}, hide_index=True)
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
