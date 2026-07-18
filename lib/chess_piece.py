"""
VIChess - Chess Piece Class
Persistent piece objects with identity
"""

import flet as ft
import chess


class BoardPiece:
    """
    A chess piece with persistent identity.
    The piece control stays alive for the entire game.
    """

    def __init__(self, piece: chess.Piece, square: int, image_path: str):
        self.piece = piece  # python-chess piece object
        self.square = square
        self.image_path = image_path
        self.is_captured = False

        # Create the UI control (created once, never recreated)
        # Use ft.Alignment(0, 0) which is the center
        self.control = ft.Container(
            width=0,
            height=0,
            alignment=ft.Alignment(0, 0),
            content=ft.Image(
                src=image_path,
                fit=ft.BoxFit.CONTAIN,
            ),
            opacity=1.0,
            scale=1.0,
            visible=True,
        )

    def create_animation_copy(self, square_size: int, piece_size: int) -> ft.Container:
        """Create a temporary copy used only for movement animation."""

        return ft.Container(
            width=square_size,
            height=square_size,
            left=self.control.left,
            top=self.control.top,
            content=ft.Image(
                src=self.image_path,
                width=piece_size,
                height=piece_size,
                fit=ft.BoxFit.CONTAIN,
            ),
            animate_position=150,
            opacity=1.0,
        )

    def update_position(self, x: float, y: float, square_size: int, piece_size: int):
        """Update the piece's position on the board"""
        self.control.width = square_size
        self.control.height = square_size
        self.control.left = x
        self.control.top = y

        # Update the image size inside the container
        if self.control.content:
            self.control.content.width = piece_size
            self.control.content.height = piece_size

    def set_opacity(self, opacity: float):
        """Fade the piece in/out"""
        self.control.opacity = opacity

    def set_scale(self, scale: float):
        """Scale the piece (for pop effects)"""
        self.control.scale = scale

    def capture(self):
        """Mark the piece as captured"""
        self.is_captured = True
        self.set_opacity(0)

    def uncapture(self):
        """Restore a captured piece (for undo)"""
        self.is_captured = False
        self.set_opacity(1.0)

    def get_symbol(self) -> str:
        """Get the piece symbol"""
        return self.piece.symbol()

    def get_color(self) -> chess.Color:
        """Get the piece color"""
        return self.piece.color

    def get_piece_type(self) -> int:
        """Get the piece type"""
        return self.piece.piece_type