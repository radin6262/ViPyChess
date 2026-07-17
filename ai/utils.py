"""
Utility functions for the chess AI
"""

import chess


def get_piece_value(piece_type: int) -> int:
    """Get material value for a piece type"""
    values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000,
    }
    return values.get(piece_type, 0)


def is_endgame(board: chess.Board) -> bool:
    """Check if the position is in the endgame phase"""
    # Count non-pawn material
    total_material = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type != chess.PAWN and piece.piece_type != chess.KING:
            total_material += get_piece_value(piece.piece_type)

    # Endgame if less than 2 rooks or equivalent material
    return total_material < 1500


def square_to_coord(square: int) -> tuple:
    """Convert square index to (rank, file) tuple"""
    return (square // 8, square % 8)