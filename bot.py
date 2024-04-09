import asyncio
import os
import sys

import threading
from asyncio import create_task

import discord.utils
from discord.ext import commands

from backend.config import discord_token, sync_server, should_sync, presence, version
from backend.utils.logging import log


class RollplayerBot(commands.Bot):
    coglist = []

    async def setup_hook(self) -> None:
        print(os.listdir('cogs'))
        for file in os.listdir('cogs'):  # load cogs
            if file.endswith('.py'):
                print(file)
                await bot.load_extension(f'cogs.{file[:-3]}')
                self.coglist.append(file[:-3])
                print(self.coglist)
        if should_sync:
            await self.tree.sync(guild=bot.get_guild(sync_server))


intents = discord.Intents.default()
intents.message_content = True

bot = RollplayerBot(intents=intents, command_prefix="r!")  # Setting prefix


# This is what gets run when the bot stars
@bot.event
async def on_ready():
    log.info(f"Patron Saint of Vorigaria, version {version}, online. [logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name=presence))


# Run the actual bot
if __name__ == "__main__":
    try:
        bot.run(discord_token)
    except discord.LoginFailure:
        log.critical("Invalid Discord Token. Please check your config file.")
        sys.exit()
    except Exception as err:
        log.critical(f"Error while connecting to Discord. Error: {err}")
        sys.exit()
