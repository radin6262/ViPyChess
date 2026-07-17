import flet as ft
from pages.local_match import LocalMatchPage
from pages.bot_match import BotMatchPage


class HomePage:
    def __init__(self, page: ft.Page):
        self.page = page

    def _mode_card(
        self,
        icon,
        title,
        subtitle,
        color,
        border,
        callback,
    ):
        return ft.Container(
            width=320,
            padding=16,
            border_radius=16,
            bgcolor=color,
            border=ft.border.Border(
                left=ft.border.BorderSide(2, border),
                right=ft.border.BorderSide(2, border),
                top=ft.border.BorderSide(2, border),
                bottom=ft.border.BorderSide(2, border),
            ),
            on_click=lambda e: callback(),
            content=ft.Row(
                [
                    ft.Image(
                        src=icon,
                        width=48,
                        height=48,
                    ),

                    ft.Column(
                        [
                            ft.Text(
                                title,
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                subtitle,
                                size=13,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def show(self):
        self.page.controls.clear()

        self.page.add(
            ft.Column(
                [
                    ft.Container(height=25),

                    ft.Image(
                        src="pieces/wk.svg",
                        width=96,
                        height=96,
                    ),

                    ft.Text(
                        "VIChess",
                        size=34,
                        weight=ft.FontWeight.BOLD,
                    ),

                    ft.Text(
                        "Modern Chess Client",
                        color=ft.Colors.GREY_600,
                    ),

                    ft.Container(height=25),

                    self._mode_card(
                        "pieces/wp.svg",
                        "Local Match",
                        "Pass and play on one device",
                        ft.Colors.BLUE_50,
                        ft.Colors.BLUE_200,
                        self._go_to_local,
                    ),

                    ft.Container(height=12),

                    self._mode_card(
                        "pieces/bq.svg",
                        "Play vs Computer",
                        "Powered by ViChess Ai",
                        ft.Colors.GREEN_50,
                        ft.Colors.GREEN_200,
                        self._go_to_bot,
                    ),

                    ft.Container(height=35),

                    ft.Text(
                        "UI Version 1.2 • ViRender 1.0",
                        size=12,
                        color=ft.Colors.GREY_500,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

        self.page.update()

    def _go_to_local(self):
        LocalMatchPage(self.page).show()

    def _go_to_bot(self):
        BotMatchPage(self.page).show()