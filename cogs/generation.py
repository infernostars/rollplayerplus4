# Importing our custom variables/functions from backend
from typing import Optional

from backend.utils.logging import log
from backend.utils.generation import get_random_username
from backend.utils.language import s
from backend.utils.embed_templates import embed_template, error_template

import discord
from discord import app_commands
from discord.ext import commands

class GenerationCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: generation loaded")

    @app_commands.command(name="username")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def username(self, interaction: discord.Interaction, count: Optional[app_commands.Range[int, 1, 10]]):
        if count is None:
            count = 1
        usernames = []
        for i in range(count):
            usernames.append(get_random_username())
        await interaction.response.send_message(embeds=[embed_template(f"Username{s(count)} generated!",
                                                                       "\n".join(usernames))])

# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
# name of the cogto the name of your class.
async def setup(client):
    await client.add_cog(GenerationCog(client))