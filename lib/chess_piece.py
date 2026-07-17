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
            width=0,  # Will be set when board is sized
            height=0,  # Will be set when board is sized
            alignment=ft.Alignment(0, 0),  # Center the image inside
            content=ft.Image(
                src=image_path,
                fit=ft.BoxFit.CONTAIN,
            ),
            animate_position=150,
            animate_opacity=ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT),
            animate_scale=ft.Animation(duration=100, curve=ft.AnimationCurve.EASE_OUT),
            opacity=1.0,
            scale=1.0,
            visible=True,
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