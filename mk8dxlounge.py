from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timezone, timedelta

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

        datetime_text = cells[1].find("span")["data-time"]
        obj.time = datetime.fromisoformat(datetime_text)
        obj.mmr_delta = int(cells[2].text)
        obj.mmr = int(cells[3].text)
        return obj

class MK8DXLoungePlayerDetails:
    def __init__(self, lounge_id, season=None):
        self.lounge_id = lounge_id
        self.season = season
        if self.season:
            self.url = f"https://www.mk8dx-lounge.com/PlayerDetails/{lounge_id}?season={season}"
        else:
            self.url = f"https://www.mk8dx-lounge.com/PlayerDetails/{lounge_id}"
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
    
    def get_mmr(self):
        mmr_element = self.soup.find("dt", string="MMR")
        if mmr_element:
            return int(mmr_element.find_next_sibling("dd").text)
        raise ValueError("MMR not found")
    
    def get_last_online_time(self, timezone=timezone.utc):
        last_joined_event = self.get_last_joined_event()
        last_online_time = last_joined_event.time
        return last_online_time.astimezone(timezone)