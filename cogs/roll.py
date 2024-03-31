# Importing our custom variables/functions from backend
from typing import Optional

from backend.utils.logging import log
from backend.utils.roller import UnifiedDice, RollResult, RollResultFormatting, SolveMode, interpolate_color_hsv
from backend.utils.embed_templates import embed_template, error_template
from backend.utils.database import userdb, create_new_user

import discord
from discord import app_commands
from discord.ext import commands

from tinydb import Query


class RollCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Use @command.Cog.listener() for an event-listener (on_message, on_ready, etc.)
    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: rolling loaded")

    @app_commands.command(name="roll")
    @app_commands.choices(formatting=[
        app_commands.Choice(name="Default formatting", value="format_default"),
        app_commands.Choice(name="Sum only", value="format_sum"),
        app_commands.Choice(name="List only", value="format_list"),
        app_commands.Choice(name="List only (split at every 20 rolls)", value="format_list_split"),
    ])
    async def roll(self, interaction: discord.Interaction, rolls: str, formatting: Optional[app_commands.Choice[str]]):
        """
        Rolls a die [singular for now, I'm lazy]

        Parameters
        ------------
        rolls: str
            The rolls to... roll.
        formatting: Optional[app_commands.Choice[RollResultFormatting]]
            The format to show the results in. Defaults to a list view followed by sum.
        """
        rolls_split = rolls.split(" ")
        result = UnifiedDice.new(rolls_split[0]).solve(SolveMode.RANDOM)
        result_min = UnifiedDice.new(rolls_split[0]).solve(SolveMode.MIN)
        result_max = UnifiedDice.new(rolls_split[0]).solve(SolveMode.MAX)
        embed = embed_template(f"--- {rolls} ---")
        print(result.sum(), result_min.sum(), result_max.sum())
        embed.color = interpolate_color_hsv(result.sum(), result_min.sum(), result_max.sum())
        for tuple in result.format([[RollResultFormatting(formatting.value), 20]]):
            embed.add_field(name=tuple[0], value=tuple[1])
        await interaction.response.send_message(embed=embed)


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
# name of the cog (Example) to the name of your class.
async def setup(client):
    # Here, `Example` is the name of the class
    await client.add_cog(RollCog(client))
