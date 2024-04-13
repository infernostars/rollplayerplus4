from typing import Optional, Self
import discord
class Parent:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = None

    def root(self):
        if isinstance(self.parent, Parent):
            return self.parent.root()
        else:
            return self.parent


class Menu(Parent):
    def __init__(self):
        super().__init__()
        self.components = []
        self.content = None
        self.embed = None

    def add_component(self, component):
        self.components.append(component)
        component.parent = self

    def make_view(self):
        view = discord.ui.View()
        for i in self.components:
            view.add_item(i)
        return view

    def render(self, interaction: discord.Interaction):
        pass

    def send(self, interaction: discord.Interaction):
        self.render(interaction)
        interaction.response.send_message(content=self.content, embed=self.embed, view=self.make_view())

    def edit(self, interaction: discord.Interaction):
        self.render(interaction)
        interaction.response.edit_message(content=self.content, embed=self.embed, view=self.make_view())

class Button(discord.ui.Button, Parent):
    pass

class MenuButton(Button):
    """
    A button used for navigation. (Non-navigation buttons are just Button)
    """
    def __init__(self, label: str, destination: Menu):
        super().__init__(label)
        self.destination = destination

    def callback(self, interaction: discord.Interaction, edit=True):
        if edit: self.destination.edit(interaction)
        else: self.destination.send(interaction)

class Game:
    def __init__(self):
        self.players = []

class JoinMenu(Menu):
    def render(self, interaction: discord.Interaction):
        self.content = f"{interaction.user.global_name} started a map game!"

class JoinButton(Button):
    def callback(self, interaction: discord.Interaction):
        game = self.root()
        if interaction.user not in game.players:
            game.players.append(interaction.user)

def start_game(interaction: discord.Interaction):
    game = Game()
    join = JoinMenu()
    join.parent = game
    join.send(interaction)