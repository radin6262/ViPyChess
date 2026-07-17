"""
Minimax search with alpha-beta pruning
"""

import time
import chess

from ai.evaluation import evaluate_board
from ai.openings import get_opening_move


class MinimaxSearch:
    """Minimax search with alpha-beta pruning"""

    def __init__(self, depth: int = 3):
        self.depth = depth
        self.nodes_searched = 0
        self.time_limit = 5.0

    def search(self, board: chess.Board) -> chess.Move | None:
        """Find the best move"""

        if board.is_game_over():
            return None

        opening = get_opening_move(board)
        if opening is not None:
            return opening

        self.nodes_searched = 0
        start_time = time.time()

        moves = list(board.legal_moves)

        if not moves:
            return None

        if len(moves) == 1:
            return moves[0]

        maximizing = board.turn == chess.WHITE

        best_move = moves[0]

        if maximizing:
            best_score = -float("inf")
        else:
            best_score = float("inf")

        # Search captures first
        moves.sort(
            key=lambda m: board.is_capture(m),
            reverse=True,
        )

        for move in moves:

            board_copy = board.copy()
            board_copy.push(move)

            if board_copy.is_checkmate():
                return move

            score = self._minimax(
                board_copy,
                self.depth - 1,
                -float("inf"),
                float("inf"),
                board_copy.turn == chess.WHITE,
                start_time,
            )

            if maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                if score < best_score:
                    best_score = score
                    best_move = move

        print(
            f"AI searched {self.nodes_searched:,} nodes "
            f"(score={best_score})"
        )

        return best_move

    def _minimax(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool,
        start_time: float,
    ) -> float:

        self.nodes_searched += 1

        if time.time() - start_time > self.time_limit:
            return evaluate_board(board)

        if depth == 0 or board.is_game_over():
            return evaluate_board(board)

        moves = list(board.legal_moves)

        moves.sort(
            key=lambda m: board.is_capture(m),
            reverse=True,
        )

        if is_maximizing:

            value = -float("inf")

            for move in moves:

                board.push(move)

                value = max(
                    value,
                    self._minimax(
                        board,
                        depth - 1,
                        alpha,
                        beta,
                        False,
                        start_time,
                    ),
                )

                board.pop()

                alpha = max(alpha, value)

                if alpha >= beta:
                    break

            return value

        else:

            value = float("inf")

            for move in moves:

                board.push(move)

                value = min(
                    value,
                    self._minimax(
                        board,
                        depth - 1,
                        alpha,
                        beta,
                        True,
                        start_time,
                    ),
                )

                board.pop()

                beta = min(beta, value)

                if alpha >= beta:
                    break

            return value