"""
Evaluation function for the chess AI
Combines material, positional, and tactical factors
"""

import chess
from ai.pst import get_pst_value
from ai.utils import (
    get_piece_value, is_endgame, square_to_coord,
    count_attackers, count_pieces, get_mobility, get_attacks
)
from ai.see import see


def evaluate_board(board: chess.Board) -> int:
    """
    Evaluate the board position from White's perspective

    Positive score = good for White
    Negative score = good for Black

    Returns:
        int: Score in centipawns
    """
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -100000
        else:
            return 100000

    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    endgame = is_endgame(board)

    score = 0

    # 1. Material + Positional (Piece-Square Tables)
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        value = get_piece_value(piece.piece_type)
        pst_value = get_pst_value(
            piece.piece_type,
            square,
            piece.color == chess.WHITE,
            endgame
        )

        total = value + pst_value

        if piece.color == chess.WHITE:
            score += total
        else:
            score -= total

    # 2. Bishop pair bonus
    if count_pieces(board, chess.WHITE, chess.BISHOP) == 2:
        score += 40
    if count_pieces(board, chess.BLACK, chess.BISHOP) == 2:
        score -= 40

    # 3. Mobility
    score += (get_mobility(board, chess.WHITE) - get_mobility(board, chess.BLACK)) * 8

    # 4. Center control
    score += evaluate_center_control(board)

    # 5. Pawn structure
    score += evaluate_pawn_structure(board, endgame)

    # 6. King safety
    score += evaluate_king_safety(board, endgame)

    # 7. Rook bonuses
    score += evaluate_rook_bonuses(board)

    # 8. Hanging/undefended pieces - using SEE
    score += evaluate_tactical_threats(board)

    # 9. Tempo
    if board.turn == chess.WHITE:
        score += 10
    else:
        score -= 10

    return score


def evaluate_center_control(board: chess.Board) -> int:
    """Evaluate control of the center squares using board.attackers"""
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    score = 0

    for square in center_squares:
        white_attackers = count_attackers(board, square, chess.WHITE)
        black_attackers = count_attackers(board, square, chess.BLACK)

        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                score += 30
            else:
                score -= 30

        score += (white_attackers - black_attackers) * 8

    return score


def evaluate_pawn_structure(board: chess.Board, endgame: bool) -> int:
    """Evaluate pawn structure"""
    score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None or piece.piece_type != chess.PAWN:
            continue

        color = piece.color
        rank = chess.square_rank(square)
        multiplier = 1 if color == chess.WHITE else -1

        passed = is_passed_pawn(board, square, color)
        if passed:
            bonus = 50 if not endgame else 100
            advancement = (rank if color == chess.WHITE else 7 - rank) * 10
            score += multiplier * (bonus + advancement)

            if is_protected(board, square, color):
                score += multiplier * 30

        if is_doubled_pawn(board, square, color):
            score -= multiplier * 20

        if is_isolated_pawn(board, square, color):
            score -= multiplier * 15

    return score


def is_passed_pawn(board: chess.Board, square: int, color: chess.Color) -> bool:
    """Check if a pawn is passed"""
    file = chess.square_file(square)
    rank = chess.square_rank(square)

    step = 1 if color == chess.WHITE else -1

    for r in range(rank + step, 8 if color == chess.WHITE else -1, step):
        for f in range(max(0, file - 1), min(8, file + 2)):
            sq = chess.square(f, r)
            piece = board.piece_at(sq)
            if piece and piece.color != color and piece.piece_type == chess.PAWN:
                return False
    return True


def is_protected(board: chess.Board, square: int, color: chess.Color) -> bool:
    """Check if a pawn is protected by another pawn"""
    file = chess.square_file(square)
    rank = chess.square_rank(square)

    for f in [file - 1, file + 1]:
        if f < 0 or f > 7:
            continue
        r = rank - 1 if color == chess.WHITE else rank + 1
        if 0 <= r < 8:
            sq = chess.square(f, r)
            piece = board.piece_at(sq)
            if piece and piece.color == color and piece.piece_type == chess.PAWN:
                return True
    return False


def is_doubled_pawn(board: chess.Board, square: int, color: chess.Color) -> bool:
    """Check if a pawn is doubled"""
    file = chess.square_file(square)
    count = 0

    for r in range(8):
        sq = chess.square(file, r)
        piece = board.piece_at(sq)
        if piece and piece.color == color and piece.piece_type == chess.PAWN:
            count += 1

    return count >= 2


def is_isolated_pawn(board: chess.Board, square: int, color: chess.Color) -> bool:
    """Check if a pawn is isolated"""
    file = chess.square_file(square)

    for f in [file - 1, file + 1]:
        if f < 0 or f > 7:
            continue
        for r in range(8):
            sq = chess.square(f, r)
            piece = board.piece_at(sq)
            if piece and piece.color == color and piece.piece_type == chess.PAWN:
                return False
    return True


def evaluate_king_safety(board: chess.Board, endgame: bool) -> int:
    """Evaluate king safety using board.attackers"""
    if endgame:
        score = 0
        for color in [chess.WHITE, chess.BLACK]:
            king_square = board.king(color)
            if king_square is None:
                continue

            rank, file = square_to_coord(king_square)
            center_dist = abs(3.5 - rank) + abs(3.5 - file)
            bonus = (6 - center_dist) * 15

            if color == chess.WHITE:
                score += bonus
            else:
                score -= bonus
        return score

    score = 0

    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        if king_square is None:
            continue

        rank, file = square_to_coord(king_square)
        multiplier = 1 if color == chess.WHITE else -1

        # Pawn shield - only pawns in front of the king
        pawn_shield = 0
        front_rank = rank + 1 if color == chess.WHITE else rank - 1

        for f in [file - 1, file, file + 1]:
            if 0 <= f < 8:
                sq = chess.square(f, front_rank)
                piece = board.piece_at(sq)
                if piece and piece.color == color and piece.piece_type == chess.PAWN:
                    pawn_shield += 1

        shield_bonus = pawn_shield * 25

        # Exposed king
        exposed_penalty = 0
        for f in [file - 1, file, file + 1]:
            if 0 <= f < 8:
                sq = chess.square(f, front_rank)
                piece = board.piece_at(sq)
                if piece is None or piece.color != color or piece.piece_type != chess.PAWN:
                    exposed_penalty += 25

        # Enemy attacks on king - using attack units
        enemy_color = not color
        attack_units = 0
        for sq in board.attackers(enemy_color, king_square):
            piece = board.piece_at(sq)
            if piece:
                weights = {
                    chess.QUEEN: 25,
                    chess.ROOK: 18,
                    chess.BISHOP: 12,
                    chess.KNIGHT: 12,
                    chess.PAWN: 8,
                    chess.KING: 30,
                }
                attack_units += weights.get(piece.piece_type, 10)

        score += multiplier * (shield_bonus - exposed_penalty - attack_units)

    return score


def evaluate_rook_bonuses(board: chess.Board) -> int:
    """Evaluate rook-specific bonuses"""
    score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None or piece.piece_type != chess.ROOK:
            continue

        rank, file = square_to_coord(square)
        multiplier = 1 if piece.color == chess.WHITE else -1
        bonus = 0

        # Rook on open/semi-open file
        friendly_pawn = False
        enemy_pawn = False

        for r in range(8):
            sq = chess.square(file, r)
            p = board.piece_at(sq)
            if p and p.piece_type == chess.PAWN:
                if p.color == piece.color:
                    friendly_pawn = True
                else:
                    enemy_pawn = True

        if not friendly_pawn and not enemy_pawn:
            bonus += 30  # Open file
        elif not friendly_pawn and enemy_pawn:
            bonus += 15  # Semi-open file

        # Rook on 7th rank
        if (rank == 6 and piece.color == chess.WHITE) or (rank == 1 and piece.color == chess.BLACK):
            bonus += 25

        # Connected rooks - check if another rook on same rank/file with no pieces between
        for sq in chess.SQUARES:
            if sq == square:
                continue
            p = board.piece_at(sq)
            if p and p.color == piece.color and p.piece_type == chess.ROOK:
                if chess.square_file(sq) == file:
                    r1 = min(rank, chess.square_rank(sq))
                    r2 = max(rank, chess.square_rank(sq))
                    connected = True
                    for r in range(r1 + 1, r2):
                        if board.piece_at(chess.square(file, r)):
                            connected = False
                            break
                    if connected:
                        bonus += 20
                        break
                elif chess.square_rank(sq) == rank:
                    f1 = min(file, chess.square_file(sq))
                    f2 = max(file, chess.square_file(sq))
                    connected = True
                    for f in range(f1 + 1, f2):
                        if board.piece_at(chess.square(f, rank)):
                            connected = False
                            break
                    if connected:
                        bonus += 20
                        break

        score += multiplier * bonus

    return score


def evaluate_tactical_threats(board: chess.Board) -> int:
    """
    Evaluate tactical threats using SEE.
    This is much more accurate than counting attackers.
    """
    score = 0

    # Check all legal moves for tactical opportunities
    for move in board.legal_moves:
        if board.is_capture(move):
            see_score = see(board, move)
            if see_score > 100:
                # Good capture - bonus
                if board.turn == chess.WHITE:
                    score += see_score // 2
                else:
                    score -= see_score // 2

    # Hanging pieces - use board.attackers for quick detection
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        white_attackers = count_attackers(board, square, chess.WHITE)
        black_attackers = count_attackers(board, square, chess.BLACK)

        if piece.color == chess.WHITE:
            if black_attackers > white_attackers:
                # Potentially hanging - check with SEE
                # Find a move that captures this piece
                for move in board.legal_moves:
                    if move.to_square == square and board.piece_at(move.from_square).color == chess.BLACK:
                        see_score = see(board, move)
                        if see_score > 0:
                            # It's actually a good capture
                            penalty = see_score // 2
                            score -= min(penalty, 500)
                        break
        else:
            if white_attackers > black_attackers:
                for move in board.legal_moves:
                    if move.to_square == square and board.piece_at(move.from_square).color == chess.WHITE:
                        see_score = see(board, move)
                        if see_score > 0:
                            penalty = see_score // 2
                            score += min(penalty, 500)
                        break

    return score