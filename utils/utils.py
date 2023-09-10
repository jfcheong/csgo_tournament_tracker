from copy import deepcopy
import json
import pandas as pd
from pandas.api.types import is_float_dtype
import re

IMG_URL = "https://raw.githubusercontent.com/jfcheong/csgo_tournament_tracker/main/assets/%s.png"

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
    required_fields = ["money", "inventoryValue", "netWorth", "loadout.primary", "loadout.secondary"]
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

def get_event_log(event):

    player_name_id_map = {}
    for team in event["seriesState"]["teams"]:
        for _player in team["players"]:
            player_name_id_map[_player["id"]] = _player["name"]

    event_type = event["type"]
    if re.search(r"\bplayer.*killed.*player\b", event_type):

        actor = player_name_id_map[event["actor"]["id"]]
        target = player_name_id_map[event["target"]["id"]]
        action = event["action"]
        weapon = list(event["actor"]["stateDelta"]["series"]["weaponKills"].keys())[0]
        round_time = event["seriesState"]["games"][-1]["clock"]["currentSeconds"]
        minutes = int(round_time/60)
        seconds = round_time % 60
        round_time = f"{minutes}:{seconds:02}"
        action_log = f"{actor} {action} {target} with {weapon}"
        event_log = f"{minutes}:{seconds:02}     {actor} {action} {target} with {weapon}"
        return actor, target, action, weapon, round_time, action_log, event_log

    elif re.search(r"\bplayer.*completed.*\b", event_type):
        event_type_map = {
            "player-completed-plantBomb": {
                "action": "planted",
                "target": "the bomb"
            },
            "player-completed-defuseBomb": {
                "action": "defused",
                "target": "the bomb"
            },
            "player-completed-beginDefuseWithKit": {
                "action": "began defusing",
                "target": "the bomb with kit"
            },
            "player-completed-beginDefuseWithoutKit": {
                "action": "began defusing",
                "target": "the bomb without kit"
            },
            "player-completed-explodeBomb": {
                "action": "exploded",
                "target": "the bomb"
            }
        }
        actor = player_name_id_map[event["actor"]["id"]]
        target = event_type_map[event_type]["target"]
        action = event_type_map[event_type]["action"]
        round_time = event["seriesState"]["games"][-1]["clock"]["currentSeconds"]
        minutes = int(round_time/60)
        seconds = round_time % 60
        round_time = f"{minutes}:{seconds:02}"
        action_log = f"{actor} {action} {target}"
        event_log = f"{minutes}:{seconds:02}     {actor} {action} {target}"
        return round_time, action_log, event_log

    else:
        return None


def get_match_result(state_dict, key):
    teams = state_dict['teams']
    result_dict = {}
    for team in teams:
        team_name = team['name']
        value = team[key]
        result_dict[team_name] = value
    return result_dict


def get_weapons_img_path(df, weapons_col=["loadout.primary", "loadout.secondary"]):
    """ Gets image path from weapon name """
    for col in weapons_col:
        img_col = [IMG_URL % (str(val)) if val else "" for val in df[col]]
        df[f"{col}.img"] = img_col
    return df


def _clean_text(s):
    """ Cleans text into human Nreadable format """
    s = s.replace("_", " ") # replace _ with space
    s = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', s) # add space before capital letter
    s = s.title() # title case
    return s


def format_items(loadout, exclude_col=["loadout.primary", "loadout.secondary"]):
    """ Formats loadout items into list of lists """
    cols = [col for col in loadout.columns.str.startswith('loadout.')
                            if col not in exclude_col]
    items = loadout.loc[:, cols].values.tolist()
    return [cleaned if (cleaned := [_clean_text(elem) for elem in sublist 
                                                    if elem is not None])
                        else [None] for sublist in items]


if __name__ == "__main__":
    print("Loaded utils")