import flet as ft
from pages.home_page import HomePage


def main(page: ft.Page):
    page.title = "♚ VIChess ♔"
    page.theme_mode = ft.ThemeMode.LIGHT

    page.padding = 8
    page.spacing = 0

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Desktop testing
    page.window.width = 400
    page.window.height = 800
    page.window.resizable = False

    page.update()

    HomePage(page).show()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")