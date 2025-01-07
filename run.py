from highrise.__main__ import *
import time
from dotenv import load_dotenv
import os
import traceback  # Agregamos esto

load_dotenv()

bot_file_name = "bot"
bot_class_name = "Bot"
room_id = os.getenv("660e6448818d797101c5d230")
bot_token = os.getenv("have7e956310cd1600ac49d0d014eb1a13c508f93507f8519c855156c87f4b7c55ad")

# Agregamos verificación
if not room_id or not bot_token:
    print("Error: ROOM_ID or BOT_TOKEN not found in environment variables")
    exit(1)

my_bot = BotDefinition(getattr(import_module(bot_file_name), bot_class_name)(), room_id, bot_token)

while True:
    try:
        definitions = [my_bot]
        arun(main(definitions))
    except Exception as e:
        print(f"An exception occurred: {e}")
        print("Traceback:")
        print(traceback.format_exc())  # Esto mostrará más detalles del error
        time.sleep(5)
