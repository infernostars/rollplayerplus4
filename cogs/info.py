# Importing our custom variables/functions from backend
import random
import sys
from typing import Optional

from backend.config import version
from backend.utils.logging import log
from backend.utils.embed_templates import embed_template, error_template

import discord
from discord import app_commands
from discord.ext import commands

from tinydb import Query


class InfoCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: info loaded")

    @app_commands.command(name="info")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def info(self, interaction: discord.Interaction):
        """
        Info about the bot.
        """
        embed = embed_template(f"Rollplayer v{version} Info")
        embed.add_field(name="Python version", value=sys.version)
        embed.add_field(name="discord.py version", value=discord.__version__)
        await interaction.response.send_message(embed=embed, ephemeral=True)


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
# name of the cog to the name of your class.
async def setup(client):
    await client.add_cog(InfoCog(client))
