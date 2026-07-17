"""
VIChess - Reusable UI Widgets
"""

import flet as ft


class GameControls:
    """Game control buttons"""

    def __init__(
        self,
        on_new_game=None,
        show_difficulty=False,
        on_difficulty_change=None,
    ):
        self.on_new_game = on_new_game
        self.show_difficulty = show_difficulty
        self.on_difficulty_change = on_difficulty_change
        self.difficulty_btns = []

    def create(self) -> ft.Row:
        """Create the controls row"""
        controls = []

        # New Game button
        new_btn = ft.Button(
            content=ft.Row(
                [
                    ft.Image(
                        src="pieces/wk.svg",
                        width=20,
                        height=20,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    ft.Text("New Game"),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=lambda e: self.on_new_game() if self.on_new_game else None,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=ft.Colors.BLUE_100,
            ),
        )
        controls.append(new_btn)

        # Difficulty buttons (for bot mode)
        if self.show_difficulty:
            difficulties = [
                ("Easy", "pieces/wp.svg", 1),
                ("Medium", "pieces/wn.svg", 2),
                ("Hard", "pieces/wq.svg", 3),
            ]
            for label, icon, level in difficulties:
                btn = ft.Button(
                    content=ft.Row(
                        [
                            ft.Image(
                                src=icon,
                                width=18,
                                height=18,
                                fit=ft.BoxFit.CONTAIN,
                            ),
                            ft.Text(label),
                        ],
                        spacing=6,
                        tight=True,
                    ),
                    on_click=lambda e, l=level: self._change_difficulty(l),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding(10, 5, 10, 5),
                    ),
                )

                controls.append(btn)
                self.difficulty_btns.append((btn, level))

        return ft.Row(
            controls,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            wrap=True,
        )

    def _change_difficulty(self, level: int):
        """Handle difficulty change"""
        if self.on_difficulty_change:
            self.on_difficulty_change(level)

        # Highlight selected difficulty
        for btn, lvl in self.difficulty_btns:
            if lvl == level:
                btn.style.bgcolor = ft.Colors.BLUE_200
            else:
                btn.style.bgcolor = None
            btn.update()


class MoveHistory:
    """Move history display"""

    def __init__(self, max_moves: int = 10):
        self.max_moves = max_moves
        self.text_widget = None
        self.container = None

    def create(self) -> ft.Container:
        """Create the history display"""
        self.text_widget = ft.Text(
            "No moves yet",
            size=12,
            color=ft.Colors.GREY_700,
            text_align=ft.TextAlign.CENTER,
        )

        self.container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("📜 Move History", size=14, weight=ft.FontWeight.BOLD),
                    self.text_widget,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=10,
            bgcolor=ft.Colors.GREY_100,
            border_radius=10,
            width=400,
            height=120,
            alignment=ft.Alignment.CENTER,  # FIXED: Use ft.Alignment.CENTER
        )

        return self.container

    def update(self, move_stack: list):
        """Update with new moves"""
        if not move_stack:
            self.text_widget.value = "No moves yet"
            self.text_widget.update()
            return

        # Format moves as PGN
        formatted = []
        for i, move in enumerate(move_stack):
            if i % 2 == 0:
                move_num = i // 2 + 1
                formatted.append(f"{move_num}. {move}")
            else:
                formatted[-1] += f" {move}"

        # Show last N moves
        display = formatted[-self.max_moves:] if formatted else ["No moves yet"]
        self.text_widget.value = "\n".join(display)
        self.text_widget.update()

    def clear(self):
        """Clear history"""
        self.text_widget.value = "No moves yet"
        self.text_widget.update()