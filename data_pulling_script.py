import requests
import json

CURRENT_SEASON = "2025"

with open("APIKey.txt", "r") as file:
    apikey = file.read()

header = {"X-TBA-Auth-Key" : apikey}

cont = True
page = 0
team_keys = []

while cont :
    response = requests.get(
        "https://www.thebluealliance.com/api/v3/teams/" + CURRENT_SEASON + "/" + str(page) + "/keys",
        headers=header)
    if response.status_code == 200:
        data = response.json()
        if len(data)>0:
            team_keys = team_keys + data
            page = page + 1
        else :
            cont = False
    else :
        cont = False

print("Teams pulled: ", len(team_keys))

award_data = {}

for team_key in team_keys:
    response = requests.get(
        "https://www.thebluealliance.com/api/v3/team/" + team_key + "/awards",
        headers=header)
    if response.status_code == 200:
        awards = response.json()
        award_data[team_key] = awards


print("Awards Pulled. Number of teams: ", len(award_data))

award_json = json.dumps(award_data)

with open("AwardData.json", "w") as file:
    file.write(award_json)

print("Operation completed successfully")
