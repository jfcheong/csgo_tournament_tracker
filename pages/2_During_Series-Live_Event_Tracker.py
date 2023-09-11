import sys
import json
from datetime import date
import time
import pandas as pd
from pandas.api.types import is_float_dtype
import re
import streamlit as st
import streamlit.components.v1 as components
from highcharts_excentis import Highchart
import altair as alt
import plotly.express as px  # interactive charts
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import json

sys.path.append('../')
from utils import utils

st.set_page_config(page_title="CSGO Live Event Tracker", page_icon=":gun:",
    layout="wide", initial_sidebar_state="auto", menu_items=None)

# Load events jsonl file
def load_state():
    with open('../CCT-Online-Finals-1/2578928_state.json', 'r') as json_file:
        state = json.load(json_file)
    return state

@st.cache_data  # 👈 Add the caching decorator
def load_events():
    with open('../CCT-Online-Finals-1/2579089_events.jsonl', 'r') as jsonl_file:
        json_list = list(jsonl_file)
    return json_list


# @st.cache_data  # 👈 Add the caching decorator
# def load_state():
#     url = "https://github.com/grid-esports/datajam-2023/raw/master/data_files/csgo.zip?download="
#     with urlopen(url) as zipresp:
#         zip_file = ZipFile(BytesIO(zipresp.read()))
#     with zip_file.open("csgo/CCT-Online-Finals-1/2578928_state.json", "r") as json_file:
#         state = json.load(json_file)
#     return state
#
# @st.cache_data  # 👈 Add the caching decorator
# def load_events():
#     url = "https://github.com/grid-esports/datajam-2023/raw/master/data_files/csgo.zip?download="
#     with urlopen(url) as zipresp:
#         zip_file = ZipFile(BytesIO(zipresp.read()))
#     with zip_file.open("csgo/CCT-Online-Finals-1/2579089_events.jsonl", "r") as json_file:
#         json_list = list(json_file)
#     return json_list

# Load data
full_events = load_events()
state = load_state()

# Round data
## List of event IDs for Round 2
r2_eid_preround_list = ['3bb88790-d6b5-4944-b6df-b3663330c2ff', '0333e6f5-dd8e-4f93-9dca-713fd474695a', '1b9802ec-a935-42c0-8396-83a7a3768d2c', 'e2f57ccd-7882-4337-b125-b203a398721e', '3b1adf9f-98d2-49dd-94e8-09c51ef027a9', 'f730a1d1-0010-40cf-8e2c-ec451eaf23e5', '4dcecb0d-d074-4004-a22a-a7c1167c44e1', '8d4634cf-5a90-4938-8f57-dd94f301c0bd', 'c785ed45-9b12-4b7f-851c-465cdd4f8f3a', 'a93a5dab-2f6f-44d6-8355-419d4f5f1ba9', '73ac03f3-795b-4bf9-9543-7baad884b1fc', '81d78168-4c61-4a00-9a1c-b95046aaf555', 'cd454282-eadb-414f-81b6-04c2b3c91672', 'dbdad42d-249b-4836-a92f-7537231ac3cd', '627fda3c-4b57-44ea-8b65-2aae7b8ddd24', 'b9d37c61-9c72-471e-a314-781e64bd9d7a', 'c5f4d3df-917d-4380-beae-781d5b44886e', '2a798fd8-ed28-4499-a4b5-54f625ef31bc', '2450b615-96ee-4976-bc44-4a7955f0f5b9', 'dfbeef63-5409-4042-903a-61df4ae781b1', '03a2192e-c944-4a4e-8c41-ccb06c7689c4', '5f5e35fe-f6a1-4b63-b8b1-b92a9afc998f', 'f3063898-4623-40fb-910f-c2f8e1d23df3', '52df1aab-56e3-4f66-8732-e8e395ee76ba', 'ce313124-1405-4a9e-a248-cc839e6a338d', '3e7a2aa0-8994-488c-9f8e-8d7738353505', 'de27aec6-390d-49f0-a1c5-88b6f30e15ea', 'e2a29785-581a-43d4-85f2-3dfce662b8e0', 'a8c2295a-f565-47de-b517-6465e7d9cf45', 'e8cfb874-ec5b-41aa-b84f-18779c08d5e4', '36b87756-c525-4a75-8fc9-9b23c537239e', '1fa384b9-3240-45f4-b2b4-35aaad22231c', 'e2963b00-59b5-472b-9ea6-f02058cf2fc8', 'bc2a2712-6411-45e9-b477-866135d32a3f', '730cc28f-30a5-49e7-b4d2-7057def37b63', '9a20a001-0651-4975-b44a-220a79fa03d7', 'e174fb6d-5805-4017-b0e4-8eb838a09a91', '386b208e-0f7d-4f02-9e1e-bba07a6119ab', 'ab15d1bc-07b9-46ad-80bb-70570fdd02f6', 'de9cd0dc-cb88-4e1f-b957-090af7b09526', '674ff49f-baea-4c7c-9372-47e8dbf51fc4', 'b60c977d-cf69-4692-b085-19d52197a996', '8ad25215-de7c-4952-a230-3451d864338f', 'e2ccacdf-eb4c-4a53-bc05-5713663b1ce4', 'e5d3b97f-383a-4852-9b5c-41dc88259175', '44886978-2456-4e5f-b4a7-8dd0585242bf', '76ee59b9-b29c-4943-ab10-3e73ed326d0a', '0ea59f6d-a7f9-4bf6-b6db-293257fcd9eb', '69417807-8303-4ea4-85a5-43907e449b5e', '90ee06fb-6ee9-4a25-a819-4893e7a76d8e', '3d380ecc-85b8-41d2-9ac3-fc15c8b213e3', '8c9e6e89-f6b3-42e1-b107-050ece4bae83', 'de71caac-3994-4743-8761-5a4300ae9878', '030fd441-9d0c-4177-810a-30051ed4644c', '22963536-2a91-458e-bb6e-0cc83f06a19f', '1ce3128c-9e4f-41ef-8f3a-b0122630b89f', 'a54390fd-0e49-4bef-8567-22d71d162423', '008ee0f5-3fdc-4d3c-844b-5e1490368883', '17cfd64d-d40a-4300-8c53-4922f7a42ea3', '90c9856c-23e2-4bdd-8996-79ba39c3898b', 'fe57157a-3e43-43ce-a5c5-1356d5096d59', '2aa79c3c-eab6-4f80-b249-a4887abb3b16']
r2_eid_duringround_list = ['8ea82f8b-ab45-42fb-9cb1-fe90b8246923', 'd9e7735d-ea9d-41a5-9971-dc77178bec1c', '8c062b3b-624c-422c-9997-631f2b4ee045', 'c99091fb-e18b-418e-a93d-6338907b084a', 'f087de43-8f01-4dc9-9c79-13339454db95', 'eff4e72c-be30-4b8b-9bf9-3fe5661dad64', '0f21b4f6-e31b-46aa-8377-a3bed7dacfe5', '82c5dd64-d0f6-4413-b156-d0ce28fb49e2', 'bf5ce6c6-86ef-49bb-9bbe-690dafd33e42', 'fff8c15a-7868-44ba-a036-947e3766d07c', '42fbeada-e083-4bcc-80f8-a307a9aca72e', '83e93b43-07cc-4c0f-b656-4b208a8d1ba8', '13d1a95e-e5de-4d00-839e-a10ae7c77ea6', '1a6d5931-4fe1-446d-941d-86127bf2da1c', '50de27c8-01ff-45d3-a143-8baa80d695b0', '2457f7de-daf8-4f48-9bb2-6984934aa4c2', 'e532466a-d9cd-47c0-97b6-ec85d97c96a3', '07ed236d-baf7-4fab-9f49-2f5bcb6367d7', '83519a60-6fb3-4c2e-96f9-460c1acb2472', '3eb6828d-9664-4329-b46d-f355b564fb36', '899c5157-fbc8-46ae-9df3-cc9b09f896f6', 'f52dd77a-61e5-4ccd-8da9-0385976d76ac', 'c3b0483b-eda2-41b2-915a-fffceb922753', '4788a6e8-5f26-4288-bf74-801706f92420', 'cdafb888-e229-47b7-9bda-16fd61bd17ee', 'ad23a32d-86a1-4111-b48d-60fd76ac4fe3', '77c655a9-9c9b-4360-8cde-cbe0845af218', '7733512a-5af9-4a87-9042-e9a941f05be9', '8834adc2-860a-4db5-8003-ae6fd0841d52', '5fb13435-db10-4ad9-83a1-1eda7ee0600d', 'ae5b61b9-e085-4379-a5f4-b1ca453884fe', '9c13a7aa-fd4d-45b9-9749-f4fd05c5df78', 'c6d785dc-dad7-4662-b954-097bad9358d8', 'aa111fe9-2f69-4c42-a694-d51e244711b4', 'c9ce9c60-31b1-4b2e-81d9-97165f403483', 'aa0d2e15-5dfb-4497-9bf3-3b348eec6a18', '9e92ba48-85ae-4ee1-9c48-e17f9672de0e', 'b9cc15f5-715e-4449-ad70-555cd46c34e8', '34007943-82c5-4c23-8944-6a35e8912a19', '8f198336-d4ea-474c-8f9f-348e72a32716', '6b92fce7-f1e0-4370-8d6b-90ad4ccab9d2', '70a3b8d1-850c-4873-96c6-65e7ca7a6f91', '47f945d5-d6aa-4c4f-b985-b707ae7cc7c3', '7f729958-b458-4b84-8b77-1b2bc3d1faa3', 'f899d072-55b3-49b4-95c3-437b1d5c5eb7', '4bf81491-e158-4f8b-81b4-1c6216b87562', 'bea49019-eaac-418a-b05d-3c853a4fb4d0', '011b621f-e6c0-4465-859e-3af42e240f94', '6d4bc6f5-4747-49e7-a70f-0f6737290bfb', '50d292a7-264c-439b-a28b-2f0584f70ca8', '82b8e917-1376-468a-9f87-50f65fa13e44']
r2_eid_list = r2_eid_preround_list + r2_eid_duringround_list
# r2_eid_list_map2 = ['f7fb9602-7b18-4efb-b395-7bd6217bad8f', '0fb315a4-e44f-4760-9938-9a0f68735f0e', '5978e257-ef99-4c62-979a-35d664aa3995', 'f88b72e2-1407-4e5d-8aa0-a5b3c6819552', '612cfdca-615f-45d7-a5cb-a62a02bea5d3', '9118e5c6-9d07-45fd-bc8c-c28f9d5701ce', '33bb6594-de37-480c-91ad-82d15f274de5', '4e7f56b6-1e05-400b-8a68-9c621e03b182', 'd8171da5-1a74-470e-bdac-adfb69481e7b', '601577a5-b985-4695-ab44-95e62e24b394', '8d5d0e83-3a3c-457e-b6ae-e808fc8e9181', '0499e54c-06db-4021-884c-f98aab7ae6fa', '353a287e-ad44-4c8c-9fc7-1d683d7f8d9c', 'f484c1c5-b85c-4c9b-951d-a8c02f89a303', '3de22ef8-75df-4c5d-975b-cc208bef70d3', '81c84f9f-d69d-4b1d-84cf-0610f65bc789', '3c5ce637-77bc-49fa-ab32-2ede2ecbe5ee', 'e4829f7d-93a5-46a1-b7d8-f5cc1b815bf0', 'ee1b1adb-cbfe-4da4-8298-43bb729bc162', 'bec7f982-a5df-4172-88c8-16276ddfe54d', 'f8d0af99-0c67-475c-a068-6717b1ecb024', '92d7bad2-5489-4763-9410-6967e92e9797', 'bb5f87c8-2526-4bfa-adbd-f95068858d6d', '72a17460-6039-495d-9180-8d56f5968ae0', 'af95b3f4-663a-45c6-b748-62675d535d56', 'ab9f93a9-92dd-48ee-8f6d-960e0dfc1a63', 'd223293f-960c-4088-91c4-0d34e4b6d5ed', 'ec2f5c67-015b-4731-bfaf-7bd6b35a7c5c', '57d4947a-90a4-47e1-b5d5-8f55c98a7ad3', '0c80b5bf-5b8a-4cc7-9e35-3fd5691d75c9', '180a38e8-5526-4d4f-ad97-4594bbd17d5f', '1b303a67-c656-4f8f-906e-1369995edadc', 'e9ddfbed-003b-4327-a1d1-4663bea9bc8d', '04b8930a-f449-4477-8796-29e80181a511', 'bc4d3165-cdde-44db-acfb-94df9f68f11b', 'a0d4787e-c31e-4387-9879-8b4fcd597081', '04f01830-2910-4a88-a866-ddd2e70dcafc', 'cae28113-c544-495c-b744-17a73e6f9b13', 'a608f4e2-baee-4eda-84a4-35e1d38b4269', 'cca8104c-6b3c-4a2d-97b1-6ac0cb7638cf', 'b6ec1ada-6559-4b0a-bdd5-9a0031492196', '9679f0b8-72c8-40fc-b1a5-1553330dde79', 'e010a966-27eb-4802-87c9-ef46f843b31f', '3d651e59-5dce-46d5-aec9-74b85fc13ffb', 'e4e19680-67b0-4409-a502-2b069bfe73b6', 'f97987b0-3bb4-4b95-b641-5180c3a96f31', 'cc70fdbf-0e28-465e-a86c-ba22ed81a243', 'b83fdedc-a099-4608-a752-ba3c93d9fcca', '697c5b71-4ec8-4f69-ae6c-487596abd116', 'bac61ed5-f8f5-4c79-bc48-adccdd3182b2', '0c172897-0a99-4cbc-9c49-a657f4fa58f3', '04cf294f-6937-4da9-a30d-b04117f1b317', '9489c06b-57b0-49c5-bf40-28004dd5e695', 'd53228d1-94ed-438b-a3c5-6c87fba5cfdc', '08ea0145-0094-4f1d-a253-9821fc6ec26e', '271e1593-80ee-4486-a4ed-f10a797d95a6', 'd75988bd-565d-4660-bfab-a6515b962437', '946de53e-cdff-479d-a3bf-a4381f1b28fc', '4a483322-af64-4420-9d4a-38da00640d8e', 'bb6fbe56-0bcc-416f-b879-ca1e9889f28f', 'df784381-9eb7-46da-84cb-a1b3dbaf6761', '903a531f-aec2-47bb-be16-2f76a1c1c6a8', 'f53c8a8c-ee00-46ef-afb6-7f821bd11a7c', 'ed205303-58e0-4351-84af-0069d4595341', '879a2d75-3541-4f57-973d-8b546185ed59', 'ddeaeacd-81cc-48d5-a870-dee804e5e960', '9f958654-4e38-40cb-9dca-7a63a041755b', '98e8ecc9-9dd2-43eb-8f0a-55b54631ec7c', '36d15b33-055d-46dc-81de-9afa872512d9', 'c78e14ac-2448-40c6-8e23-aee4e0d984a4', 'a00e4256-86ed-4c12-9deb-93ebe4eba20e', '3cd29822-7c3c-4206-99bc-dff254a1ddd6', '72b799ce-0d37-4993-bfbf-52f490dfdf31', 'a64ad328-30ff-495e-b67f-72b9a3d1e309', 'e4117b5c-d0c7-417b-89df-aa5db414e3d9', '10cd2dac-bec8-47b8-8128-3fed70c1c5e9', '54428b60-0682-42b2-bf74-8442f505a116', '723efbc2-715d-4915-8cd3-2c0423a3e086', '4b0b13d9-9b63-4273-8792-30f97ef90206', '04a3ab47-ab8f-49f7-97e0-9a327363f30a', '263c4161-da09-4ca6-83ad-6bb54686aab4', '687d4c0d-e3a5-43b2-a2b6-dd1412bd0d3e']
## List of end-of-round event IDs
end_eid_list = ['f35471b7-952c-4efe-b847-80bb74ce8c2a', '82b8e917-1376-468a-9f87-50f65fa13e44', '54c504b3-e884-42ae-a751-9d5d66979cb3', '4f7e43dc-9bc2-4797-9ae8-ab30ee5a8bf6', '721b1669-b752-4b26-90cc-78f039f2c02e', 'e1cd7ef1-4744-4376-9293-b75fdd4bdd35', '7a5c9cf9-390f-44d4-b8a6-ec99b7ab73df', 'aec88b6c-9afe-41f8-8d52-1f1745825eef', '7bbfe100-6607-4f47-b30c-cfbcccce1276', '6232d134-4705-46d4-8b51-4920e4c7aad8', '1d57300e-f914-4109-9dcb-23469081586e', 'e9ca6127-6096-4455-8a7c-d0c2fa0fd2bd', '3bb18309-38ee-49c8-bac8-cc65eea7ba23', 'd868ff25-1a71-4336-92a6-4493520a0d40', '7c465bfe-d26f-40c5-ad6e-1c14305a8d55', 'd2ba3c87-125f-417c-aeed-ab248bdbbc07', '67d5b7d4-3cfb-4436-a1fe-f0750c1b0892', 'd72c5112-c009-4f10-ae78-6b4ba2e12dee', '1018abaa-1661-49ee-aa05-43db25b24527', '71c9eac9-171e-47af-9561-0a2b56067ccd', '5c29d456-1554-433b-9cb2-6d8f94e9c1a2', 'c6e41b6c-44f6-42e3-955d-588195e651c2', 'ecc3a49b-240d-4158-a496-909bd8e8d9f9', '05c53fad-d9e0-40ba-bb7c-d9c77649bbf6', '636217c7-f89a-4a3f-a5ed-5b76d5cfad6e', 'c736ed6d-1e86-418e-aebc-36540de9589e', 'cae04355-c61e-47ac-8828-162a3f95603b', '57a73440-d072-48e6-84f6-f84ca993263f', '687d4c0d-e3a5-43b2-a2b6-dd1412bd0d3e', 'b9c21f92-b5ab-4041-b431-34b817096bc8', '572c5102-aa0d-475c-9238-cd4a716dd08e', '6e857943-58dd-48d5-a42c-1fb6229a4551', 'd15804de-5398-4b4a-a6d5-d1230b8be859', '54803850-bc97-49c7-97c9-c55293e76d09', '497434b0-21de-4b60-ab8d-8063eab130ff', 'c6d41c5a-a04b-4586-a219-6d8172a3ea84', '53697a71-b14a-4849-8b78-fb88394c35a0', '875e969c-328d-4606-825c-445625f005cc', '63612aca-83f1-4745-9b79-9259b6067ce0', '39a61ab4-7475-45fc-9599-6a700e898ced', 'b447cc29-d133-44e5-b116-a960f4fe9ab4', 'bcd2fe49-106f-4aa2-8bea-1d8f2257c000', '2348dbb1-053a-41ad-9cb5-0256eb09ab14', '4c41bc08-a590-45bc-b418-118c7ca6f9f6', 'a8ca863a-5d83-4761-9a88-4e69deaa2ebe', '42c5d10b-9835-4f86-b62b-c9d4c1c101dc', '203b0896-3f9e-4768-8631-28bcc13ce760', '294ccf13-cdd7-4bd5-81e3-98b76b215672', '79fb2e1b-c201-429b-b1ca-e3bcd17f9f56', 'f9852911-f659-46da-91e3-e4da9654a238', 'c5ccdc67-26e7-46ce-b1f4-1c71cb774117', 'e2d7672e-87c2-4beb-9e27-4af70b17c5f7', '18402283-9873-448e-8b91-a316dedd1ee8']

# Get round number
for i in range(4, len(full_events) - 1):
    for j in range(len(json.loads(full_events[i])["events"])):
        json_event = json.loads(full_events[i])["events"][j]
        if json_event["id"] == r2_eid_list[0]:
            round_num = json_event["seriesState"]["games"][-1]["segments"][-1]["id"].replace('round-', '')
            break

# Get list of end-of-round events
end_events_list = []
for i in range(4, len(full_events)-1):
    loaded_events = json.loads(full_events[i])
    for j in range(len(loaded_events["events"])):
        if loaded_events["events"][j]["id"] in end_eid_list:
            end_events_list.append(loaded_events)

# Match information
match_date = state["startedAt"].split("T")[0]
format = state["format"].replace('-', ' ').capitalize()
match_result = utils.get_match_result(state, key='score')
final_teams = list(match_result.keys())
match_score = list(match_result.values())
team1=final_teams[0]
team2=final_teams[1]
team1_score=match_score[0]
team2_score=match_score[1]
forze_url = "https://preview.redd.it/new-forze-logo-v0-x31u5t3sg8ba1.png?width=600&format=png&auto=webp&s=041b6912e65d06e150219f63f79dc05b911e9c04"
ecstatic_url = "https://img-cdn.hltv.org/teamlogo/Ox1eFAB6o8VM6jwgPbQuks.svg?ixlib=java-2.1.0&s=66680f6d946ff4a93bc311f3bbab8d9e"

# Streamlit Visuals
## Top Header Section
col1, col2 = st.columns([5, 1])
with col1:
    st.title("During Series")
with col2:
    st.button("Rerun")

col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"Date of Match: {match_date}")
with col2:
    st.caption(f"Match format: {format}")
with col3:
    st.caption(f"Round: {round_num}")

components.html(
    f"""
    <div style="height:200px; background-color:#F0F2F6;display: grid;column-gap: 30px;grid-template-columns: auto auto auto;padding: 10px;">
        <div style="text-align: right;">
            <h3 style="color:black; font-family:sans-serif">{team1}</h3>
            <img style="height:50px;" src="{ecstatic_url}" />
        </div>

        <h3 style="color:black;font-size:40px;;text-align: center;font-family:sans-serif ">{team1_score} - {team2_score}</h3>
        <div style="text-align: left;">
            <h3 style="color:black;font-family:sans-serif">{team2}</h3>
            <img style="height:50px;" src="{forze_url}" />
        </div>
    </div>
    """
)

## Tabs
preround_tab, duringround_tab, postround_tab = st.tabs(["Pre-Round", "During Round", "Post-Round"])

### Pre-Round Tab
with preround_tab:

    # Init empty container
    placeholder_pre = st.empty()
    with placeholder_pre:
        st.info('Please wait for buying phase to begin...', icon="ℹ️")

### During Round Tab
with duringround_tab:

    # Init empty container
    placeholder_during = st.empty()
    with placeholder_during:
        st.info('Please wait for round to begin...', icon="ℹ️")


### Post Round Tab
with postround_tab:
    placeholder = st.empty()
    placeholder2 = st.empty()

    for event_num in range(len(end_events_list)):
        selected_event_list = end_events_list[event_num]["events"]
        for j in range(len(selected_event_list)):
            selected_event = selected_event_list[j]
            map = utils.get_team_info(selected_event, granularity="game").iloc[-1, 1].capitalize()

        with placeholder.container():
            full_df = utils.get_team_info(selected_event, granularity="round")
            team_round_kills = full_df.loc[full_df.map_seq == 1]

            st.markdown("#### Total Kills Stats Across Rounds")
            st.markdown(f"##### Map: {map}")
            fig2 = px.line(data_frame=team_round_kills, y=team_round_kills['kills'], x=team_round_kills['round_seq'],
                           color=team_round_kills['name'])
            st.write(fig2)

            time.sleep(0.5)

        with placeholder2.container():
            player_kda = utils.get_player_kdao(selected_event, granularity="game").loc[
                utils.get_player_kdao(selected_event, granularity="game").map_seq == 1]
            team1 = player_kda["team"].unique()[0]
            team2 = player_kda["team"].unique()[1]

            bomb_info = ['Bomb_Planted', 'Bomb_StartDefuse_WithKit', 'Bomb_StartDefuse_WithoutKit', 'Bomb_Defused',
                         'Bomb_Exploded']

            team1_df = player_kda.loc[player_kda.team == team1].drop(["map_name", "team"], axis=1
                                                                     ).rename(
                columns={'map_seq': 'Map_Number', 'kills': 'Kills', 'killAssistsGiven': 'Assists',
                         'multikills': 'Multi_Kills',
                         'deaths': 'Deaths', 'adr': 'ADR', 'name': 'Player', 'objectives.plantBomb': 'Bomb_Planted',
                         'objectives.beginDefuseWithKit': 'Bomb_StartDefuse_WithKit',
                         'objectives.beginDefuseWithoutKit': 'Bomb_StartDefuse_WithoutKit',
                         'objectives.defuseBomb': 'Bomb_Defused', 'objectives.explodeBomb': 'Bomb_Exploded'})
            team2_df = player_kda.loc[player_kda.team == team2].drop(["map_name", "team"], axis=1
                                                                     ).rename(
                columns={'map_seq': 'Map_Number', 'kills': 'Kills', 'killAssistsGiven': 'Assists',
                         'multikills': 'Multi_Kills',
                         'deaths': 'Deaths', 'adr': 'ADR', 'name': 'Player', 'objectives.plantBomb': 'Bomb_Planted',
                         'objectives.beginDefuseWithKit': 'Bomb_StartDefuse_WithKit',
                         'objectives.beginDefuseWithoutKit': 'Bomb_StartDefuse_WithoutKit',
                         'objectives.defuseBomb': 'Bomb_Defused', 'objectives.explodeBomb': 'Bomb_Exploded'})

            for metric in bomb_info:
                if metric not in team1_df:
                    team1_df[metric] = 0
                if metric not in team2_df:
                    team2_df[metric] = 0

            team1_killInfo = team1_df[['Map_Number', 'Player', 'Kills', 'Assists', 'Multi_Kills', 'Deaths', 'ADR']]
            team1_bombInfo = team1_df[['Map_Number', 'Player', 'Bomb_Planted', 'Bomb_StartDefuse_WithKit',
                                       'Bomb_StartDefuse_WithoutKit', 'Bomb_Defused', 'Bomb_Exploded']]

            team2_killInfo = team2_df[['Map_Number', 'Player', 'Kills', 'Assists', 'Multi_Kills', 'Deaths', 'ADR']]
            team2_bombInfo = team2_df[['Map_Number', 'Player', 'Bomb_Planted', 'Bomb_StartDefuse_WithKit',
                                       'Bomb_StartDefuse_WithoutKit', 'Bomb_Defused', 'Bomb_Exploded']]

            st.markdown("#### Kill Information")
            st.markdown(f"##### Team - :blue[{team1}]")
            st.table(team1_killInfo)
            st.markdown(f"##### Team - :blue[{team2}]")
            st.table(team2_killInfo)

            st.markdown("#### Bomb Information")
            st.markdown(f"##### Team - :blue[{team1}]")
            st.table(team1_bombInfo)
            st.markdown(f"##### Team - :blue[{team2}]")
            st.table(team2_bombInfo)

            time.sleep(0.5)

# Get list of Round 2 events
r2_events_list = []
for i in range(4, len(full_events)-1):
    loaded_events = json.loads(full_events[i])
    for j in range(len(loaded_events["events"])):
        if loaded_events["events"][j]["id"] in r2_eid_list:
            r2_events_list.append(loaded_events)

# Loop events in round 2 to simulate live events occuring

display_cols = ["name", "loadout.primary.img", "loadout.secondary.img",
                 "Equipment", "inventoryValue", "money" ]
kill_log_list = []
obj_log_list = []
obj_log_list_dedup = []

for event_num in range(len(r2_events_list)):
    # Load event data
    selected_event_list = r2_events_list[event_num]["events"]
    for j in range(len(selected_event_list)):
        selected_event = selected_event_list[j]
        economy = utils.get_player_economy(selected_event).fillna('')
        pha = utils.get_player_health_armor(selected_event)
        kda = utils.get_player_kdao(selected_event, 'game')
        gti = utils.get_team_info(selected_event, 'round')
        ps = utils.get_player_state(selected_event, 'game')
        lo = utils.get_loadouts(selected_event)
        gti_latest_round = gti.loc[gti['round_seq'] == int(round_num)].reset_index(drop=True)
        if selected_event["type"] == "player-killed-player":
            actor, target, action, weapon, round_time, action_log, event_log = utils.get_event_log(selected_event)
            kill_list = [round_time, actor, weapon, target]
            kill_log_list.append(kill_list)
        if re.search(r"\bplayer.*completed.*\b", selected_event["type"]):
            round_time, action_log, event_log = utils.get_event_log(selected_event)
            obj_list = [event_log]
            obj_log_list.append(obj_list)

    ## PRE ROUND

    # Format economy df
    economy["Equipment"] = utils.format_items(lo)
    economy = utils.get_weapons_img_path(economy)

    # Split df by team
    team1_economy = economy[economy["team"]==team1][display_cols]
    team1_total = team1_economy["inventoryValue"].sum()

    team2_economy = economy[economy["team"]==team2][display_cols]
    team2_total = team2_economy["inventoryValue"].sum()

    # Clear placeholder container
    placeholder_pre.empty()

    # Display Pre-Round
    with placeholder_pre.container():
        st.subheader("Pre-Round Economy", divider='rainbow')
        col1, col2 = st.columns([4,1])
        with col1:
            st.subheader(f"{team1}")
        with col2:
            st.write(f"Total Inventory Value: {team1_total}")

        st.dataframe(team1_economy,
                    column_config={
                        "name": "Player",
                        "money":"Money",
                        "inventoryValue": "Inventory Value",
                        "loadout.primary.img": st.column_config.ImageColumn(
                            "Primary Weapon", help="Primary Weapon"
                        ),
                        "loadout.secondary.img": st.column_config.ImageColumn(
                            "Secondary Weapon", help="Secondary Weapon"
                        )
                    },
                    hide_index=True)

        col1, col2 = st.columns([4,1])
        with col1:
            st.subheader(f"{team2}")
        with col2:
            st.write(f"Total Inventory Value: {team2_total}")

        st.dataframe(team2_economy,
                    column_config={
                        "name": "Player",
                        "money":"Money",
                        "inventoryValue": "Inventory Value",
                        "loadout.primary.img": st.column_config.ImageColumn(
                            "Primary Weapon", help="Primary Weapon"
                        ),
                        "loadout.secondary.img": st.column_config.ImageColumn(
                            "Secondary Weapon", help="Secondary Weapon"
                        )
                    },
                    hide_index=True)

    ## DURING ROUND

    # Empty during round container
    placeholder_during.empty()

    with placeholder_during.container():
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Kills", divider='grey')
            kill_log_list.sort(reverse=False)
            kills_df = pd.DataFrame(kill_log_list, columns=['Round_Time', 'Player', 'Weapon', 'Target'])
            kills_df = utils.get_weapons_img_path(kills_df, ['Weapon'])
            st.dataframe(kills_df[['Round_Time', 'Player', 'Weapon.img', 'Target']],
                         column_config={"Weapon.img": st.column_config.ImageColumn(label="Weapon", width='small')},
                         hide_index=True, use_container_width=True)

        with col2:
            st.subheader("Objectives", divider='grey')
            for item in obj_log_list:
                if item not in obj_log_list_dedup:
                    obj_log_list_dedup.append(item)
            obj_log_list_dedup.sort(reverse=False)
            obj_df = pd.DataFrame(obj_log_list_dedup, columns=['Objectives'])
            st.dataframe(obj_df, hide_index=True, use_container_width=True)

        with st.container():
            st.markdown("***Note: Game clock is counted down and round time ends at 0:00.***")

        # Players' Info Section
        st.subheader("Players' Info", divider='grey')
        colors = ['#edb5b5', '#52c222']
        col_t, col_ct = st.columns(2)
        with st.container():
            st.markdown(
                "***Note: Players are dead once Health and Armor bar depletes to zero. Once players are dead, their inventory will be empty too.***")

        with (col_t):
            st.markdown("#### Terrorists")
            team_t = gti_latest_round.loc[gti_latest_round['side'] == 'terrorists', 'name'].values[0]
            st.markdown(f"##### Team - :blue[{team_t}]")
            pha_filtered = pha.loc[pha['team'] == team_t].reset_index(drop=True)
            df_t = pha_filtered.set_index('name')
            df_t = pha_filtered.pivot(index="name", columns="team",
                                      values=['currentHealth', 'currentArmor']).reset_index()
            bar_chart_day = alt.Chart(df_t).transform_fold(['currentHealth', 'currentArmor']) \
                .mark_bar(clip=True).encode(
                x=alt.X('value:Q', stack='zero', scale=alt.Scale(domain=(0, 200)), title=''),
                y=alt.Y('name', title=''),
                order='color_value_sort_index:Q',
                color=alt.Color('key:N',).legend(None)
                ).properties(width=300, height=200).repeat(layer=['currentHealth', 'currentArmor']
                                      ).configure_range(category=alt.RangeScheme(colors))
            bar_chart_day
            with st.container():
                components.html("""
                            <div style="text-align: right;">
                                    <img style="height:50px;" src="" />
                                </div>
                            """)

            for i in range(len(pha_filtered)):
                lo_filtered = lo.loc[(lo['team'] == team_t) & (lo['name'] == pha_filtered.loc[i, 'name'])].filter(
                    like='loadout').reset_index(drop=True)
                lo_mapped = utils.get_weapons_img_path(lo_filtered, ['loadout.primary', 'loadout.secondary',
                                                                     'loadout.melee']).rename(
                    columns={'loadout.primary.img': 'Primary', 'loadout.secondary.img': 'Secondary',
                             'loadout.melee.img': 'Melee'})
                st.markdown(
                    f"##### Player {i + 1} - {pha_filtered.loc[i, 'name']} ({utils.get_player_kda(kda, gti_latest_round, pha_filtered, i)})")
                st.dataframe(lo_mapped[["Primary", "Secondary", "Melee"]], column_config={
                    "Primary": st.column_config.ImageColumn(label="Primary", width='small'),
                    "Secondary": st.column_config.ImageColumn(label="Secondary", width='small'),
                    "Melee": st.column_config.ImageColumn(label="Melee", width='small'),
                }, hide_index=True)

        with (col_ct):
            st.markdown("#### Counter Terrorists")
            team_ct = gti_latest_round.loc[gti_latest_round['side'] == 'counter-terrorists', 'name'].values[0]
            st.markdown(f"##### Team - :blue[{team_ct}]")
            pha_filtered = pha.loc[pha['team'] == team_ct].reset_index(drop=True)
            df_ct = pha_filtered.set_index('name')
            df_ct = pha_filtered.pivot(index="name", columns="team",
                                       values=['currentHealth', 'currentArmor']).reset_index()
            bar_chart_day = alt.Chart(df_ct).transform_fold(['currentHealth', 'currentArmor']) \
                .mark_bar(clip=True).encode(
                x=alt.X('value:Q', stack='zero', scale=alt.Scale(domain=(0, 200)), title=''),
                y=alt.Y('name', title=''),
                order='color_value_sort_index:Q',
                color=alt.Color('key:N',).legend(None)
                ).properties(width=300, height=200).repeat(layer=['currentHealth', 'currentArmor']
                                                       ).configure_range(category=alt.RangeScheme(colors))
            bar_chart_day
            with st.container():
                components.html("""
                            <div style="text-align: right;">
                                    <img style="height:50px;" src="https://raw.githubusercontent.com/jfcheong/csgo_tournament_tracker/main/assets/legend.png" />
                                </div>
                            """)

            for i in range(len(pha_filtered)):
                lo_filtered = lo.loc[(lo['team'] == team_ct) & (lo['name'] == pha_filtered.loc[i, 'name'])].filter(
                    like='loadout').reset_index(drop=True)
                lo_mapped = utils.get_weapons_img_path(lo_filtered, ['loadout.primary', 'loadout.secondary',
                                                                     'loadout.melee']).rename(
                    columns={'loadout.primary.img': 'Primary', 'loadout.secondary.img': 'Secondary',
                             'loadout.melee.img': 'Melee'})
                st.markdown(
                    f"##### Player {i + 1} - {pha_filtered.loc[i, 'name']} ({utils.get_player_kda(kda, gti_latest_round, pha_filtered, i)})")
                st.dataframe(lo_mapped[["Primary", "Secondary", "Melee"]], column_config={
                    "Primary": st.column_config.ImageColumn(label="Primary", width='small'),
                    "Secondary": st.column_config.ImageColumn(label="Secondary", width='small'),
                    "Melee": st.column_config.ImageColumn(label="Melee", width='small'),
                }, hide_index=True)
        time.sleep(0.3)
