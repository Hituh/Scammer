import aiohttp
import nextcord
import os
import random

from nextcord import Interaction, Member, Object, SelectOption, slash_command
from nextcord.ext import tasks, commands
from nextcord.ext.commands.bot import Bot
from nextcord.ui import View, TextInput, Select
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

servers_str = os.getenv("SERVERS")
SERVERS = [int(id_str) for id_str in servers_str.split(",")]
BOT_TOKEN = os.getenv("BOT_TOKEN")


class InputShort(nextcord.ui.TextInput):
    def __init__(self, label, placeholder, required):
        super().__init__(
            label=label,
            placeholder=placeholder,
            required=required,
            style=nextcord.TextInputStyle.short,
        )

    async def callback(self, interaction: Interaction):
        print(self.value)


class InputParagraph(nextcord.ui.TextInput):

    def __init__(self, label, placeholder, required):
        super().__init__(
            label=label,
            placeholder=placeholder,
            required=required,
            style=nextcord.TextInputStyle.paragraph,
        )

    async def callback(self, interaction: Interaction):
        print(self.value)


class Button(nextcord.ui.Button):
    def __init__(self, label, style):
        super().__init__(label=label, style=style)


class EmbedView(nextcord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.check_button = Button("Search", nextcord.ButtonStyle.primary)
        self.report_button = Button("Report", nextcord.ButtonStyle.danger)
        self.add_item(self.check_button)
        self.add_item(self.report_button)
        self.report_button.callback = self.report_button_callback
        self.check_button.callback = self.check_button_callback

    async def report_button_callback(self, interaction):
        modal = ReportModal(self.bot, interaction, interaction.channel)
        await interaction.response.send_modal(modal)

    async def check_button_callback(self, interaction):
        modal = SearchModal(self.bot, interaction)
        await interaction.response.send_modal(modal)


class SearchModal(nextcord.ui.Modal):
    def __init__(self, bot: commands.Bot, interaction):
        super().__init__(title="Search menu.", timeout=None)
        self.bot = bot
        self.ign_input = InputShort("Write their in game name.", "Hituh", False)
        self.discord_input = InputShort("Write their discord name", "Hituh", False)
        self.discord_id_input = InputShort(
            "Write their discord id. (optional)", "158643072886898688", False
        )
        self.add_item(self.ign_input)
        self.add_item(self.discord_input)
        self.add_item(self.discord_id_input)

    async def callback(self, interaction) -> None:
        await interaction.send("Tested", ephemeral=True, delete_after=30)


class ReportModal(nextcord.ui.Modal):  # Inherit directly from `nextcord.ui.View`
    def __init__(self, bot: commands.Bot, interaction, message_channel):
        super().__init__(
            title="Report menu.", timeout=None
        )  # Set timeout to None for persistence
        self.bot = bot
        self.channel = message_channel
        self.ign_input = InputShort("Write their in game name.", "Hituh", True)
        self.discord_input = InputShort("Write their discord name.", "Hituh", False)
        self.discord_id_input = InputShort(
            "Write their discord id (optional).", "158643072886898688", False
        )
        self.discord_description = InputParagraph(
            "Write down short tldr of the issue.", "Tried to island scam me.", True
        )
        self.add_item(self.ign_input)
        self.add_item(self.discord_input)
        self.add_item(self.discord_id_input)
        self.add_item(self.discord_description)

    async def callback(self, interaction) -> None:
        print(self.ign_input.value)
        print(self.discord_input.value)
        print(self.discord_id_input.value)
        print(self.discord_description.value)


class ScamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        guild_ids=SERVERS,
        description="Self assign roles",
        default_member_permissions=8,
    )
    async def create_scam_embed(self, interaction):
        view = EmbedView(self.bot)
        embed = nextcord.Embed(
            description="To search for person press 'Search'.\nTo submit a report, press 'Submit' and continue with the steps."
        )
        await interaction.channel.send(embed=embed, view=view)

    async def test(self, interaction):
        modal = ReportModal(self.bot, interaction, interaction.channel)
        await interaction.response.send_modal(modal)


def setup(bot):
    print(SERVERS)
    bot.add_cog(ScamCog(bot))
