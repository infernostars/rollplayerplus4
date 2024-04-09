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


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
class GamesCog(commands.GroupCog, group_name="game"):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: games loaded")

    @app_commands.command(name="tictactoe")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def tictactoe(self, interaction: discord.Interaction, size: app_commands.Range[int, 3, 5], row: Optional[app_commands.Range[int, 3, 5]]):
        """
        Plays some tic-tac-toe.

        Parameters
        ------------
        size: app_commands.Range[int, 3, 5]
            The size of the board. Ranges from 3 to 5.
        row: Optional[app_commands.Range[int, 3, 5]]
            The amount of letters in a row you need to win. Defaults to the board size, but can go down to 3.
        """
        if row is None:
            row = size #its probably expected that the row length = the size
        """
        Creates a tic-tac-toe game. Note that it doesn't log who clicked, so anyone can place. Try not to cheat?
        """
        if row > size:
            await interaction.response.send_message(error_template("Row length has to be less than or equal to the board size!"))
        await interaction.response.send_message("Pick a place to start!", view=TicTacToe(size, row))


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
# name of the cog to the name of your class.
async def setup(client):
    await client.add_cog(GamesCog(client))
