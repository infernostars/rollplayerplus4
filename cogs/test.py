# Importing our custom variables/functions from backend
import random
import sys
from typing import List
from typing import Optional

from backend.games.tictactoe import TicTacToe
from backend.config import version
from backend.utils.logging import log
from backend.utils.embed_templates import embed_template, error_template

import discord
from discord import app_commands
from discord.ext import commands

from tinydb import Query


class TestCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: test loaded")

    @app_commands.command(name="test")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def test(self, interaction: discord.Interaction):
        """
        Test command ooooOOOOOOOOOOOOOOOOOOOOOOOOOOOOooooooooOOOOOoOOOOOOOOOOOooooOOOOOOOoooOOOOOOOooooooo
        """
        await interaction.response.send_message("Example contents", view=TicTacToe(3))


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
# name of the cog to the name of your class.
async def setup(client):
    await client.add_cog(TestCog(client))
