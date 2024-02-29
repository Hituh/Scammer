import aiohttp
import nextcord
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SERVERS = os.getenv("SERVERS")
BOT_TOKEN = os.getenv("BOT_TOKEN")

from nextcord.ext import commands
from nextcord import Intents

bot = commands.Bot("=", intents=Intents(messages=True, guilds=True, members=True, message_content=True))

@bot.event
async def on_ready():
    print(
        f"        {bot.user} has connected to Discord!\n        Currently it is connected to the following servers:"
    )
    for guild in bot.guilds:
        print("       ", guild)

def load_cogs():
    counter = 0
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
            counter += 1
        elif os.path.isfile(filename):
            print(f"Unable to load {filename[:-3]}")
    return counter

def main():
    cogs_counter = load_cogs()
    if cogs_counter == 0:
        print("No cogs loaded.")
    else:
        print(f"{cogs_counter} cogs loaded.")
    bot.loop.create_task(startup())        
    bot.run(BOT_TOKEN)

async def startup():
    bot.session = aiohttp.ClientSession()


if __name__ == "__main__":
    main()
