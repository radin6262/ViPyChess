"""
Custom Chess AI - Public API
The UI only interacts with this class
"""

import chess
import random
from ai.minimax import MinimaxSearch


class CustomChessAI:
    """
    Custom chess AI with adjustable difficulty

    Difficulty levels:
        1 = Easy (depth 1) - makes obvious mistakes
        2 = Medium (depth 3) - decent player
        3 = Hard (depth 5) - strong player
        4 = Expert (depth 6) - very strong
    """

    def __init__(self, difficulty: int = 2):
        """
        Initialize the AI

        Args:
            difficulty: 1-4, higher = stronger
        """
        self.difficulty = difficulty
        self.depth_map = {
            1: 1,   # Easy
            2: 3,   # Medium
            3: 5,   # Hard
            4: 7,   # Expert
        }
        self.depth = self.depth_map.get(difficulty, 3)
        self.name = f"VIChess AI"
        self.search = MinimaxSearch(depth=self.depth)
        self.nodes_searched = 0

    def choose_move(self, board: chess.Board) -> chess.Move | None:
        """
        Choose the best move for the current position

        Args:
            board: Current board position

        Returns:
            Best move found, or None if game is over
        """
        if board.is_game_over():
            return None

        # If only one legal move, play it
        moves = list(board.legal_moves)
        if len(moves) == 1:
            return moves[0]

        # Use minimax search
        move = self.search.search(board)
        self.nodes_searched = self.search.nodes_searched

        # Fallback to random if something went wrong
        if move is None:
            return random.choice(moves)

        return move

    def get_name(self) -> str:
        """Get the AI's name"""
        return f"{self.name} (Depth {self.depth})"

    def get_difficulty_name(self) -> str:
        """Get the difficulty level name"""
        names = {
            1: "Easy (Depth 1)",
            2: "Medium (Depth 3)",
            3: "Hard (Depth 5)",
            4: "Expert (Depth 7)",
        }
        return names.get(self.difficulty, "Medium (Depth 3)")

    def get_stats(self) -> dict:
        """Get AI statistics"""
        return {
            "name": self.name,
            "difficulty": self.difficulty,
            "depth": self.depth,
            "nodes_searched": self.nodes_searched,
        }