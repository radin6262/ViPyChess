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
        chess.QUEEN: 950,
        chess.KING: 20000,
    }
    return values.get(piece_type, 0)


def is_endgame(board: chess.Board) -> bool:
    """Check if the position is in the endgame phase"""
    total_material = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type != chess.PAWN and piece.piece_type != chess.KING:
            total_material += get_piece_value(piece.piece_type)
    return total_material < 1500


def square_to_coord(square: int) -> tuple:
    """Convert square index to (rank, file) tuple"""
    return (square // 8, square % 8)


def count_attackers(board: chess.Board, square: int, color: chess.Color) -> int:
    """Count attackers of a square by the given color"""
    return len(board.attackers(color, square))


def is_attacked(board: chess.Board, square: int, color: chess.Color) -> bool:
    """Check if a square is attacked by the given color"""
    return board.is_attacked_by(color, square)


def count_pieces(board: chess.Board, color: chess.Color, piece_type: int) -> int:
    """Count pieces of a specific type and color"""
    count = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color and piece.piece_type == piece_type:
            count += 1
    return count


def get_mobility(board: chess.Board, color: chess.Color) -> int:
    """Count legal moves for a specific color"""
    original_turn = board.turn
    board.turn = color
    moves = list(board.legal_moves)
    board.turn = original_turn
    return len(moves)


def get_attacks(board: chess.Board, square: int, color: chess.Color) -> list:
    """Get all attackers of a square by the given color"""
    return list(board.attackers(color, square))