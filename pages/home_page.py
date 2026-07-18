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
            width=400,
            padding=22,
            border_radius=20,
            bgcolor=color,
            shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK),
                offset=ft.Offset(0, 6),
            ),
            border=ft.border.Border(
                left=ft.border.BorderSide(2, border),
                top=ft.border.BorderSide(2, border),
                right=ft.border.BorderSide(2, border),
                bottom=ft.border.BorderSide(2, border),
            ),
            animate=200,
            on_click=lambda e: callback(),
            content=ft.Row(
                [
                    ft.Image(
                        src=icon,
                        width=60,
                        height=60,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                title,
                                size=21,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                subtitle,
                                size=14,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        size=24,
                        color=border,
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
                    ft.Container(height=45),

                    ft.Image(
                        src="pieces/wk.svg",
                        width=120,
                        height=120,
                    ),

                    ft.Text(
                        "VIChess",
                        size=42,
                        weight=ft.FontWeight.BOLD,
                    ),

                    ft.Text(
                        "Modern Chess Client",
                        size=16,
                        color=ft.Colors.GREY_600,
                    ),

                    ft.Container(height=40),

                    self._mode_card(
                        "pieces/wp.svg",
                        "Local Match",
                        "Pass and play on one device",
                        ft.Colors.BLUE_50,
                        ft.Colors.BLUE_200,
                        self._go_to_local,
                    ),

                    ft.Container(height=18),

                    self._mode_card(
                        "pieces/bq.svg",
                        "Play vs Computer",
                        "Powered by VIChess AI",
                        ft.Colors.GREEN_50,
                        ft.Colors.GREEN_200,
                        self._go_to_bot,
                    ),

                    ft.Container(height=50),

                    ft.Text(
                        "VIUI 2.0 • VIRender 2.0",
                        size=13,
                        color=ft.Colors.GREY_500,
                    ),
                ],
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

        self.page.update()

    def _go_to_local(self):
        LocalMatchPage(self.page).show()

    def _go_to_bot(self):
        BotMatchPage(self.page).show()