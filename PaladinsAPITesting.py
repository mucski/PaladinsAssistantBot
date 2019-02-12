import requests
from pyrez.api import PaladinsAPI
from datetime import timedelta, datetime
import json
from bs4 import BeautifulSoup
import time
"""
ResponseFormat = "JSON"

api_url = "http://api.paladins.com/paladinsapi.svc"


def createTimeStamp(format="%Y%m%d%H%M%S"):
    return currentTime().strftime(format)


def currentTime():
    return datetime.utcnow()

paladinsAPI.__createSession__()
SessionId = paladinsAPI.currentSessionId
Signature = (paladinsAPI.__createSignature__("createsession"))

print(Signature)

url = str(api_url + "/getplayerjson/" + "3046/" + Signature + "/" + SessionId + "/" + createTimeStamp() + "/" + "FeistyJalapeno")
print(url)

r = requests.get(url)
print(r.status_code)
print(r.json())
"""


# n1 = wins and n2 = total matches
def create_win_rate(n1, n2):
    if n2 == 0:  # This means they have no data for the ranked split/season
        return "0"
    return str('{0:.2f}'.format((n1 / n2) * 100))


# Converts the number to the proper name
def convert_rank(x):
    return {
        1: "Bronze 5",
        2: "Bronze 4",
        3: "Bronze 3",
        4: "Bronze 2",
        5: "Bronze 1",
        6: "Silver 5",
        7: "Silver 4",
        8: "Silver 3",
        9: "Silver 2",
        10: "Silver 1",
        11: "Gold 5",
        12: "Gold 4",
        13: "Gold 3",
        14: "Gold 2",
        15: "Gold 1",
        16: "Platinum 5",
        17: "Platinum 4",
        18: "Platinum 3",
        19: "Platinum 2",
        20: "Platinum 1",
        21: "Diamond 5",
        22: "Diamond 4",
        23: "Diamond 3",
        24: "Diamond 2",
        25: "Diamond 1",
        26: "Master",
        27: "GrandMaster",
    }.get(x, "Un-Ranked")


paladinsAPI = PaladinsAPI(devId=3046, authKey="BB8E882EADB0431E990CD95E05C2B8C9")
print(paladinsAPI.getDataUsed())


def currentTime():
    return datetime.utcnow()


def createTimeStamp(format="%Y%m%d"):
    return currentTime().strftime(format)


def create_json(raw_data):
    json_data = str(raw_data).replace("'", "\"").replace("None", "0").replace("Mal\"", "Mal\'")
    return json.loads(json_data)


# Gets kda and Winrate for a player
def get_global_kda(player_name):
    url = "http://paladins.guru/profile/pc/" + player_name

    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    sup = str(soup.get_text())

    sup = sup.split(" ")
    data = list(filter(None, sup))

    stats = []

    # Gets account name and level
    for i, row in enumerate(data):
        if data[i] == "Giveaway":
            stats.append(data[i + 2])
            stats.append(data[i + 1])
            break

    # Gets Global wins and loses
    for i, row in enumerate(data):
        if data[i] == "Loss":
            new_s = str(data[i + 4].replace("(", "") + " %")
            stats.append(new_s)
            break

    # Gets Global KDA
    for i, row in enumerate(data):
        if data[i] == "KDA":
            stats.append(data[i + 6])
            break

    # Error checking to make sure that the player was found on the site
    if 'not' in stats:
        # error = "Could not the find player " + player_name + \
        #       ". Please make sure the name is spelled right (capitalization does not matter)."
        error = [player_name, "???", "???", "???"]
        return error

    # Puts all the info into one string to print
    # global_stats = "Name: " + stats.pop(0) + " (Lv. " + stats.pop(0) + ")\n" + "WinRate: " + \
    #                stats.pop(0) + "\n" + "Global KDA: " + stats.pop(0)
    # return global_stats
    return stats


def get_player_in_match(player_name):
    # Data Format
    # {'Match': 795950194, 'match_queue_id': 452, 'personal_status_message': 0, 'ret_msg': 0, 'status': 3,
    # 'status_string': 'In Game'}
    j = create_json(paladinsAPI.getPlayerStatus(player_name))
    if j == 0:
        return str("Player " + player_name + " is not found.")
    match_id = j["Match"]
    if j['status'] == 0:
        return "Player is offline."
    elif j['status'] == 1:
        return "Player is in lobby."
    elif j['status'] == 2:
        return "Player in champion selection."
    # Need to test for champ banning and selection
    # print(match_id)

    # ValueError: 2509 is not a valid Champions (Imani)

    # match_queue_id = 424 = Siege
    # match_queue_id = 445 = Test Maps (NoneType) --> no json data
    # match_queue_id = 452 = Onslaught
    # match_queue_id = 469 = DTM
    # match_queue_id = 486 = Ranked (Invalid)

    match_string = ""
    if j["match_queue_id"] == 424:
        match_string = "Siege"
    elif j["match_queue_id"] == 445:
        return "No data for Test Maps."
    elif j["match_queue_id"] == 452:
        match_string = "Onslaught"
    elif j["match_queue_id"] == 469:
        match_string = "Team Death Match"
    elif j["match_queue_id"] == 486:
        return "Ranked is currently not working."

    # Data Format
    # {'Account_Level': 17, 'ChampionId': 2493, 'ChampionName': 'Koga', 'Mastery_Level': 10, 'Match': 795511902,
    # 'Queue': '424', 'SkinId': 0, 'Tier': 0, 'playerCreated': '11/10/2017 10:00:03 PM', 'playerId': '12368291',
    # 'playerName': 'NabbitOW', 'ret_msg': None, 'taskForce': 1, 'tierLosses': 0, 'tierWins': 0}
    try:
        players = paladinsAPI.getMatchPlayerDetails(match_id)
    except:
        return "Imani is in the match and therefore we can not get stats on the current Match."
    # print(players)
    info = []
    team1 = []
    team2 = []
    for player in players:
        j = create_json(player)
        name = (j["playerName"])
        if (j["taskForce"]) == 1:
            team1.append(name)
        else:
            team2.append(name)

    match_data = ""
    match_data += match_string  # Match Type
    match_data += str('\n\n{:18} {:7}  {:7}  {:6}\n\n').format("Player name", "Level", "WinRate", "KDA")

    for player in team1:
        # print(get_global_kda(player))
        pl = get_global_kda(player)
        ss = str('{:18} Lv. {:3}  {:7}  {:6}\n')
        match_data += ss.format(pl.pop(0), pl.pop(0), pl.pop(0), pl.pop(0))

    match_data += "\n"

    for player in team2:
        # print(get_global_kda(player))
        info.append(get_global_kda(player))
        pl = get_global_kda(player)
        ss = str('{:18} Lv. {:3}  {:7}  {:6}\n')
        match_data += ss.format(pl.pop(0), pl.pop(0), pl.pop(0), pl.pop(0))

    return match_data


string_s = get_player_in_match("Kresnik")
print(string_s)
# print(get_player_in_match("DonPellegrino"))
# get_player_in_match("IDodgeBulletz")
# print(get_player_in_match("Z1unknown"))

"""
data = (get_player_in_match("FeistyJalapeno"))

match_data = ""
match_data += data.pop(0)  # Match Type
match_data += str('\n\n{:18} {:7}  {:7}  {:6}\n\n').format("Player name", "Level", "WinRate", "KDA")
pl = data.pop(0)
ss = str('{:18} Lv. {:3}  {:7}  {:6}')
match_data += ss.format(pl.pop(0), pl.pop(0), pl.pop(0), pl.pop(0))

print(match_data)
"""

def get_player_stats(player_name):
    # Player level, played hours, etc
    try:
        info = paladinsAPI.getPlayer(player_name)
    except:
        return "Player not found. Capitalization does not matter."
    # print(info)

    json_data = str(info).replace("'", "\"").replace("None", "0")
    #print(json_data)

    # Works amazingly
    j = json.loads(json_data)
    ss = ""
    # print(str(j["Last_Login_Datetime"]).split()[0], j["RankedKBM"]["Tier"])

    # Basic Stats
    ss += "Casual stats: \n"
    ss += "Name: " + (j["Name"]) + "\n"
    ss += "Account Level: " + str(j["Level"]) + "\n"
    total = int(j["Wins"]) + int(j["Losses"])
    ss += "WinRate: " + create_win_rate(int(j["Wins"]), total) + "% out of " + str(total) + \
          " matches.\n"
    ss += "Times Deserted: " + str(j["Leaves"]) + "\n\n"

    # Ranked Info
    ss += "Ranked stats for Season " + str(j["RankedKBM"]["Season"]) + ":\n"
    # Rank (Masters, GM, Diamond, etc)
    ss += "Rank: " + convert_rank(j["RankedKBM"]["Tier"]) + "\nTP: " + str(j["RankedKBM"]["Points"]) + " Position: " +\
          str(j["RankedKBM"]["Rank"]) + "\n"

    win = int(j["RankedKBM"]["Wins"])
    lose = int(j["RankedKBM"]["Losses"])

    ss += "WinRate: " + create_win_rate(win, win + lose) + "% (" + '{}-{}'.format(win, lose) + ")\n"
    ss += "Times Deserted: " + str(j["RankedKBM"]["Leaves"]) + "\n\n"

    # Extra info
    ss += "Extra details: \n"
    ss += "Account created on: " + str(j["Created_Datetime"]).split()[0] + "\n"
    ss += "Last login on: " + str(j["Last_Login_Datetime"]).split()[0] + "\n"
    ss += "Platform: " + str(j["Platform"]) + "\n"
    ss += "MasteryLevel: " + str(j["MasteryLevel"]) + "\n"
    ss += "Steam Achievements completed: " + str(j["Total_Achievements"]) + "\n"

    return ss


#print(get_player_stats("IsaacFernando"))


def get_champ_stats_api(player_name, champ):
    # Stats for the champs
    champ = str(champ).lower().capitalize()
    stats = paladinsAPI.getChampionRanks(player_name)

    if "Mal" in champ:
        champ = "Mal'Damba"

    ss = ""
    t_wins = 0
    t_loses = 0
    t_kda = 0
    count = 0

    for stat in stats:
        # print(type(stat))
        # print(type(str(stat)))
        json_data = str(stat).replace("'", "\"").replace("None", "0").replace("Mal\"", "Mal\'")
        #print(json_data)
        j = json.loads(json_data)
        wins = stat.wins
        loses = stat.losses
        kda = stat.getKDA()
        count += 1
        if stat.godName == champ:
            ss = str('Champion: {} (Lv {})\nKDA: {} ({}-{}-{}) \nWinRate: {}% ({}-{}) \nLast Played: {}')
            ss = ss.format(stat.godName, stat.godLevel, kda, stat.kills, stat.deaths, stat.assists,
                           create_win_rate(wins, wins+loses), stat.wins, stat.losses, str(j["LastPlayed"]).split()[0])
        if ss == "":
            ss += "No data for champion: " + champ + "\n"

        t_wins += wins
        t_loses += loses
        t_kda += kda
        # print(stat.getKDA())
        # print(stat.godName)

    global_ss = str("\n\nGlobal KDA: {}\nGlobal WinRate: {}% ({}-{})")
    win_rate = create_win_rate(t_wins, t_wins + t_loses)
    t_kda = str('{0:.2f}').format(t_kda/count)
    global_ss = global_ss.format(t_kda, win_rate, t_wins, t_loses)
    ss += global_ss
    return ss


# print(get_champ_stats_api("LordCreeper", "Willo"))

# IS the person offline
"""
status = paladinsAPI.getPlayerStatus("FeistyJalapeno")
print(status)
status = paladinsAPI.getPlayerStatus("Z1unknown")
print(status)
status = paladinsAPI.getPlayerStatus("CavityCalamity")
print(status)
"""

"""
# Get match info
matches = paladinsAPI.getMatchHistory("FeistyJalapeno")
for match in matches:
    print(match)
"""


# http://api.smitegame.com/smiteapi.svc/createsessionJson/1004/8f53249be0922c94720834771ad43f0f/20120927183145

# for some in info:
#    print()


# print(championsRank)


'''
if championsRank is not None:
    for championRank in championsRank:
        print(championRank.getWinratio())
        
'''
