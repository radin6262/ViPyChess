"""
VIChess - Bot Match
Play against Stockfish AI
Board is fixed: You (White) at bottom, AI (Black) at top
"""

import flet as ft
import threading
import chess
from lib.chess_board import ChessBoardUI
from lib.chess_logic import ChessGameLogic
from lib.widgets import GameControls, MoveHistory
from ai import CustomChessAI


class BotMatchPage:
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
        self.difficulty_text = None

        self.is_ai_thinking = False
        self.ai = CustomChessAI(difficulty=2)
        self.difficulty = 2
        self._pending_ai_move = None

    def show(self):
        """Display the bot match page"""
        self.page.controls.clear()

        # Back button
        back_btn = ft.TextButton(
            "← Back",
            on_click=lambda e: self._go_home(),
            style=ft.ButtonStyle(color=ft.Colors.BLUE_700),
        )

        # Player indicators
        player_row = ft.Row([
            ft.Text("Black (AI)", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.RED_700),
            ft.Container(expand=True),
            ft.Text("⬇You (White)", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_700),
        ], alignment=ft.MainAxisAlignment.CENTER)

        # Status
        self.status_text = ft.Text("Your turn (White)", size=20, weight=ft.FontWeight.W_600)

        # Move count + difficulty
        self.move_count_text = ft.Text("Move: 1", size=14, color=ft.Colors.GREY_700)

        difficulty_names = {1: "Easy", 2: "Medium", 3: "Hard"}
        self.difficulty_text = ft.Text(
            f"VIChess AI: {difficulty_names[self.difficulty]}",
        )

        # Board
        board_container = self.board_ui.create()

        # Controls with difficulty
        controls = GameControls(
            on_new_game=self._new_game,
            show_difficulty=True,
            on_difficulty_change=self._change_difficulty,
        )
        controls_row = controls.create()

        # Layout
        self.page.add(
            ft.Row([back_btn], alignment=ft.MainAxisAlignment.START),
            player_row,
            self.status_text,
            ft.Row([self.move_count_text, ft.Container(width=20), self.difficulty_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            board_container,
            ft.Container(height=10),
            controls_row,
            ft.Container(height=10),
        )

        self.page.update()

    def on_move(self, move: chess.Move):
        self._update_ui()

        if (
                not self.game.board.is_game_over()
                and self.game.board.turn == chess.BLACK
        ):
            self._trigger_ai_move()

    def _trigger_ai_move(self):
        if self.is_ai_thinking:
            return

        self.is_ai_thinking = True
        self.status_text.value = "VIChess AI is thinking..."
        self.page.update()

        threading.Thread(target=self._ai_worker, daemon=True).start()

    def _ai_worker(self):
        try:
            move = self.ai.choose_move(self.game.board.copy())
            self._pending_ai_move = move
        except Exception as e:
            print("AI error:", e)
            self._pending_ai_move = None

        self.is_ai_thinking = False

        self.page.run_thread(self._check_ai_move)

    def _check_ai_move(self):
        if self._pending_ai_move:
            move = self._pending_ai_move
            self._pending_ai_move = None

            self.game.board.push(move)
            self.board_ui.update()
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
            if turn == "Black":
                self.status_text.value = "VIChess AI is thinking..."
            else:
                self.status_text.value = f"Your turn ({turn})"

        half_moves = len(board.move_stack)
        full_moves = half_moves // 2 + 1
        self.move_count_text.value = f"Move: {full_moves}"

        self.board_ui.update()
        self.page.update()

    def _new_game(self):
        self.game.reset()
        self.board_ui.reset()

        self.ai = CustomChessAI(self.difficulty)

        self._pending_ai_move = None
        self.is_ai_thinking = False

        self._update_ui()

    def _change_difficulty(self, level: int):
        self.difficulty = level
        difficulty_names = {1: "Easy", 2: "Medium", 3: "Hard"}
        self.ai = CustomChessAI(level)
        self.difficulty_text.value = f"VIChess AI: {difficulty_names[level]}"
        self.difficulty_text.update()
        self._new_game()

    def _go_home(self):
        from pages.home_page import HomePage
        HomePage(self.page).show()