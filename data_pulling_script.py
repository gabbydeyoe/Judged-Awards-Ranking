import os
from pathlib import Path

import requests
import json

CURRENT_SEASON = "2025"


def load_env(path=".env"):
    """Load KEY=VALUE pairs from a .env file into os.environ (existing vars win)."""
    env_path = Path(__file__).resolve().parent / path
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

apikey = os.environ.get("TBA_API_KEY")
if not apikey:
    raise SystemExit(
        "TBA_API_KEY is not set. Copy .env.example to .env and add your "
        "The Blue Alliance API key."
    )

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
