"""
Evaluation function for the chess AI
Combines material, positional, and tactical factors
"""

import chess
from ai.pst import get_pst_value
from ai.utils import get_piece_value, is_endgame


def evaluate_board(board: chess.Board) -> int:
    """
    Evaluate the board position from White's perspective

    Positive score = good for White
    Negative score = good for Black

    Returns:
        int: Score in centipawns
    """
    if board.is_checkmate():
        # Checkmate: return huge score
        if board.turn == chess.WHITE:
            return -100000  # Black wins
        else:
            return 100000  # White wins

    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    # Check if in endgame
    endgame = is_endgame(board)

    # Initialize score
    score = 0

    # Evaluate each piece
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        # Material value
        value = get_piece_value(piece.piece_type)

        # Piece-square table value
        pst_value = get_pst_value(
            piece.piece_type,
            square,
            piece.color == chess.WHITE,
            endgame
        )

        # Combine material and positional
        total = value + pst_value

        # Add to score (positive for White, negative for Black)
        if piece.color == chess.WHITE:
            score += total
        else:
            score -= total

    # Additional evaluation factors
    score += evaluate_mobility(board)
    score += evaluate_center_control(board)
    score += evaluate_pawn_structure(board)

    return score


def evaluate_mobility(board: chess.Board) -> int:
    """Evaluate piece mobility (number of legal moves)"""
    # Count legal moves for each side
    moves_white = 0
    moves_black = 0

    # Temporarily disable the turn check
    for move in board.legal_moves:
        if board.piece_at(move.from_square):
            piece = board.piece_at(move.from_square)
            if piece.color == chess.WHITE:
                moves_white += 1
            else:
                moves_black += 1

    # Mobility bonus (10 centipawns per move advantage)
    return (moves_white - moves_black) * 10


def evaluate_center_control(board: chess.Board) -> int:
    """Evaluate control of the center squares"""
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    score = 0

    for square in center_squares:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                score += 30
            else:
                score -= 30

    return score


def evaluate_pawn_structure(board: chess.Board) -> int:
    """Evaluate pawn structure (doubled, isolated, passed pawns)"""
    score = 0

    # Check for doubled pawns (penalty)
    white_pawns = []
    black_pawns = []

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN:
            file = chess.square_file(square)
            if piece.color == chess.WHITE:
                white_pawns.append(file)
            else:
                black_pawns.append(file)

    # Penalty for doubled pawns
    for file in set(white_pawns):
        count = white_pawns.count(file)
        if count > 1:
            score -= count * 20

    for file in set(black_pawns):
        count = black_pawns.count(file)
        if count > 1:
            score += count * 20

    return score