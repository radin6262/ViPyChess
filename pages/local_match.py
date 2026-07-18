"""
VIChess - Local 2-Player Match
Pass and play on the same device
Board is fixed: White at bottom, Black at top
"""

import flet as ft
import chess
from lib.chess_board import ChessBoardUI
from lib.chess_logic import ChessGameLogic
from lib.widgets import GameControls, MoveHistory


class LocalMatchPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.game = ChessGameLogic()
        self.board_ui = ChessBoardUI(
            self.page,
            self.game,
            on_move=self.on_move,
        )
        self.status_text = None
        self.move_count_text = None
        self.history = None

    def show(self):
        """Display the local match page"""
        self.page.controls.clear()

        # Back button
        back_btn = ft.TextButton(
            "← Back",
            on_click=lambda e: self._go_home(),
            style=ft.ButtonStyle(color=ft.Colors.BLUE_700),
        )

        # Player indicators
        player_row = ft.Row([
            ft.Text("⬆ Black", size=14, weight=ft.FontWeight.W_500),
            ft.Container(expand=True),
            ft.Text("⬇ White", size=14, weight=ft.FontWeight.W_500),
        ], alignment=ft.MainAxisAlignment.CENTER)

        # Status
        self.status_text = ft.Text("White's turn", size=20, weight=ft.FontWeight.W_600)

        # Move count
        self.move_count_text = ft.Text("Move: 1", size=14, color=ft.Colors.GREY_700)

        # Board
        board_stack = self.board_ui.create()

        # Move history
        self.history = MoveHistory()
        history_container = self.history.create()

        # Controls
        controls = GameControls(
            on_new_game=self._new_game,
        )
        controls_row = controls.create()

        # Layout - wrap everything in a column
        content_column = ft.Column(
            [
                ft.Row([back_btn], alignment=ft.MainAxisAlignment.START),
                player_row,
                self.status_text,
                self.move_count_text,
                ft.Container(height=10),
                board_stack,
                ft.Container(height=10),
                controls_row,
                ft.Container(height=10),
                history_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
        )

        # Wrap in container with top padding
        content = ft.Container(
            content=content_column,
            padding=ft.Padding(top=15),
        )

        self.page.add(content)
        self.page.update()

    def on_move(self, move: chess.Move):
        """Called after a move is made"""
        self._update_ui()

        board = self.game.board
        if board.is_game_over():
            self._show_game_over_dialog()

    def _update_ui(self):
        board = self.game.board

        if board.is_checkmate():
            winner = "Black" if board.turn == chess.WHITE else "White"
            self.status_text.value = f"Checkmate! {winner} wins!"
        elif board.is_stalemate():
            self.status_text.value = "Stalemate! It's a draw!"
        elif board.is_insufficient_material():
            self.status_text.value = "Draw! Insufficient material."
        elif board.can_claim_threefold_repetition():
            self.status_text.value = "Draw! Threefold repetition."
        elif board.can_claim_fifty_moves():
            self.status_text.value = "Draw! 50-move rule."
        else:
            turn = "White" if board.turn == chess.WHITE else "Black"
            self.status_text.value = f"{turn}'s turn"

        half_moves = len(board.move_stack)
        full_moves = half_moves // 2 + 1
        self.move_count_text.value = f"Move: {full_moves}"

        self.history.update(board.move_stack)
        self.board_ui.update()
        self.page.update()

    def _show_game_over_dialog(self):
        """Show a popup dialog for game over events"""
        board = self.game.board
        title = ""
        message = ""
        icon = ""
        color = ""

        if board.is_checkmate():
            winner = "Black" if board.turn == chess.WHITE else "White"

            icon = ft.Image(
                src="assets/icons/crown.svg",
                width=48,
                height=48,
            )

            title = "Checkmate!"
            message = f"{winner} wins the game!"

            color = (
                ft.Colors.BLUE_700
                if winner == "White"
                else ft.Colors.RED_700
            )

        elif board.is_stalemate():
            icon = ft.Image(
                src="assets/icons/stalemate.svg",
                width=48,
                height=48,
            )
            title = "Stalemate!"
            message = "It's a draw!"
            color = ft.Colors.ORANGE_700

        elif board.is_insufficient_material():
            icon = ft.Image(
                src="assets/icons/balance.svg",
                width=48,
                height=48,
            )
            title = "Insufficient Material"
            message = "Draw! Not enough pieces to checkmate."
            color = ft.Colors.ORANGE_700

        elif board.can_claim_threefold_repetition():
            icon = ft.Image(
                src="assets/icons/repeat.svg",
                width=48,
                height=48,
            )
            title = "Threefold Repetition"
            message = "Draw! The position has repeated three times."
            color = ft.Colors.ORANGE_700

        elif board.can_claim_fifty_moves():
            icon = ft.Image(
                src="assets/icons/hourglass.svg",
                width=48,
                height=48,
            )
            title = "50-Move Rule"
            message = "Draw! No capture or pawn move in 50 moves."
            color = ft.Colors.ORANGE_700

        else:
            return

        # Get move count
        half_moves = len(board.move_stack)
        full_moves = half_moves // 2 + 1

        # Build the dialog content
        dialog_content = ft.Column([
            ft.Text(
                f"{icon} {title}",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=color,
            ),
            ft.Container(height=10),
            ft.Text(
                message,
                size=18,
                color=ft.Colors.GREY_800,
            ),
            ft.Container(height=5),
            ft.Text(
                f"After {full_moves} moves",
                size=14,
                color=ft.Colors.GREY_600,
            ),
            ft.Container(height=15),
            ft.Row([
                ft.ElevatedButton(
                    "New Game",
                    on_click=lambda e: self._close_dialog_and_new_game(),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.BLUE_100,
                    ),
                ),
                ft.ElevatedButton(
                    "Close",
                    on_click=lambda e: self._close_dialog(),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.GREY_200,
                    ),
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ])

        # Create and show the dialog using show_dialog
        dialog = ft.AlertDialog(
            modal=True,
            content=dialog_content,
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        self.page.show_dialog(dialog)
        self.page.update()

    def _close_dialog(self):
        """Close the game over dialog"""
        self.page.pop_dialog()
        self.page.update()

    def _close_dialog_and_new_game(self):
        """Close dialog and start a new game"""
        self._close_dialog()
        self._new_game()

    def _new_game(self):
        """Reset the game"""
        self.game.reset()
        self.board_ui.reset()
        self.history.clear()
        self._update_ui()

    def _go_home(self):
        """Navigate back to home"""
        from pages.home_page import HomePage
        HomePage(self.page).show()