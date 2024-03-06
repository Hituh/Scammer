import nextcord
import os
import json

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
config_json_path = r"C:\Users\okazy\Desktop\AssociaterV2\configs\config.json"
active_scam_threads_json_path = (
    r"C:\Users\okazy\Desktop\AssociaterV2\data\active_scam_threads.json"
)
confirmed_scam_threads_json_path = (
    r"C:\Users\okazy\AssociaterV2\data\confirmed_scam_threads.json"
)
scammers_channel_id = None
main_guild_id = None


def find_existing(active_channels, ign, discord, discord_id):
    key1, key2, key3 = "scammer_name", "scammer_discord_tag", "scammer_discord_id"
    for item in active_channels:
        if (
            item[key1].lower() == ign.lower()
            or item[key2].lower() == discord.lower()
            or item[key3].lower() == discord_id.lower()
        ):
            return item["channel_id"]
    return False


async def create_thread(
    channel, interaction, ign, description, discord="Undefined", discord_id="Undefined"
):
    active_channels = load_json(active_scam_threads_json_path)
    exists = find_existing(active_channels, ign, discord, discord_id)
    if exists != False:
        thread = channel.get_thread(exists)
        await thread.add_user(interaction.user)
        await interaction.send(
            f"There is already an open thread for this person {thread.mention}.",
            ephemeral=True,
            delete_after=15,
        )
    else:
        thread = await channel.create_thread(
            name=f"{ign} report.",
            message=None,
            auto_archive_duration=1440,
            type=None,
        )
        active_channels.append(
            {
                "channel_id": thread.id,
                "reporter_discord_id": interaction.user.id,
                "scammer_name": ign,
                "scammer_discord_tag": discord,
                "scammer_discord_id": discord_id,
                "description": description,
            }
        )
        save_json(active_channels, active_scam_threads_json_path)
        await thread.add_user(interaction.user)
        await interaction.send(
            f"*Here is your report - {thread.mention}.*",
            ephemeral=True,
            delete_after=15,
        )
        await thread.send(
            f"""
            **Scammer ign:** {ign}
            **Scammer discord tag:** {discord if discord else "not provided"}
            **Scammer discord id:** {discord_id if discord_id else "not provided"}
            **Description:** {description}        
            """
        )
        await thread.send(
            f"\n{interaction.user.mention} please provide any more info (such as screenshots of the issue), to help us better resolve the issue.\nWe'll get back to you shortly"
        )


class InputShort(TextInput):
    def __init__(self, label, placeholder, required, min_length=0):
        super().__init__(
            label=label,
            min_length=min_length,
            placeholder=placeholder,
            required=required,
            style=nextcord.TextInputStyle.short,
        )


class InputParagraph(TextInput):

    def __init__(self, label, placeholder, required, min_length=0):
        super().__init__(
            label=label,
            min_length=min_length,
            placeholder=placeholder,
            required=required,
            style=nextcord.TextInputStyle.paragraph,
        )


class Button(Button):
    def __init__(self, label, style, custom_id):
        super().__init__(label=label, style=style, custom_id=custom_id)


class MainEmbed(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.message_channel = None
        self.search_button = Button(
            "Search", nextcord.ButtonStyle.primary, "Searchbutton"
        )
        self.report_button = Button(
            "Report", nextcord.ButtonStyle.danger, "Reportbutton"
        )
        self.add_item(self.search_button)
        self.add_item(self.report_button)
        self.report_button.callback = self.report_button_callback
        self.search_button.callback = self.check_button_callback

    async def report_button_callback(self, interaction):
        self.message_channel = interaction.channel
        modal = ReportModal(self.bot, self.message_channel)
        await interaction.response.send_modal(modal)

    async def check_button_callback(self, interaction):
        self.message_channel = interaction.channel
        modal = SearchModal(self.bot, interaction)
        await interaction.response.send_modal(modal)


class SearchModal(Modal):
    def __init__(self, bot: commands.Bot):
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


class ReportModal(Modal):  # Inherit directly from `View`
    def __init__(self, bot: commands.Bot, message_channel):
        super().__init__(
            title="Report menu.", timeout=None
        )  # Set timeout to None for persistence
        self.bot = bot
        self.channel = message_channel
        self.ign_input = InputShort(
            "In game name. (Required)", "Hituh", True, min_length=3
        )
        self.discord_input = InputShort(
            "Discord name (not server name). (Optional)", "Hituh", False
        )
        self.discord_id_input = InputShort(
            "Discord ID. (Optional).", "158643072886898688", False
        )
        self.description = InputParagraph(
            "Short description of the issue. (Required)",
            "Eg. Tried to island scam me.",
            True,
            min_length=5,
        )
        self.add_item(self.ign_input)
        self.add_item(self.discord_input)
        self.add_item(self.discord_id_input)
        self.add_item(self.description)

    async def callback(self, interaction) -> None:
        player_exists = find_player(self.ign_input.value)
        if not player_exists:
            await interaction.send(
                f"Player {self.ign_input.value} not found. Did you write the name correctly?",
                ephemeral=True,
                delete_after=30,
            )
        if player_exists == None:
            await interaction.send(
                f"Something went wrong. Please contact Hituh for help.",
                ephemeral=True,
                delete_after=30,
            )
        if player_exists:
            await interaction.send(
                f"Player {self.ign_input.value} found. Opening thread...",
                ephemeral=True,
                delete_after=15,
            )
            await create_thread(
                channel=self.channel,
                interaction=interaction,
                ign=self.ign_input.value,
                discord=self.discord_input.value,
                discord_id=self.discord_id_input.value,
                description=self.description.value,
            )


class ScamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scammers_channel = None

    @commands.Cog.listener()
    async def on_ready(self):

        config = load_json(config_json_path)
        main_guild_id = config["main_guild_id"]
        scammers_channel_id = config["scammers_channel_id"]
        for guild in self.bot.guilds:
            if guild.id == int(main_guild_id):
                self.scammers_channel = guild.get_channel(int(scammers_channel_id))
                break
        self.bot.add_view(MainEmbed(self.bot))
        self.compare_active_scam_threads.start()

    @tasks.loop(seconds=5, reconnect=True)
    async def compare_active_scam_threads(self):
        active_channels_json = load_json(active_scam_threads_json_path)
        active_channels_ids = {
            channel["channel_id"] for channel in active_channels_json
        }

        if self.scammers_channel:
            thread_ids = {thread.id for thread in self.scammers_channel.threads}

            channels_to_remove = active_channels_ids - thread_ids

            active_channels_json = [
                channel
                for channel in active_channels_json
                if channel["channel_id"] not in channels_to_remove
            ]

            save_json(active_channels_json, active_scam_threads_json_path)

    @slash_command(
        guild_ids=SERVERS,
        description="Self assign roles",
        default_member_permissions=8,
    )
    async def create_scam_embed(self, interaction):
        view = MainEmbed(self.bot)
        embed = nextcord.Embed(
            description="To search for person press 'Search'.\nTo submit a report, press 'Submit' and continue with the steps."
        )
        await interaction.channel.send(embed=embed, view=view)

    @slash_command(
        guild_ids=SERVERS,
        description="Update information about scam report.",
        default_member_permissions=8,
    )
    async def update_scam_embed(
        self,
        interaction,
        ign: str = SlashOption(
            description="Write the updated IGN. Leave blank for no change.",
            required=False,
        ),
        discord: str = SlashOption(
            description="Write the updated Discord TAG. Leave blank for no change.",
            required=False,
        ),
        discord_id: str = SlashOption(
            description="Write the updated Discord ID. Leave blank for no change",
            required=False,
        ),
        description: str = SlashOption(
            description="Write the updated description of the issue. Leave blank for no change.",
            required=False,
        ),
    ):
        active_channels_json = load_json(active_scam_threads_json_path)
        for channel in active_channels_json:
            if channel["channel_id"] == interaction.channel.id:
                thread = interaction.channel
                messages = await thread.history(limit=5, oldest_first=True).flatten()
                if (ign and find_player(ign)) or not ign:
                    await messages[1].edit(
                        f"""
                            **Reporter: <@{channel['reporter_discord_id']}>**
                            **Scammer ign:** {ign if ign else channel['scammer_name']}
                            **Scammer discord tag:** {discord if discord else channel['scammer_discord_tag']}
                            **Scammer discord id:** {discord_id if discord_id else channel['scammer_discord_id']}
                            **Description:** {description if description else channel['description']}        
                            """
                    )
                    if ign:
                        channel["scammer_name"] = ign
                    if discord:
                        channel["scammer_discord_tag"] = discord
                    if discord_id:
                        channel["scammer_discord_id"] = discord_id
                    if description:
                        channel["description"] = description
                    save_json(active_channels_json, active_scam_threads_json_path)
                    await interaction.send(
                        f"Report info updated. Please check {messages[1].jump_url}",
                        ephemeral=True,
                        delete_after=15,
                    )

                else:
                    await interaction.send("Couldn't find IGN.")
                return True
        await interaction.send(
            "You shouldn't use that here.", ephemeral=True, delete_after=15
        )


def setup(bot):
    bot.add_cog(ScamCog(bot))
