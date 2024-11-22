from highrise.__main__ import *
import time
from dotenv import load_dotenv
import os

load_dotenv()

bot_file_name = "bot"
bot_class_name = "Bot"
room_id = os.getenv("ROOM_ID")
bot_token = os.getenv("BOT_TOKEN")
#6694de2ee40b58ae179d8ddf-paseito
#669887710b6fb0741853e424-susan
#"66f5fda4fe8df01629d3495e"-FEARLESS
#6730ea2867f96ade3be2a58f ludo

my_bot = BotDefinition(getattr(import_module(bot_file_name), bot_class_name)(), room_id, bot_token)

while True:
    try:
        definitions = [my_bot]
        arun(main(definitions))
    except Exception as e:
        print(f"An exception occourred: {e}")
        time.sleep(5)