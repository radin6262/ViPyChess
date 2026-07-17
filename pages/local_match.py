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

        # Layout
        self.page.add(
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
        )

        self.page.update()

    def on_move(self, move: chess.Move):
        self._update_ui()

    def _update_ui(self):
        board = self.game.board

        if board.is_checkmate():
            winner = "Black" if board.turn == chess.WHITE else "White"
            self.status_text.value = f"Checkmate! {winner} wins!"
        elif board.is_stalemate():
            self.status_text.value = "Stalemate! It's a draw!"
        elif board.is_insufficient_material():
            self.status_text.value = "Draw! Insufficient material."
        else:
            turn = "White" if board.turn == chess.WHITE else "Black"
            self.status_text.value = f"{turn}'s turn"

        half_moves = len(board.move_stack)
        full_moves = half_moves // 2 + 1
        self.move_count_text.value = f"Move: {full_moves}"

        self.history.update(board.move_stack)
        self.board_ui.update()
        self.page.update()

    def _new_game(self):
        self.game.reset()
        self.board_ui.reset()
        self.history.clear()
        self._update_ui()

    def _go_home(self):
        from pages.home_page import HomePage
        HomePage(self.page).show()