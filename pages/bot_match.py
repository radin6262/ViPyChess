"""
VIChess - Bot Match
Play against VIChess AI
"""

import flet as ft
import threading
import asyncio
import chess
from lib.chess_board import ChessBoardUI
from lib.chess_logic import ChessGameLogic
from lib.widgets import MoveHistory
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
        self.move_count_text = None
        self.difficulty_text = None
        self.history = None
        self.spinner_container = None
        self.player_indicator = None
        self.difficulty_buttons = {}

        self.is_ai_thinking = False
        self.ai = CustomChessAI(difficulty=2)
        self.difficulty = 2
        self._pending_ai_move = None

    def show(self):
        """Display the bot match page"""
        self.page.controls.clear()

        # Header: Player indicator with spinner
        self.spinner_container = ft.Container(
            content=ft.ProgressRing(
                width=20,
                height=20,
                stroke_width=2,
            ),
            visible=False,
        )

        title = ft.Row(
            [
                ft.Text(
                    "You (White)",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.BLUE_700,
                ),
                ft.Text(" vs ", size=14, color=ft.Colors.GREY_600),
                ft.Text(
                    "AI (Black)",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.RED_700,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        )

        self.player_indicator = ft.Stack(
            width=self.board_ui.board_size,  # or any fixed width
            controls=[
                ft.Container(
                    content=title,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=self.spinner_container,
                    alignment=ft.Alignment(1, 0),
                    right=0,
                ),
            ],
        )

        # Move count + difficulty (no status text)
        self.move_count_text = ft.Text("Move 1", size=14, color=ft.Colors.GREY_600)

        difficulty_names = {1: "Easy", 2: "Normal", 3: "Hard", 4: "Expert"}
        self.difficulty_text = ft.Text(
            f"AI: {difficulty_names[self.difficulty]}",
            size=14,
            color=ft.Colors.BLUE_700,
            weight=ft.FontWeight.W_500,
        )

        # Board
        board_stack = self.board_ui.create()

        difficulty_icons = {
            1: "icons/feather.svg",
            2: "icons/crosshair.svg",
            3: "icons/shield.svg",
            4: "icons/cpu.svg",
        }

        # Difficulty buttons
        self.difficulty_buttons = {}
        difficulty_names = {1: "Easy", 2: "Normal", 3: "Hard", 4: "Expert"}

        difficulty_buttons_row = ft.Row(
            [],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
            wrap=True,
        )

        for level in [1, 2, 3, 4]:
            btn = ft.Button(
                content=ft.Row(
                    [
                        ft.Image(
                            src=difficulty_icons[level],
                            width=18,
                            height=18,
                        ),
                        ft.Text(difficulty_names[level]),
                    ],
                    spacing=6,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                on_click=lambda e, l=level: self._change_difficulty(l),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    bgcolor=ft.Colors.BLUE_100 if self.difficulty == level else None,
                ),
            )

            self.difficulty_buttons[level] = btn
            difficulty_buttons_row.controls.append(btn)

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
                self.player_indicator,
                ft.Row([
                    self.move_count_text,
                    ft.Container(width=20),
                    self.difficulty_text,
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                board_stack,
                ft.Container(height=10),
                difficulty_buttons_row,
                ft.Container(height=5),
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

    def _refresh_difficulty_buttons(self):
        """Update difficulty button styles"""
        for level, btn in self.difficulty_buttons.items():
            btn.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=ft.Colors.BLUE_100 if level == self.difficulty else None,
            )
        self.page.update()

    def on_move(self, move: chess.Move):
        """Called after a move is made (human or AI)"""
        self._update_ui()

        # Re-enable board interaction
        self.board_ui.set_interactive(True)

        board = self.game.board
        if board.is_game_over():
            self._show_game_over_dialog()
            return

        # Trigger AI if it's Black's turn
        if (
            not self.game.board.is_game_over()
            and self.game.board.turn == chess.BLACK
        ):
            self._trigger_ai_move()

    def _trigger_ai_move(self):
        """Trigger AI move in background thread"""
        if self.is_ai_thinking:
            return

        self.is_ai_thinking = True
        self.spinner_container.visible = True
        self.board_ui.set_interactive(False)
        self.page.update()  # Repaint FIRST before thread starts

        threading.Thread(target=self._ai_worker, daemon=True).start()

    def _ai_worker(self):
        """AI worker thread - computes the best move"""
        try:
            move = self.ai.choose_move(self.game.board)
            self._pending_ai_move = move
        except Exception as e:
            print("AI error:", e)
            self._pending_ai_move = None

        self.is_ai_thinking = False

        # Schedule the UI update on the main thread
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(self._check_ai_move)
        except RuntimeError:
            # Fallback
            self.page.update()
            self._check_ai_move()

    def _check_ai_move(self):
        """Execute the AI move on the main thread"""
        if self._pending_ai_move:
            move = self._pending_ai_move
            self._pending_ai_move = None

            self.board_ui.play_move(move)
            self.board_ui.set_interactive(True)

        # Hide spinner after AI move completes
        self.spinner_container.visible = False
        self.page.update()

    def _update_ui(self):
        """Update all UI elements"""
        board = self.game.board

        if board.is_checkmate():
            winner = "Black" if board.turn == chess.WHITE else "White"
            self.move_count_text.value = f"Checkmate! {winner} wins!"
            self.spinner_container.visible = False
        elif board.is_stalemate():
            self.move_count_text.value = "Stalemate! It's a draw!"
            self.spinner_container.visible = False
        elif board.is_insufficient_material():
            self.move_count_text.value = "Draw! Insufficient material."
            self.spinner_container.visible = False
        elif board.can_claim_threefold_repetition():
            self.move_count_text.value = "Draw! Threefold repetition."
            self.spinner_container.visible = False
        elif board.can_claim_fifty_moves():
            self.move_count_text.value = "Draw! 50-move rule."
            self.spinner_container.visible = False
        else:
            half_moves = len(board.move_stack)
            full_moves = half_moves // 2 + 1
            self.move_count_text.value = f"Move {full_moves}"

        if self.history:
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

            if winner == "White":
                color = ft.Colors.BLUE_700
                message = "You win! 🎉"
            else:
                color = ft.Colors.RED_700
                message = "AI wins! Better luck next time."

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
                    content=ft.Text("New Game"),
                    on_click=lambda e: self._close_dialog_and_new_game(),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor=ft.Colors.BLUE_100,
                    ),
                ),
                ft.Button(
                    content=ft.Text("Close"),
                    on_click=lambda e: self._close_dialog(),
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

    def _new_game(self):
        """Reset the game"""
        self.game.reset()
        self.board_ui.reset()

        self.ai = CustomChessAI(self.difficulty)

        self._pending_ai_move = None
        self.is_ai_thinking = False

        if self.history:
            self.history.clear()

        self.board_ui.set_interactive(True)
        self.spinner_container.visible = False
        self._refresh_difficulty_buttons()
        self._update_ui()

    def _change_difficulty(self, level: int):
        """Change AI difficulty"""
        self.difficulty = level
        self.ai = CustomChessAI(level)

        difficulty_names = {1: "Easy", 2: "Normal", 3: "Hard", 4: "Expert"}
        self.difficulty_text.value = f"AI: {difficulty_names[level]}"
        self.difficulty_text.update()

        self._refresh_difficulty_buttons()
        self._new_game()

    def _go_home(self):
        """Navigate back to home"""
        from pages.home_page import HomePage
        HomePage(self.page).show()