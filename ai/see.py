"""
Static Exchange Evaluation (SEE)
Determines the outcome of a capture sequence
"""

import chess


def see(board: chess.Board, move: chess.Move) -> int:
    """
    Static Exchange Evaluation

    Returns the material gain/loss from a capture sequence.
    Positive = good for the side making the move.
    """
    if not board.is_capture(move):
        return 0

    from_piece = board.piece_at(move.from_square)
    to_piece = board.piece_at(move.to_square)

    if from_piece is None or to_piece is None:
        return 0

    from_value = get_piece_value(from_piece.piece_type)
    to_value = get_piece_value(to_piece.piece_type)

    # Make a copy and play the move
    board_copy = board.copy()
    board_copy.push(move)

    # Start the exchange sequence
    gain = to_value

    # Recursively evaluate the exchange
    gain -= see_recursive(board_copy, move.to_square, from_value)

    return gain


def see_recursive(board: chess.Board, square: int, previous_value: int) -> int:
    """
    Recursive SEE evaluation
    """
    attacker_color = board.turn
    attackers = []

    # Find least valuable attacker using board.attackers
    for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        for sq in board.attackers(attacker_color, square):
            piece = board.piece_at(sq)
            if piece and piece.piece_type == piece_type:
                # Check if pinned using python-chess's built-in method
                if not board.is_pinned(attacker_color, sq):
                    attackers.append(sq)
                    break
        if attackers:
            break

    if not attackers:
        return 0

    attacker_sq = attackers[0]
    attacker_piece = board.piece_at(attacker_sq)
    attacker_value = get_piece_value(attacker_piece.piece_type)

    # Make the capture
    board.push(chess.Move(attacker_sq, square))

    # Check if there's a recapture using board.attackers
    enemy_color = not attacker_color
    has_recapture = False

    for sq in board.attackers(enemy_color, square):
        piece = board.piece_at(sq)
        if piece and piece.color == enemy_color:
            if not board.is_pinned(enemy_color, sq):
                has_recapture = True
                break

    if has_recapture:
        score = previous_value - see_recursive(board, square, attacker_value)
    else:
        score = previous_value

    board.pop()

    return max(0, score - attacker_value)


def see_simple(board: chess.Board, move: chess.Move) -> int:
    """Simplified SEE - MVV-LVA for move ordering"""
    if not board.is_capture(move):
        return 0

    from_piece = board.piece_at(move.from_square)
    to_piece = board.piece_at(move.to_square)

    if from_piece is None or to_piece is None:
        return 0

    from_value = get_piece_value(from_piece.piece_type)
    to_value = get_piece_value(to_piece.piece_type)

    return to_value - from_value


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