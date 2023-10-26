import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import argparse


class KnightAgent:
    """AI Agent for playing as the knight in the Isolation Game."""

    def __init__(self, game, knight_number, lookahead_depth=2):
        """
        Initialize the KnightAgent.

        Parameters:
        - game: Instance of the IsolationKnightGame.
        - knight_number: Integer, indicating which knight the agent is playing (1 or 2).
        - lookahead_depth: Depth to look ahead when evaluating moves. Defaults to 2.
        """
        self.game = game
        self.knight_number = knight_number
        self.lookahead_depth = lookahead_depth

    def get_legal_moves(self, position):
        """
        Returns all legal moves from the current position.

        Parameters:
        - position: Tuple (x,y) representing the current position.

        Returns:
        - List of tuples representing legal moves from the position.
        """
        moves = [
            (position[0] + move[0], position[1] + move[1])
            for move in self.game.knight_moves
        ]
        legal_moves = [
            move
            for move in moves
            if 0 <= move[0] < self.game.board_size
            and 0 <= move[1] < self.game.board_size
            and self.game.visited[move[0]][move[1]] == 0
        ]
        return legal_moves

    def warnsdorffs_rule(self, position):
        """
        Get sorted legal moves based on Warnsdorff's rule.

        Parameters:
        - position: Tuple (x,y) representing the current position.

        Returns:
        - List of sorted legal moves.
        """
        legal_moves = self.get_legal_moves(position)
        legal_moves.sort(key=lambda move: len(self.get_legal_moves(move)))
        return legal_moves

    def evaluate_position(self, position, depth):
        """
        Evaluate a position's desirability using a recursive search.

        Parameters:
        - position: Tuple (x,y) representing the current position.
        - depth: Depth of the recursive search.

        Returns:
        - Average score of all moves from the position.
        """
        if depth == 0:
            return len(self.get_legal_moves(position))

        possible_moves = self.warnsdorffs_rule(position)
        if not possible_moves:
            return -9999  # No legal moves, very undesirable

        scores = [self.evaluate_position(move, depth - 1) for move in possible_moves]
        return sum(scores) / len(scores)

    def make_move(self):
        """
        Make the best move for the agent's knight based on the evaluation function.
        
        Returns:
        None
        """
        knight_pos = (
            self.game.knight1_position
            if self.knight_number == 1
            else self.game.knight2_position
        )
        best_move = None
        best_value = -9999

        for move in self.warnsdorffs_rule(knight_pos):
            move_value = self.evaluate_position(move, self.lookahead_depth)
            if move_value > best_value:
                best_value = move_value
                best_move = move

        if best_move:
            self.game.on_square_click(best_move[0], best_move[1])


class IsolationKnightGame:
    """Main game class for the Isolation Knight Game."""

    def __init__(
        self, root, knight1_start=(0, 0), knight2_start=(7, 7), use_agent=False
    ):
        """
        Initialize the game and set up the board.

        Parameters:
        - root (tk.Tk): The main tkinter root window.
        - knight1_start (tuple): Tuple containing the starting coordinates of knight1. Defaults to (0,0).
        - knight2_start (tuple): Tuple containing the starting coordinates of knight2. Defaults to (7,7).
        - use_agent (bool): If True, knight2 will be controlled by an AI agent.

        Returns:
        None
        """
        self.root = root
        self.board_size = 8
        self.board = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]
        self.visited = [
            [0 for _ in range(self.board_size)] for _ in range(self.board_size)
        ]

        self.knight_moves = [
            (2, 1),
            (1, 2),
            (-1, 2),
            (-2, 1),
            (-2, -1),
            (-1, -2),
            (1, -2),
            (2, -1),
        ]

        self.current_knight = 1  # Start with knight1

        self.knight1_position = knight1_start
        self.knight2_position = knight2_start
        self.visited[self.knight1_position[0]][self.knight1_position[1]] = 1
        self.visited[self.knight2_position[0]][self.knight2_position[1]] = 2

        self.create_board()

        if use_agent:
            self.agent = KnightAgent(self, 2)

    def create_board(self):
        """
        Set up the GUI board, load knight images, and bind click events.

        Returns:
        None
        """
        image1 = Image.open("figs/white_knight.png")
        image2 = Image.open("figs/black_knight.png")
        self.knight1_image = ImageTk.PhotoImage(image1)
        self.knight2_image = ImageTk.PhotoImage(image2)

        for i in range(self.board_size):
            for j in range(self.board_size):
                color = self.determine_color(i, j)
                self.board[i][j] = tk.Label(self.root, bg=color, width=8, height=4)
                self.board[i][j].grid(row=i, column=j)
                self.board[i][j].bind(
                    "<Button-1>", lambda event, x=i, y=j: self.on_square_click(x, y)
                )

        self.board[self.knight1_position[0]][self.knight1_position[1]].config(
            image=self.knight1_image, width=58, height=58, anchor="center"
        )
        self.board[self.knight2_position[0]][self.knight2_position[1]].config(
            image=self.knight2_image, width=58, height=58, anchor="center"
        )

    def determine_color(self, i, j):
        """
        Determine the color of a given board square based on its state and position.

        Parameters:
        - i (int): Row index of the square.
        - j (int): Column index of the square.

        Returns:
        str: Color name or hex code representing the color of the square.
        """
        if self.visited[i][j] != 0:
            return "#FF6347" if (i + j) % 2 == 0 else "#8B0000"
        return "#F5F5DC" if (i + j) % 2 == 0 else "black"

    def on_square_click(self, x, y):
        """
        Handle a square being clicked by the user or AI, and perform game logic accordingly.

        Parameters:
        - x (int): Row index of the clicked square.
        - y (int): Column index of the clicked square.

        Returns:
        None
        """
        if self.current_knight == 1:
            if self.is_valid_move(self.knight1_position, (x, y)):
                self.move_knight(self.knight1_position, (x, y), self.knight1_image)
                self.knight1_position = (x, y)
                self.visited[x][y] = 1
                if not self.has_valid_moves(self.knight2_position):
                    messagebox.showinfo("Game Over", "Knight 1 Wins!")
                    return
                self.current_knight = 2
                if hasattr(self, "agent"):
                    self.agent.make_move()
                    return
        elif self.current_knight == 2:
            if self.is_valid_move(self.knight2_position, (x, y)):
                self.move_knight(self.knight2_position, (x, y), self.knight2_image)
                self.knight2_position = (x, y)
                self.visited[x][y] = 2
                if not self.has_valid_moves(self.knight1_position):
                    messagebox.showinfo("Game Over", "Knight 2 Wins!")
                    return
                self.current_knight = 1
        self.update_board()

    def has_valid_moves(self, position):
        """
        Check if a given knight has any valid moves left.

        Parameters:
        - position (tuple): Tuple containing the current coordinates of the knight.

        Returns:
        bool: True if there are valid moves available, False otherwise.
        """
        for move in self.knight_moves:
            next_move = (position[0] + move[0], position[1] + move[1])
            if (
                0 <= next_move[0] < self.board_size
                and 0 <= next_move[1] < self.board_size
                and self.visited[next_move[0]][next_move[1]] == 0
            ):
                return True
        return False

    def is_valid_move(self, start, end):
        """
        Validate whether moving a knight from a start position to an end position is allowed.

        Parameters:
        - start (tuple): Tuple containing the starting coordinates of the knight.
        - end (tuple): Tuple containing the desired end coordinates of the knight.

        Returns:
        bool: True if the move is valid, False otherwise.
        """
        if (
            end
            in [(start[0] + move[0], start[1] + move[1]) for move in self.knight_moves]
            and self.visited[end[0]][end[1]] == 0
        ):
            return True
        return False

    def move_knight(self, start, end, image):
        """
        Move a knight on the GUI board from the start position to the end position.

        Parameters:
        - start (tuple): Tuple containing the starting coordinates of the knight.
        - end (tuple): Tuple containing the desired end coordinates of the knight.
        - image (ImageTk.PhotoImage): Image of the knight to be moved.

        Returns:
        None
        """
        self.board[start[0]][start[1]].config(image="", width=8, height=4)
        self.board[end[0]][end[1]].config(
            image=image, width=58, height=58, anchor="center"
        )

    def update_board(self):
        """
        Update the colors of the board squares and the positions of the knights on the GUI board.

        Returns:
        None
        """
        for i in range(self.board_size):
            for j in range(self.board_size):
                color = self.determine_color(i, j)
                self.board[i][j].config(bg=color)


parser = argparse.ArgumentParser(
    description="Isolation Knight Game Command Line Options"
)
parser.add_argument(
    "--knight1",
    type=int,
    nargs=2,
    default=[0, 0],
    help="Starting position for knight 1 in format: x y",
)
parser.add_argument(
    "--knight2",
    type=int,
    nargs=2,
    default=[7, 7],
    help="Starting position for knight 2 in format: x y",
)
parser.add_argument("--agent", action="store_true", help="Use agent for knight 2")

args = parser.parse_args()

root = tk.Tk()
root.title("Isolation Knight Game")
game = IsolationKnightGame(
    root,
    knight1_start=tuple(args.knight1),
    knight2_start=tuple(args.knight2),
    use_agent=args.agent,
)
root.mainloop()
