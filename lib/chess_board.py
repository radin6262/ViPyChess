"""
VIChess - Chess Board UI
Compatible with Flet 0.86.x
"""

import flet as ft
import chess
import os
import sys

class ChessBoardUI:

    PIECE_IMAGES = {
        "P": "pieces/wp.svg",
        "R": "pieces/wr.svg",
        "N": "pieces/wn.svg",
        "B": "pieces/wb.svg",
        "Q": "pieces/wq.svg",
        "K": "pieces/wk.svg",

        "p": "pieces/bp.svg",
        "r": "pieces/br.svg",
        "n": "pieces/bn.svg",
        "b": "pieces/bb.svg",
        "q": "pieces/bq.svg",
        "k": "pieces/bk.svg",
    }

    def __init__(self, page: ft.Page, game_logic, on_move=None):
        self.page = page
        self.game = game_logic
        self.on_move = on_move

        self.selected_square = None

        self.images = {}
        self.squares = {}

        self.board_container = None

        self.light_color = ft.Colors.WHITE
        self.dark_color = ft.Colors.BROWN_600
        self.selected_color = ft.Colors.YELLOW_400

    def create(self):

        # Determine board size from available page width
        available_width = self.page.width or 360

        # Leave some margin on the sides
        board_size = min(available_width - 24, 480)

        # Make sure it's divisible by 8
        square_size = board_size // 8
        board_size = square_size * 8

        piece_size = int(square_size * 0.72)

        self.squares.clear()
        self.images.clear()

        rows = []

        for rank in range(7, -1, -1):

            controls = []

            for file in range(8):
                square = chess.square(file, rank)

                image = ft.Image(
                    src="",
                    width=int(square_size * 0.82),
                    height=int(square_size * 0.82),
                    fit=ft.BoxFit.CONTAIN,
                )

                is_light = (rank + file) % 2 == 1

                container = ft.Container(
                    width=square_size,
                    height=square_size,
                    bgcolor=self.light_color if is_light else self.dark_color,
                    content=image,
                    data=square,
                    on_click=self._on_square_click,
                )

                self.images[square] = image
                self.squares[square] = container

                controls.append(container)

            rows.append(
                ft.Row(
                    controls,
                    spacing=0,
                    tight=True,
                )
            )

        self.board_container = ft.Container(
            width=board_size + 8,
            height=board_size + 8,
            padding=4,
            bgcolor=ft.Colors.BROWN_400,
            border_radius=8,
            content=ft.Column(
                rows,
                spacing=0,
                tight=True,
            ),
        )

        self._update_pieces_no_update()

        return self.board_container

    def _on_square_click(self, e):

        if self.game.is_game_over():
            return

        target = e.control.data
        piece = self.game.get_piece_at(target)

        if self.selected_square is None:

            if piece and piece.color == self.game.board.turn:
                self.selected_square = target
                self._update_pieces()

            return

        if piece and piece.color == self.game.board.turn:
            self.selected_square = target
            self._update_pieces()
            return

        move = chess.Move(self.selected_square, target)

        moving = self.game.get_piece_at(self.selected_square)

        if (
            moving
            and moving.piece_type == chess.PAWN
            and chess.square_rank(target) in (0, 7)
        ):
            move = chess.Move(
                self.selected_square,
                target,
                promotion=chess.QUEEN,
            )

        if move in self.game.board.legal_moves:
            self.game.board.push(move)

            self.selected_square = None
            self._update_pieces()

            if self.on_move:
                self.on_move(move)

        else:
            self.selected_square = None
            self._update_pieces()

    def _update_pieces_no_update(self):

        for square, image in self.images.items():

            piece = self.game.get_piece_at(square)

            if piece:
                self.squares[square].content = ft.Image(
                    src=self.PIECE_IMAGES[piece.symbol()],
                    fit=ft.BoxFit.CONTAIN,
                )
            else:
                self.squares[square].content = None

            rank = chess.square_rank(square)
            file = chess.square_file(square)

            if square == self.selected_square:
                self.squares[square].bgcolor = self.selected_color
            else:
                self.squares[square].bgcolor = (
                    self.light_color
                    if (rank + file) % 2 == 1
                    else self.dark_color
                )

    def _update_pieces(self):
        self._update_pieces_no_update()

        if self.board_container.page:
            self.board_container.update()

    def update(self):
        self._update_pieces()

    def reset(self):
        self.selected_square = None
        self._update_pieces()