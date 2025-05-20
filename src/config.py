import dotenv
import os

dotenv.load_dotenv()

LOUNGE_ID = int(os.getenv("LOUNGE_ID"))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
