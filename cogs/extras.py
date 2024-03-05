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


class ExtrasCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        description="Deletes all threads from the channel.",
        guild_ids=SERVERS,
        default_member_permissions=8,
    )
    async def clear_threads(self, interaction):
        threads = interaction.channel.threads
        counter = 0
        for thread in threads: 
            counter += 1
            await thread.delete()
        await interaction.send(f'Deleted {counter} threads', ephemeral=True, delete_after= 15)


def setup(bot):
    print(SERVERS)
    bot.add_cog(ExtrasCog(bot))
