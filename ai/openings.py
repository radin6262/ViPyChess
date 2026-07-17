"""
Opening Book for the chess AI
Common openings to play without thinking
"""

import chess

# Opening moves as a list of UCI moves
OPENINGS = {
    "italian": [
        "e2e4",  # White: e4
        "e7e5",  # Black: e5
        "g1f3",  # White: Nf3
        "b8c6",  # Black: Nc6
        "f1c4",  # White: Bc4
    ],
    "sicilian": [
        "e2e4",  # White: e4
        "c7c5",  # Black: c5
        "g1f3",  # White: Nf3
        "d7d6",  # Black: d6
        "d2d4",  # White: d4
        "c5d4",  # Black: cxd4
        "f3d4",  # White: Nxd4
    ],
    "queens_gambit": [
        "d2d4",  # White: d4
        "d7d5",  # Black: d5
        "c2c4",  # White: c4
        "e7e6",  # Black: e6
        "b1c3",  # White: Nc3
        "g8f6",  # Black: Nf6
    ],
    "kings_indian": [
        "d2d4",  # White: d4
        "g8f6",  # Black: Nf6
        "c2c4",  # White: c4
        "g7g6",  # Black: g6
        "b1c3",  # White: Nc3
        "f8g7",  # Black: Bg7
    ],
    "french": [
        "e2e4",  # White: e4
        "e7e6",  # Black: e6
        "d2d4",  # White: d4
        "d7d5",  # Black: d5
        "b1c3",  # White: Nc3
        "g8f6",  # Black: Nf6
    ],
    "caro_kann": [
        "e2e4",  # White: e4
        "c7c6",  # Black: c6
        "d2d4",  # White: d4
        "d7d5",  # Black: d5
        "b1c3",  # White: Nc3
        "d5e4",  # Black: dxe4
    ],
}


def get_opening_move(board: chess.Board) -> chess.Move | None:
    """
    Get a move from the opening book if available

    Args:
        board: Current board position

    Returns:
        chess.Move or None if no opening move found
    """
    # Get the current move number (ply count)
    ply_count = len(board.move_stack)

    # Only use opening book for first 10 moves
    if ply_count >= 10:
        return None

    # For now, try all openings
    # In a full implementation, you'd track which opening is being played
    for opening_name, moves in OPENINGS.items():
        # Check if the current position matches this opening
        if ply_count < len(moves):
            # Check if the moves played so far match this opening
            match = True
            for i in range(ply_count):
                if board.move_stack[i].uci() != moves[i]:
                    match = False
                    break

            if match:
                # Return the next move in the opening
                next_move_uci = moves[ply_count]
                try:
                    return chess.Move.from_uci(next_move_uci)
                except ValueError:
                    return None

    return None


def get_opening_name(board: chess.Board) -> str | None:
    """Get the name of the opening being played"""
    ply_count = len(board.move_stack)

    for opening_name, moves in OPENINGS.items():
        if ply_count <= len(moves):
            match = True
            for i in range(ply_count):
                if board.move_stack[i].uci() != moves[i]:
                    match = False
                    break
            if match and ply_count >= 2:
                return opening_name

    return None