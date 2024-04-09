# Importing our custom variables/functions from backend
from typing import Optional

from backend.utils.logging import log
from backend.utils.battle import casualties
from backend.utils.embed_templates import embed_template, error_template

import discord
from discord import app_commands
from discord.ext import commands

class BattleCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: battle loaded")

    @app_commands.command(name="casualties")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def casualties(self, interaction: discord.Interaction, side_a: int, side_b: int, loss: Optional[float]):
        """
        Calculates the casualties of a battle.

        Parameters
        ------------
        side_a: int
            The strength of the first side. Combination of both manpower and individual strength.
        side_b: int
            The strength of the second side.
        loss: Optional[float]
            Percentage of an army that will be lost if it loses the battle. Defaults to 1/3-2/3.
        """

        await interaction.response.send_message(embed=embed_template(casualties(side_a, side_b, loss)))


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
# name of the cogto the name of your class.
async def setup(client):
    await client.add_cog(BattleCog(client))