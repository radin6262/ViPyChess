"""
Custom Chess AI - Public API
"""

import chess
import random
from ai.minimax import MinimaxSearch


class CustomChessAI:
    """
    Custom chess AI with adjustable difficulty

    Difficulty levels:
        1 = Easy (depth 2)
        2 = Medium (depth 3)
        3 = Hard (depth 5)
        4 = Expert (depth 10)
    """

    def __init__(self, difficulty: int = 2):
        self.difficulty = difficulty
        self.depth_map = {
            1: 2,
            2: 3,
            3: 5,
            4: 10,
        }
        self.depth = self.depth_map.get(difficulty, 3)
        self.name = "VIChess AI"
        self.search = MinimaxSearch(depth=self.depth)
        self.nodes_searched = 0

    def choose_move(self, board: chess.Board) -> chess.Move | None:
        if board.is_game_over():
            return None

        moves = list(board.legal_moves)
        if len(moves) == 1:
            return moves[0]

        move = self.search.search(board)
        self.nodes_searched = self.search.nodes_searched

        if move is None and moves:
            safe_moves = []
            for m in moves:
                board_copy = board.copy()
                board_copy.push(m)
                if not board_copy.is_check():
                    safe_moves.append(m)

            if safe_moves:
                center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
                center_moves = [m for m in safe_moves if m.to_square in center_squares]
                if center_moves:
                    return random.choice(center_moves)
                return random.choice(safe_moves)
            return random.choice(moves)

        return move

    def get_name(self) -> str:
        return f"{self.name} (Depth {self.depth})"

    def get_difficulty_name(self) -> str:
        names = {
            1: "Easy (Depth 2)",
            2: "Normal (Depth 3)",
            3: "Hard (Depth 5)",
            4: "Expert (Depth 10)",
        }
        return names.get(self.difficulty, "Normal (Depth 3)")

    def get_stats(self) -> dict:
        return {
            "name": self.name,
            "difficulty": self.difficulty,
            "depth": self.depth,
            "nodes_searched": self.nodes_searched,
        }