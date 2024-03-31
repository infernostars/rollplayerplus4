# Importing our custom variables/functions from backend
from typing import Union

from backend.utils.logging import log
from backend.utils.embed_templates import embed_template, error_template

import discord
from discord import app_commands
from discord.ext import commands


class ContextMenuCog(commands.Cog):
    def __init__(self, client: discord.Client) -> None:
        self.client = client
        self.profile_pic = app_commands.ContextMenu(
            name='Get Profile Picture',
            callback=profile_pic,
        )
        self.client.tree.add_command(self.profile_pic)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.profile_pic.name, type=self.profile_pic.type)


    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: context menus loaded")


async def setup(client):
    await client.add_cog(ContextMenuCog(client))

async def profile_pic(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(file=await user.display_avatar.to_file(), ephemeral=True)
