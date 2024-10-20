from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import time

class MK8DXLoungeEvent:
    def __init__(self):
        self.name = ""
        self.id = 0
        self.time: datetime = None
        self.mmr_delta = 0
        self.mmr = 0
    
    def parse_html_table_row(row: BeautifulSoup):
        obj = MK8DXLoungeEvent()
        cells = row.find_all("td")
        name_raw = cells[0].text.strip()
        obj.name = re.sub(r" \(ID: [0-9]+\)$", "", name_raw)
        obj.id = int(re.sub(r"^/TableDetails/", "", cells[0].find("a")["href"]))

        datetime_text = cells[1].find("span")["data-time"].replace("Z", "+00:00")
        obj.time = datetime.fromisoformat(datetime_text)
        obj.mmr_delta = int(cells[2].text)
        obj.mmr = int(cells[3].text)
        return obj

class MK8DXLoungePlayerDetails:
    def __init__(self, lounge_id, season):
        self.lounge_id = lounge_id
        self.season = season
        self.url = f"https://www.mk8dx-lounge.com/PlayerDetails/{lounge_id}?season={season}"
        self.update()

    def update(self):
        self.soup = BeautifulSoup(requests.get(self.url).content, "html.parser")

    def get_player_name(self):
        h1_text = self.soup.find("h1").text
        return re.sub(r" - [A-Z][a-z]+ [0-9] $", "", h1_text)
    
    def get_division(self):
        h1_text = self.soup.find("h1").text
        return re.sub(r"^.* - ", "", h1_text)
    
    def get_last_joined_event(self) -> MK8DXLoungeEvent:
        table = self.soup.find("table")
        rows = table.find_all("tr")
        return MK8DXLoungeEvent.parse_html_table_row(rows[1])
    
    def get_peak_mmr(self):
        peak_mmr_element = self.soup.find("dt", string="Peak MMR")
        if peak_mmr_element:
            return int(peak_mmr_element.find_next_sibling("dd").text)
        raise ValueError("Peak MMR not found")
    
    def get_last_online_time(self):
        last_joined_event = self.get_last_joined_event()
        return last_joined_event.time

LOUNGE_ID = 58599
SEASON = 12
DISCORD_WEBHOOK_URL = "your_webhook_url_here"

fefe = MK8DXLoungePlayerDetails(LOUNGE_ID, SEASON)

def post_discord_message(content):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": content})

last_online_time = None

while True:
    fefe.update()
    new_last_online_time = fefe.get_last_online_time()
    if new_last_online_time != last_online_time:
        post_discord_message(f"{fefe.get_player_name()} went online at {new_last_online_time}")
        last_online_time = new_last_online_time
    time.sleep(60)