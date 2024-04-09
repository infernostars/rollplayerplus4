from typing import List

import discord

# Defines a custom button that contains the logic of the game.
# The ['TicTacToe'] bit is for type hinting purposes to tell your IDE or linter
# what the type of `self.view` is. It is not required.
class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It's now O's turn."
        else:
            self.style = discord.ButtonStyle.primary
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It's now X's turn."

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = 'X won!'
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


class TicTacToe(discord.ui.View):
    # This tells the IDE or linter that all our children will be TicTacToeButtons
    # This is not required
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self, size, row):
        super().__init__()
        self.size = size
        self.current_player = self.X
        self.board = [x[:] for x in [[0] * size] * size]
        self.row = row

        # Our board is made up of 3-5 by 3-5 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for x in range(size):
            for y in range(size):
                self.add_item(TicTacToeButton(x, y))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        """Returns the 'mark' of the player with a row of the given length."""
        width = range(len(self.board))
        height = range(len(self.board[0]))
        # Do four scans across the board -- right, down, and diagonals.
        for dx, dy in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            edges = []
            if dx > 0:
                # scanning right, start from left edge
                edges += [(0, y) for y in height]
            if dy > 0:
                # scanning down, start from top edge
                edges += [(x, 0) for x in width]
            if dy < 0:
                # scanning up, start from bottom edge
                edges += [(x, height[-1]) for x in width]
            for ex, ey in edges:
                mark = 0
                row = 0
                x, y = ex, ey
                while x in width and y in height:
                    if self.board[x][y] == mark:
                        row += 1
                    else:
                        mark = self.board[x][y]
                        row = 1
                    if mark != 0 and row >= self.row:
                        return mark
                    x, y = x + dx, y + dy

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None