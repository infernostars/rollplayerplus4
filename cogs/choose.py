# Importing our custom variables/functions from backend
import random
from typing import Optional

from backend.utils.logging import log
from backend.utils.language import list_format
from backend.utils.embed_templates import embed_template, error_template

import discord
from discord import app_commands
from discord.ext import commands

from tinydb import Query


class ChooseCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: choose loaded")

    @app_commands.command(name="choose")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def choose(self, interaction: discord.Interaction, options: str, count: Optional[int], unique: Optional[bool]):
        """
        Rolls one or more dice.

        Parameters
        ------------
        options: str
            A list of options, split by commas.
        count: Optional[int]
        unique: Optional[bool]
            If true, no option will be picked twice.

        """
        if count is None:
            count = 1
        if unique is None:
            unique = True

        option_list = options.split(",")
        option_list = [x.strip() for x in option_list]
        if len(option_list) >= count:
            if count > 0:
                if unique:
                    await interaction.response.send_message(
                        embed=embed_template(f"let's pick... {list_format(random.sample(option_list, k=count))}."))
                else:
                    await interaction.response.send_message(
                        embed=embed_template(f"let's pick... {list_format(random.choices(option_list,k=count))}."))
            else:
                await interaction.response.send_message(embed=error_template("Asked for zero or negative choices!"))
        else:
            await interaction.response.send_message(embed=error_template("Asked for too many choices!"))

# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
# name of the cogto the name of your class.
async def setup(client):
    await client.add_cog(ChooseCog(client))
