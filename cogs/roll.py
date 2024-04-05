# Importing our custom variables/functions from backend
from typing import Optional

from backend.utils.logging import log
from backend.utils.lerp import interpolate_color_hsv, normalize
from backend.utils.roller import UnifiedDice, RollResultFormatting, SolveMode, RollException
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
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def roll(self, interaction: discord.Interaction, rolls: Optional[str], formatting: Optional[app_commands.Choice[str]]):
        """
        Rolls one or more dice.

        Parameters
        ------------
        rolls: str
            The rolls to roll, separated by spaces. For example: "1d100 2d20 1d6".
        formatting: Optional[app_commands.Choice[RollResultFormatting]]
            The format to show the results in. Defaults to a list view followed by sum.
        """
        if not rolls:
            rolls = "1d100"

        # Split the input string into individual roll expressions
        roll_expressions = rolls.split()

        results = []
        result_mins = []
        result_maxs = []

        # Roll each expression and collect the results
        for roll_expression in roll_expressions:
            try:
                result = UnifiedDice.new(roll_expression).solve(SolveMode.RANDOM)
                result_min = UnifiedDice.new(roll_expression).solve(SolveMode.MIN)
                result_max = UnifiedDice.new(roll_expression).solve(SolveMode.MAX)
                results.append(result)
                result_mins.append(result_min)
                result_maxs.append(result_max)
            except RollException as exc:
                await interaction.response.send_message(embed=error_template(exc.information))
                return

        try:
            format = RollResultFormatting(formatting.value)
        except:
            format = RollResultFormatting.FORMAT_DEFAULT

        embed = embed_template(f"--- {' '.join(roll_expressions)} ---")

        normalized_results = [normalize(sum(mini.rolls), sum(maxi.rolls), sum(result.rolls)) for mini, maxi, result in zip(result_mins, result_maxs, results)]
        normalized_color_value = sum(normalized_results) / len(normalized_results)

        embed.color = interpolate_color_hsv(normalized_color_value)

        for i, result in enumerate(results):
            try:
                for tuple in result.format([[format, 20]]):
                    if len(tuple[1]) > 1024:
                        raise RollException("Roll result too long.")
                    embed.add_field(name=f"{tuple[0]}", value=tuple[1], inline=False)
            except:
                embed.add_field(name=f"{roll_expressions[i]} - Your result was too long, so the format changed to sum only.", value="", inline=False)
                for tuple in result.format([[RollResultFormatting.FORMAT_SUM, 20]]):
                    embed.add_field(name=tuple[0], value=tuple[1])

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roll_help")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def help(self, interaction: discord.Interaction):
        """
        Help with /roll's syntax.
        """
        await interaction.response.send_message("""The syntax of a roll is composed of 3 parts.
`xdy+z` - x is the amount of dice rolled, y is the size of the die, and z is a modifier. x and z can be omitted, but y cannot (unless you enter nothing, which will roll a base d100).
First, y can be either a number, like 100, in which case the roll is between 1 and that maximum (inclusive),
Or it can be a range, like 50:100, in which case it will roll between both extremes (still inclusive).
Next, there are modifiers. The most basic type is math operations, like +, -, \*, and /. You can tack them onto a roll (like `d100+5*3`) and they will modify the result of the roll (in order, no PEMDAS).
Then you have the i operator, the most complex one. It lets you choose which rolls will be affected by modifiers. This can best be explained with two examples:
- `3d100i1,3:+20` will roll 3 dice and then add 20 to the first and third.
- `3d100i1,3:+20;2,-5` will do the same, and then subtract 5 from the second.
Lastly, you can roll multiple different sets of dice in the same command (like `5d100+5 5d100`).
That should be all you need to know about rolling with Rollplayer!""", ephemeral=True)


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
# name of the cog (Example) to the name of your class.
async def setup(client):
    # Here, `Example` is the name of the class
    await client.add_cog(RollCog(client))
