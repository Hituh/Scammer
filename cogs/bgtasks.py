import nextcord
import os
import json
import shutil
from datetime import datetime
from nextcord import Interaction, slash_command, SlashOption

from nextcord.ext import tasks, commands
from nextcord.ui import TextInput, Button, View, Modal
from dotenv import load_dotenv, find_dotenv
from API.find_player import find_player
from extras.json_handling import load_json, save_json

load_dotenv(find_dotenv())

servers_str = os.getenv("SERVERS")
SERVERS = [int(id_str) for id_str in servers_str.split(",")]
BOT_TOKEN = os.getenv("BOT_TOKEN")


class BgTasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     self.backup_data.start()

    @tasks.loop(seconds=86400, reconnect=True)
    async def backup_data(self):
        print("Starting backup...")
        source_folder = r"C:\Users\okazy\Desktop\AssociaterV2\data"
        backup_folder = r"C:\Users\okazy\Desktop\AssociaterV2\data_backup"
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        # Get the current date and time for the backup
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Iterate through files in the source folder
        for filename in os.listdir(source_folder):
            source_path = os.path.join(source_folder, filename)

            # Check if the item is a file (not a subfolder)
            if os.path.isfile(source_path):
                # Generate the new filename with the backup date
                backup_filename = f"{current_datetime}_{filename}"

                # Create the full path for the backup file
                backup_path = os.path.join(backup_folder, backup_filename)

                # Copy the file to the backup folder
                shutil.copy2(source_path, backup_path)

                print(f"Backup created: {backup_filename}")


def setup(bot):
    bot.add_cog(BgTasksCog(bot))
