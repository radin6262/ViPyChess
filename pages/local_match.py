"""
VIChess - Local 2-Player Match
Pass and play on the same device
Board is fixed: White at bottom, Black at top
"""

import flet as ft
import chess
from lib.chess_board import ChessBoardUI
from lib.chess_logic import ChessGameLogic
from lib.widgets import MoveHistory


class LocalMatchPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.game = ChessGameLogic()
        self.board_ui = ChessBoardUI(
            self.page,
            self.game,
            on_move=self.on_move,
        )
        self.move_count_text = None
        self.status_text = None

    def show(self):
        """Display the local match page"""
        self.page.controls.clear()

        # Player indicator
        title = ft.Row(
            [
                ft.Text(
                    "White",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.BLUE_700,
                ),
                ft.Text(" vs ", size=14, color=ft.Colors.GREY_600),
                ft.Text(
                    "Black",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.RED_700,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        )

        # Status text
        self.status_text = ft.Text(
            "White's turn",
            size=18,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.GREY_800,
        )

        # Move count
        self.move_count_text = ft.Text("Move 1", size=14, color=ft.Colors.GREY_600)

        # Board
        board_stack = self.board_ui.create()

        # Controls row: New Game, Menu
        controls_row = ft.Row(
            [
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Image(
                                src="icons/refresh-cw.svg",
                                width=18,
                                height=18,
                            ),
                            ft.Text("New Game"),
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    on_click=lambda e: self._new_game(),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.BLUE_100,
                    ),
                ),
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Image(
                                src="icons/home.svg",
                                width=18,
                                height=18,
                            ),
                            ft.Text("Menu"),
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    on_click=lambda e: self._go_home(),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.GREY_200,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        # Main layout
        content_column = ft.Column(
            [
                title,
                self.status_text,
                ft.Row([self.move_count_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                board_stack,
                ft.Container(height=10),
                controls_row,
                ft.Container(height=10),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
        )

        # Wrap in container with padding
        content = ft.Container(
            content=content_column,
            padding=ft.Padding(top=15),
        )

        self.page.add(content)
        self.page.update()

        # Initially enable interaction
        self.board_ui.set_interactive(True)

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
            self.move_count_text.value = "Game Over"
        elif board.is_stalemate():
            self.status_text.value = "Stalemate! It's a draw!"
            self.move_count_text.value = "Draw"
        elif board.is_insufficient_material():
            self.status_text.value = "Draw! Insufficient material."
            self.move_count_text.value = "Draw"
        elif board.can_claim_threefold_repetition():
            self.status_text.value = "Draw! Threefold repetition."
            self.move_count_text.value = "Draw"
        elif board.can_claim_fifty_moves():
            self.status_text.value = "Draw! 50-move rule."
            self.move_count_text.value = "Draw"
        else:
            turn = "White" if board.turn == chess.WHITE else "Black"
            self.status_text.value = f"{turn}'s turn"
            half_moves = len(board.move_stack)
            full_moves = half_moves // 2 + 1
            self.move_count_text.value = f"Move {full_moves}"

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

        half_moves = len(board.move_stack)
        full_moves = half_moves // 2 + 1

        dialog_content = ft.Column([
            icon,
            ft.Container(height=10),
            ft.Text(
                title,
                size=32,
                weight=ft.FontWeight.BOLD,
                color=color,
            ),
            ft.Container(height=5),
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
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Image(
                                src="icons/refresh-cw.svg",
                                width=18,
                                height=18,
                            ),
                            ft.Text("New Game"),
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    on_click=lambda e: self._close_dialog_and_new_game(),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.BLUE_100,
                    ),
                ),
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Image(
                                src="icons/home.svg",
                                width=18,
                                height=18,
                            ),
                            ft.Text("Menu"),
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    on_click=lambda e: self._close_dialog_and_go_home(),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.GREY_200,
                    ),
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ])

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

    def _close_dialog_and_go_home(self):
        """Close dialog and go home"""
        self._close_dialog()
        self._go_home()

    def _new_game(self):
        """Reset the game"""
        self.game.reset()
        self.board_ui.reset()
        self.board_ui.set_interactive(True)
        self._update_ui()

    def _go_home(self):
        """Navigate back to home"""
        from pages.home_page import HomePage
        HomePage(self.page).show()