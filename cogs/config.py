import nextcord
import os

from nextcord import Interaction, slash_command
from nextcord.ext import commands
from nextcord.ui import TextInput, Button, View, Modal
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

servers_str = os.getenv("SERVERS")
SERVERS = [int(id_str) for id_str in servers_str.split(",")]
BOT_TOKEN = os.getenv("BOT_TOKEN")


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    print(SERVERS)
    bot.add_cog(ConfigCog(bot))
