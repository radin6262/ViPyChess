"""
VIChess - Shared Chess Logic
Wrapper around python-chess
"""

import chess


class ChessGameLogic:
    """Wrapper around python-chess board"""

    def __init__(self):
        self.board = chess.Board()

    def reset(self):
        """Reset to starting position"""
        self.board.reset()

    def make_move(self, from_sq: int, to_sq: int, promotion: int = chess.QUEEN) -> bool:
        """Make a move, returns True if successful"""
        move = chess.Move(from_sq, to_sq)

        piece = self.board.piece_at(from_sq)
        if piece and piece.piece_type == chess.PAWN:
            if chess.square_rank(to_sq) in [0, 7]:
                move = chess.Move(from_sq, to_sq, promotion=promotion)

        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def undo_move(self):
        """Undo last move"""
        if self.board.move_stack:
            self.board.pop()

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
        return "Game over."

    def get_legal_moves(self, square: int) -> list:
        return [m for m in self.board.legal_moves if m.from_square == square]

    def get_piece_at(self, square: int):
        return self.board.piece_at(square)

    def get_move_stack(self):
        return self.board.move_stack