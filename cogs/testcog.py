# Importing our custom variables/functions from backend
from backend.utils.logging import log
from backend.utils.embed_templates import embed_template, error_template
from backend.utils.database import userdb, create_new_user

import discord
from discord import app_commands
from discord.ext import commands

from tinydb import Query


class TestCog(commands.GroupCog, group_name="testing"):
    def __init__(self, client):
        self.client = client

    # Use @command.Cog.listener() for an event-listener (on_message, on_ready, etc.)
    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: testing loaded")

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        """
        Replies with "pong".
        """
        # Use `await interaction.response.send_message()` to send a message
        await interaction.response.send_message("pong")

    @app_commands.command(name="testembed")
    async def test_embed(self, interaction: discord.Interaction):
        """
        Testing embed for if things go successfully.
        """
        embed = embed_template("Test embed", "Something went right!")
        await interaction.response.send_message(embeds=[embed])

    @app_commands.command(name="testembed2")
    async def test_embed2(self, interaction: discord.Interaction):
        """
        Testing embed for if things go wrong.
        """
        error_embed = error_template("Oops! Something went wrong!")
        await interaction.response.send_message(embeds=[error_embed])

    @app_commands.command(name="counter")
    async def counter(self, interaction: discord.Interaction):
        """
        Database testing; counts up when used, then pulls from db to get return value.
        """
        User = Query()
        if userdb.contains(User.id == interaction.user.id):
            try:
                usercount = userdb.get(User.id == interaction.user.id)["count"]
            except KeyError as e:
                usercount = 0
            usercount += 1
            userdb.update({"count": usercount}, User.id == interaction.user.id)
        else:
            create_new_user(interaction.user.id)
            userdb.update({"count": 1}, User.id == interaction.user.id)
        count = userdb.get(User.id == interaction.user.id)["count"]
        await interaction.response.send_message(f"your counter is {count}")

    @app_commands.command(name="test_one")
    async def test_one(self, interaction: discord.Interaction):
        """
        Undocumented; testing command for debugging, don't expect anything here to be permanent.
        """
        pass

# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
# name of the cog (Example) to the name of your class.
async def setup(client):
    # Here, `Example` is the name of the class
    await client.add_cog(TestCog(client))
