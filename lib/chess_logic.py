"""
VIChess - Shared Chess Logic
Wrapper around python-chess
"""

import chess


class ChessGameLogic:
    """Wrapper around python-chess board"""

    def __init__(self):
        self.board = chess.Board()
        self.move_history = []

    def reset(self):
        """Reset to starting position"""
        self.board.reset()
        self.move_history = []

    def make_move(self, from_sq: int, to_sq: int, promotion: int = chess.QUEEN) -> bool:
        """Make a move, returns True if successful"""
        move = chess.Move(from_sq, to_sq)

        piece = self.board.piece_at(from_sq)
        if piece and piece.piece_type == chess.PAWN:
            if chess.square_rank(to_sq) in [0, 7]:
                move = chess.Move(from_sq, to_sq, promotion=promotion)

        if move in self.board.legal_moves:
            self.board.push(move)
            self.move_history.append(move)
            return True
        return False

    def undo_move(self):
        """Undo last move"""
        if self.board.move_stack:
            self.board.pop()
            if self.move_history:
                self.move_history.pop()

    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    def get_result(self) -> str:
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            return f"Checkmate! {winner} wins!"
        elif self.board.is_stalemate():
            return "Stalemate! Draw."
        elif self.board.is_insufficient_material():
            return "Draw (insufficient material)."
        elif self.board.can_claim_threefold_repetition():
            return "Draw (threefold repetition)."
        elif self.board.can_claim_fifty_moves():
            return "Draw (50-move rule)."
        return "Game over."

    def get_legal_moves(self, square: int) -> list:
        return [m for m in self.board.legal_moves if m.from_square == square]

    def get_piece_at(self, square: int):
        return self.board.piece_at(square)

    def get_move_stack(self):
        return self.board.move_stack

    def is_king_in_check(self, color: chess.Color) -> bool:
        """Check if the king of the given color is in check"""
        king_square = self.board.king(color)
        if king_square is None:
            return False
        return self.board.is_check()

    def get_king_square(self, color: chess.Color) -> int | None:
        """Get the square of the king of the given color"""
        return self.board.king(color)