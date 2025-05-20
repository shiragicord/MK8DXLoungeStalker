from mk8dxlounge import MK8DXLoungePlayerDetails
from datetime import datetime, timedelta, timezone
import time
import requests

from config import DISCORD_WEBHOOK_URL, LOUNGE_ID


def post_discord_embed(
    text_content, title, url, timestamp: datetime, color, inline_fields: dict
):
    fields = []
    for key, value in inline_fields.items():
        fields.append({"name": key, "value": value, "inline": True})

    requests.post(
        DISCORD_WEBHOOK_URL,
        json={
            "content": text_content,
            "embeds": [
                {
                    "title": title,
                    "url": url,
                    "timestamp": timestamp.isoformat(),
                    "color": color,
                    "fields": fields,
                }
            ],
        },
    )


def main():
    player = MK8DXLoungePlayerDetails(LOUNGE_ID)
    previous_mmr = None
    previous_last_online_time = None

    while True:
        player.update()
        new_mmr = player.get_mmr()
        new_last_online_time = player.get_last_online_time(
            timezone=timezone(timedelta(hours=9))
        )

        if new_mmr != previous_mmr or new_last_online_time != previous_last_online_time:
            previous_mmr = new_mmr
            previous_last_online_time = new_last_online_time
            post_discord_embed(
                f"{player.get_player_name()} ({player.get_division()} MMR:{player.get_mmr()}) went online at {new_last_online_time}",
                f"{player.get_player_name()} - {player.get_division()}",
                player.url,
                new_last_online_time,
                0x00FF00,
                {"MMR": new_mmr, "Peak MMR": player.get_peak_mmr()},
            )

        time.sleep(60)


if __name__ == "__main__":
    main()
