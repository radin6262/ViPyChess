"""
VIRender Engine - Chess Board UI
"""

import flet as ft
import chess
import asyncio
from lib.chess_piece import BoardPiece


class ChessBoardUI:
    """
    Stack-based chess board with proper layering:
    - Board Layer (8x8 grid graphics)
    - Highlight Layer (selection, legal moves, check, last move)
    - Piece Layer (persistent piece controls)
    - Click Layer (64 transparent click areas - ON TOP)
    - Animation Layer (floating pieces for animations)
    - Promotion Layer (pawn promotion picker)
    """

    PIECE_IMAGES = {
        "P": "pieces/wp.svg",
        "R": "pieces/wr.svg",
        "N": "pieces/wn.svg",
        "B": "pieces/wb.svg",
        "Q": "pieces/wq.svg",
        "K": "pieces/wk.svg",
        "p": "pieces/bp.svg",
        "r": "pieces/br.svg",
        "n": "pieces/bn.svg",
        "b": "pieces/bb.svg",
        "q": "pieces/bq.svg",
        "k": "pieces/bk.svg",
    }

    def __init__(self, page: ft.Page, game_logic, on_move=None):
        self.page = page
        self.game = game_logic
        self.on_move = on_move

        # Board state
        self.selected_square = None
        self.animating = False
        self.board_pieces = []  # List of BoardPiece objects (persistent)
        self.piece_map = {}  # square -> BoardPiece for quick lookup

        # Last move tracking
        self.last_move_from = None
        self.last_move_to = None

        # Board dimensions
        self.square_size = 0
        self.board_size = 0
        self.piece_size = 0
        self.padding = 4

        # Colors
        self.light_color = ft.Colors.WHITE
        self.dark_color = ft.Colors.BROWN_600
        self.selected_color = ft.Colors.YELLOW_400
        self.highlight_color = ft.Colors.GREEN_300
        self.check_color = ft.Colors.RED_300
        self.last_move_color = ft.Colors.YELLOW_600

        # Layers
        self.board_stack = None
        self.board_layer = None
        self.click_layer = None
        self.highlight_layer = None
        self.piece_layer = None
        self.animation_layer = None
        self.promotion_layer = None
        self.click_areas = []  # Store click area references

        # Animation settings
        self.animation_duration = 150
        self.animation_sleep = 0.17

        # Promotion vars
        self.pending_promotion_from = None
        self.pending_promotion_to = None

    def square_to_xy(self, square: int) -> tuple:
        """Convert square to pixel coordinates (top-left of square)"""
        file = chess.square_file(square)
        rank = 7 - chess.square_rank(square)
        return (
            file * self.square_size,
            rank * self.square_size,
        )

    def create(self) -> ft.Stack:
        """Create the board UI with proper layering"""
        # Calculate board size
        available_width = self.page.width or 360
        board_size = min(available_width - 24, 480)
        self.square_size = board_size // 8
        self.board_size = self.square_size * 8
        self.piece_size = int(self.square_size * 0.82)

        # Clear state
        self.board_pieces.clear()
        self.piece_map.clear()
        self.click_areas.clear()
        self.last_move_from = None
        self.last_move_to = None

        # Create layers - ORDER MATTERS (bottom to top)
        self.board_layer = self._build_board_layer()
        self.highlight_layer = ft.Stack(
            width=self.board_size,
            height=self.board_size,
        )
        self.piece_layer = ft.Stack(
            width=self.board_size,
            height=self.board_size,
        )
        self.click_layer = self._build_click_layer()
        self.animation_layer = ft.Stack(
            width=self.board_size,
            height=self.board_size,
        )
        self.promotion_layer = ft.Stack(
            width=self.board_size,
            height=self.board_size,
        )

        # Main stack - promotion layer is the topmost
        self.board_stack = ft.Stack(
            width=self.board_size + self.padding * 2,
            height=self.board_size + self.padding * 2,
            controls=[
                self.board_layer,
                self.highlight_layer,
                self.piece_layer,
                self.click_layer,
                self.animation_layer,
                self.promotion_layer,
            ],
        )

        # Create persistent pieces
        self._create_all_pieces()

        return self.board_stack

    def _build_board_layer(self) -> ft.Container:
        """Build the 8x8 board grid (visual only, no click handlers)"""
        rows = []
        for rank in range(7, -1, -1):
            row = []
            for file in range(8):
                square = chess.square(file, rank)
                is_light = (rank + file) % 2 == 1

                container = ft.Container(
                    width=self.square_size,
                    height=self.square_size,
                    bgcolor=self.light_color if is_light else self.dark_color,
                )

                row.append(container)

            rows.append(
                ft.Row(
                    row,
                    spacing=0,
                    tight=True,
                )
            )

        return ft.Container(
            width=self.board_size,
            height=self.board_size,
            content=ft.Column(
                rows,
                spacing=0,
                tight=True,
            ),
        )

    def _build_click_layer(self) -> ft.Stack:
        """Build click overlay - transparent containers that capture all clicks"""
        click_stack = ft.Stack(
            width=self.board_size,
            height=self.board_size,
        )

        for rank in range(7, -1, -1):
            for file in range(8):
                square = chess.square(file, rank)
                x, y = self.square_to_xy(square)

                click_area = ft.Container(
                    width=self.square_size,
                    height=self.square_size,
                    left=x,
                    top=y,
                    bgcolor=ft.Colors.TRANSPARENT,
                    data=square,
                    on_click=lambda e, s=square: self._on_clicked_square(s),
                )

                click_stack.controls.append(click_area)
                self.click_areas.append(click_area)

        return click_stack

    def _create_all_pieces(self):
        """Create persistent piece objects for all pieces on the board"""
        for square in chess.SQUARES:
            piece = self.game.get_piece_at(square)
            if piece:
                self._create_piece(square, piece)

    def _create_piece(self, square: int, piece: chess.Piece):
        """Create a persistent piece object (no click handler needed)"""
        symbol = piece.symbol()
        image_path = self.PIECE_IMAGES.get(symbol, "")
        x, y = self.square_to_xy(square)

        # Create the piece data
        board_piece = BoardPiece(piece, square, image_path)

        # Update position - piece fills the entire square
        board_piece.update_position(
            x,
            y,
            self.square_size,
            self.piece_size,
        )

        # IMPORTANT: Disable click on piece so click layer handles it
        board_piece.control.on_click = None

        # Add to layers
        self.piece_layer.controls.append(board_piece.control)
        self.board_pieces.append(board_piece)
        self.piece_map[square] = board_piece

    def _get_piece_at(self, square: int) -> BoardPiece | None:
        """Get the piece object at a square"""
        return self.piece_map.get(square)

    def _move_piece(self, from_sq: int, to_sq: int):
        """Move a piece from one square to another"""
        piece_obj = self._get_piece_at(from_sq)
        if piece_obj is None:
            return

        # Remove from old square
        del self.piece_map[from_sq]

        # Update piece data
        piece_obj.square = to_sq

        # Update position
        x, y = self.square_to_xy(to_sq)
        piece_obj.update_position(
            x,
            y,
            self.square_size,
            self.piece_size,
        )

        # Add to new square
        self.piece_map[to_sq] = piece_obj

    def _get_castling_rook_move(self, king_from: int, king_to: int) -> tuple | None:
        """Get the rook's from and to squares for castling"""
        if king_from == chess.E1:
            if king_to == chess.G1:
                return (chess.H1, chess.F1)  # White kingside
            elif king_to == chess.C1:
                return (chess.A1, chess.D1)  # White queenside
        elif king_from == chess.E8:
            if king_to == chess.G8:
                return (chess.H8, chess.F8)  # Black kingside
            elif king_to == chess.C8:
                return (chess.A8, chess.D8)  # Black queenside
        return None

    async def _animate_castling_and_push(
        self,
        king_from: int,
        king_to: int,
        rook_from: int,
        rook_to: int,
        move: chess.Move,
    ):
        """Animate castling and push the move"""
        self.animating = True

        # Move king first
        king_obj = self._get_piece_at(king_from)
        if king_obj:
            self._move_piece(king_from, king_to)
            self.piece_layer.update()
            await asyncio.sleep(self.animation_sleep)

            # Pop effect on king landing
            king_obj.set_scale(1.2)
            self.piece_layer.update()
            await asyncio.sleep(0.08)
            king_obj.set_scale(1.0)
            self.piece_layer.update()

        # Move rook
        rook_obj = self._get_piece_at(rook_from)
        if rook_obj:
            self._move_piece(rook_from, rook_to)
            self.piece_layer.update()
            await asyncio.sleep(self.animation_sleep)

            # Pop effect on rook landing
            rook_obj.set_scale(1.2)
            self.piece_layer.update()
            await asyncio.sleep(0.08)
            rook_obj.set_scale(1.0)
            self.piece_layer.update()

        # Push the move
        self.game.board.push(move)

        # Track last move
        self.last_move_from = king_from
        self.last_move_to = king_to

        # Clear highlights
        self.selected_square = None
        self._clear_highlights()
        self._update_highlights()

        self.animating = False

        if self.on_move:
            self.on_move(move)

    def _on_clicked_square(self, square: int):
        """Handle click on a square (called from click layer)"""
        if self.game.is_game_over() or self.animating:
            return

        # Check if promotion picker is active
        if self.pending_promotion_from is not None:
            return

        piece = self.game.get_piece_at(square)

        # If no piece selected yet
        if self.selected_square is None:
            # Only select if there's a piece of the current player's color
            if piece and piece.color == self.game.board.turn:
                self.selected_square = square
                self._update_highlights()
            else:
                self._clear_highlights()
            return

        # If clicking on another own piece, switch selection
        if piece and piece.color == self.game.board.turn:
            self.selected_square = square
            self._update_highlights()
            return

        # Try to make a move
        move = chess.Move(self.selected_square, square)
        moving = self.game.get_piece_at(self.selected_square)

        # Handle pawn promotion
        if (
            moving
            and moving.piece_type == chess.PAWN
            and chess.square_rank(square) in (0, 7)
        ):
            self.pending_promotion_from = self.selected_square
            self.pending_promotion_to = square
            self._show_promotion_overlay()
            return

        if move in self.game.board.legal_moves:
            from_sq = self.selected_square
            self.selected_square = None

            # Check if this is a castling move
            if self.game.board.is_castling(move):
                rook_move = self._get_castling_rook_move(from_sq, square)
                if rook_move:
                    rook_from, rook_to = rook_move
                    self.page.run_task(
                        self._animate_castling_and_push,
                        from_sq,
                        square,
                        rook_from,
                        rook_to,
                        move,
                    )
                    return

            # Normal move
            self.page.run_task(self._animate_and_move, from_sq, square, move)
        else:
            self.selected_square = None
            self._update_highlights()

    def _show_promotion_overlay(self):
        """Show promotion picker overlay on the board (Lichess style)"""
        self.promotion_layer.controls.clear()

        is_white = self.game.board.turn == chess.WHITE
        promotion_square = self.pending_promotion_to
        file = chess.square_file(promotion_square)

        square_px = self.square_size
        x = file * square_px

        # Piece order: Queen, Rook, Bishop, Knight
        pieces = [
            ("q", chess.QUEEN),
            ("r", chess.ROOK),
            ("b", chess.BISHOP),
            ("n", chess.KNIGHT),
        ]

        # White promotes upward, Black promotes downward
        if is_white:
            # White: picker starts at top of the file (rank 7)
            start_y = 0
            order = pieces
        else:
            # Black: picker starts at bottom of the file (rank 0)
            start_y = self.board_size - square_px * 4
            order = list(reversed(pieces))

        picker_controls = []

        for i, (symbol, piece_type) in enumerate(order):
            img = f"pieces/{'w' if is_white else 'b'}{symbol}.svg"

            picker_controls.append(
                ft.Container(
                    width=square_px,
                    height=square_px,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.Border(
                        left=ft.border.BorderSide(1, ft.Colors.GREY_400),
                        right=ft.border.BorderSide(1, ft.Colors.GREY_400),
                        top=ft.border.BorderSide(1, ft.Colors.GREY_400),
                        bottom=ft.border.BorderSide(1, ft.Colors.GREY_400),
                    ),
                    on_click=lambda e, p=piece_type: self._finish_promotion(p),
                    content=ft.Image(
                        src=img,
                        width=self.piece_size,
                        height=self.piece_size,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                )
            )

        picker_column = ft.Column(
            spacing=0,
            controls=picker_controls,
        )

        self.promotion_layer.controls.append(
            ft.Container(
                left=x,
                top=start_y,
                content=picker_column,
            )
        )

        self.promotion_layer.update()

    def _finish_promotion(self, promotion_piece: int):
        """Complete the promotion and make the move"""
        # Clear promotion overlay
        self.promotion_layer.controls.clear()
        self.promotion_layer.update()

        move = chess.Move(
            self.pending_promotion_from,
            self.pending_promotion_to,
            promotion=promotion_piece,
        )

        self.pending_promotion_from = None
        self.pending_promotion_to = None

        self.selected_square = None

        self.page.run_task(
            self._animate_and_move,
            move.from_square,
            move.to_square,
            move,
        )

    async def _animate_and_move(self, from_sq: int, to_sq: int, move: chess.Move):
        """Animate a move using a temporary sprite in animation_layer."""
        self.animating = True

        moving_piece = self._get_piece_at(from_sq)
        if moving_piece is None:
            self.animating = False
            return

        # -------------------------------
        # Handle capture
        # -------------------------------
        captured = self._get_piece_at(to_sq)
        if captured:
            captured.set_opacity(0)
            self.piece_layer.update()
            await asyncio.sleep(0.10)

            if captured.control in self.piece_layer.controls:
                self.piece_layer.controls.remove(captured.control)

            if to_sq in self.piece_map:
                del self.piece_map[to_sq]

            captured.is_captured = True
            self.piece_layer.update()

        # -------------------------------
        # Hide the real moving piece
        # -------------------------------
        moving_piece.control.visible = False
        self.piece_layer.update()

        # -------------------------------
        # Create temporary animation sprite
        # -------------------------------
        from_x, from_y = self.square_to_xy(from_sq)

        anim = ft.Container(
            width=self.square_size,
            height=self.square_size,
            left=from_x,
            top=from_y,
            content=ft.Image(
                src=moving_piece.image_path,
                width=self.piece_size,
                height=self.piece_size,
                fit=ft.BoxFit.CONTAIN,
            ),
            animate_position=150,
        )

        self.animation_layer.controls.append(anim)
        self.animation_layer.update()

        await asyncio.sleep(0.05)

        # -------------------------------
        # Animate to destination
        # -------------------------------
        to_x, to_y = self.square_to_xy(to_sq)

        anim.left = to_x
        anim.top = to_y

        self.animation_layer.update()

        await asyncio.sleep(self.animation_sleep)

        # -------------------------------
        # Remove animation sprite
        # -------------------------------
        if anim in self.animation_layer.controls:
            self.animation_layer.controls.remove(anim)

        self.animation_layer.update()

        # -------------------------------
        # Move the real piece instantly
        # -------------------------------
        if from_sq in self.piece_map:
            del self.piece_map[from_sq]

        moving_piece.square = to_sq

        moving_piece.update_position(
            to_x,
            to_y,
            self.square_size,
            self.piece_size,
        )

        moving_piece.control.visible = True

        self.piece_map[to_sq] = moving_piece

        self.piece_layer.update()

        # -------------------------------
        # Landing pop
        # -------------------------------
        moving_piece.set_scale(1.2)
        self.piece_layer.update()
        await asyncio.sleep(0.08)

        moving_piece.set_scale(1.0)
        self.piece_layer.update()

        # -------------------------------
        # Update chess state
        # -------------------------------
        self.game.board.push(move)

        # Update promoted piece sprite
        if move.promotion:
            promoted_piece = self.game.board.piece_at(to_sq)
            if promoted_piece:
                moving_piece.piece = promoted_piece
                moving_piece.image_path = self.PIECE_IMAGES[promoted_piece.symbol()]
                # Update the image source
                moving_piece.control.content.src = moving_piece.image_path
                moving_piece.control.content.update()

        # Track last move
        self.last_move_from = from_sq
        self.last_move_to = to_sq

        self.selected_square = None
        self._clear_highlights()
        self._update_highlights()

        self.animating = False

        if self.on_move:
            self.on_move(move)

    def play_move(self, move: chess.Move):
        """
        Public method to play a move from outside (e.g., AI)
        This ensures the UI stays in sync with the game logic
        """
        if self.game.is_game_over() or self.animating:
            return

        from_sq = move.from_square
        to_sq = move.to_square

        # Check if this is a castling move
        if self.game.board.is_castling(move):
            rook_move = self._get_castling_rook_move(from_sq, to_sq)
            if rook_move:
                rook_from, rook_to = rook_move
                self.page.run_task(
                    self._animate_castling_and_push,
                    from_sq,
                    to_sq,
                    rook_from,
                    rook_to,
                    move,
                )
                return

        # Normal move
        self.page.run_task(self._animate_and_move, from_sq, to_sq, move)

    def _update_highlights(self):
        """Update square highlights"""
        self._clear_highlights()

        # Highlight last move first (so it's behind selection highlights)
        if self.last_move_from is not None and self.last_move_to is not None:
            self._highlight_square(self.last_move_from, self.last_move_color)
            self._highlight_square(self.last_move_to, self.last_move_color)

        if self.selected_square is not None:
            # Highlight selected square
            self._highlight_square(self.selected_square, self.selected_color)

            # Highlight legal moves
            for move in self.game.board.legal_moves:
                if move.from_square == self.selected_square:
                    self._highlight_square(move.to_square, self.highlight_color)

        # Check for check
        if self.game.board.is_check():
            king_color = self.game.board.turn
            king_square = self.game.board.king(king_color)
            if king_square is not None:
                self._highlight_square(king_square, self.check_color)

        self.highlight_layer.update()

    def _highlight_square(self, square: int, color: str):
        """Highlight a square"""
        x, y = self.square_to_xy(square)

        highlight = ft.Container(
            width=self.square_size,
            height=self.square_size,
            left=x,
            top=y,
            bgcolor=color,
            opacity=0.5,
            border_radius=4,
        )

        self.highlight_layer.controls.append(highlight)

    def _clear_highlights(self):
        """Clear all highlights"""
        self.highlight_layer.controls.clear()

    def update(self):
        """Refresh the board"""
        self._update_highlights()
        self.piece_layer.update()

    def reset(self):
        """Reset the board"""
        # Reset game logic
        self.game.reset()

        # Clear piece layer
        self.piece_layer.controls.clear()
        self.board_pieces.clear()
        self.piece_map.clear()

        # Clear animation layer
        self.animation_layer.controls.clear()

        # Clear promotion layer
        self.promotion_layer.controls.clear()

        # Reset highlights
        self.selected_square = None
        self.last_move_from = None
        self.last_move_to = None
        self._clear_highlights()

        # Reset promotion state
        self.pending_promotion_from = None
        self.pending_promotion_to = None

        # Recreate pieces
        self._create_all_pieces()

        self.animating = False
        self.piece_layer.update()
        self.highlight_layer.update()
        self.promotion_layer.update()

    def set_piece_images(self, image_paths: dict):
        """Override default piece images"""
        self.PIECE_IMAGES.update(image_paths)
        self.reset()