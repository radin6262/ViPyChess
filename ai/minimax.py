"""
Minimax search with alpha-beta pruning, quiescence, and advanced search features
"""

import time
import random
import chess
from ai.evaluation import evaluate_board
from ai.openings import get_opening_move
from ai.see import see
from ai.utils import get_piece_value
from ai.transposition import TranspositionTable


class MinimaxSearch:
    """Minimax search with alpha-beta pruning and search enhancements"""

    def __init__(self, depth: int = 3):
        self.depth = depth
        self.nodes_searched = 0
        self.time_limit = 5.0
        self.max_quiescence_depth = 4

        # Search enhancements
        self.killer_moves = {}
        self.history_heuristic = {}
        self.pv_move = None
        self.best_move = None

        # randomness code
        self.randomness_margin = {
            1: 100,  # Easy
            2: 50,  # Normal
            3: 20,  # Hard
            4: 5,  # Expert
        }.get(depth, 20)

        self.max_random_candidates = 3

        # Transposition table / 200k
        self.tt = TranspositionTable(max_entries=200000)

        # Null-move pruning
        self.null_move_enabled = True
        self.null_move_reduction = 2

        # LMR
        self.lmr_enabled = True
        self.lmr_min_depth = 3
        self.lmr_reduction = 1

    def search(self, board: chess.Board) -> chess.Move | None:
        root_move_scores = {}
        """Find the best move using iterative deepening"""
        if board.is_game_over():
            return None

        opening = get_opening_move(board)
        if opening is not None:
            return opening

        self.nodes_searched = 0
        start_time = time.time()

        # Clear killer moves for new search
        self.killer_moves.clear()

        # Increment TT age at the start of each search
        self.tt.increment_age()

        moves = list(board.legal_moves)
        if not moves:
            return None

        if len(moves) == 1:
            return moves[0]

        # Iterative deepening
        self.best_move = moves[0]
        best_score = -float('inf') if board.turn == chess.WHITE else float('inf')

        for current_depth in range(1, self.depth + 1):
            alpha = -float('inf')
            beta = float('inf')

            # Use aspiration window for deeper searches
            if current_depth >= 3:
                window = 50
                alpha = best_score - window
                beta = best_score + window
            else:
                alpha = -float('inf')
                beta = float('inf')

            # Order moves using MVV-LVA + Killer + History
            moves = self._order_moves(board, moves)

            for move in moves:
                board_copy = board.copy()
                board_copy.push(move)

                if board_copy.is_checkmate():
                    self.best_move = move
                    return move

                score = self._quiescence_search(
                    board_copy,
                    current_depth - 1,
                    alpha,
                    beta,
                    board_copy.turn == chess.WHITE,
                    start_time,
                    0
                )
                if current_depth == self.depth:
                    root_move_scores[move] = score

                if board.turn == chess.WHITE:
                    if score > best_score:
                        best_score = score
                        self.best_move = move
                    alpha = max(alpha, best_score)
                else:
                    if score < best_score:
                        best_score = score
                        self.best_move = move
                    beta = min(beta, best_score)

                if alpha >= beta:
                    break

            # Update history heuristic with best move
            if self.best_move:
                move_key = (self.best_move.from_square, self.best_move.to_square)
                self.history_heuristic[move_key] = self.history_heuristic.get(move_key, 0) + current_depth * current_depth

            # Store in transposition table
            flag = TranspositionTable.FLAG_EXACT
            self.tt.store(board, current_depth, best_score, flag, self.best_move)

        # ---------------------------------------------------------
        # Controlled randomness
        # ---------------------------------------------------------
        # Only consider moves that are close to the best move.
        # This prevents the AI from making obvious bad moves,
        # while allowing different games to play differently.
        if root_move_scores:
            if board.turn == chess.WHITE:
                best_score = max(root_move_scores.values())

                candidates = [
                    move
                    for move, score in root_move_scores.items()
                    if score >= best_score - self.randomness_margin
                ]
            else:
                best_score = min(root_move_scores.values())

                candidates = [
                    move
                    for move, score in root_move_scores.items()
                    if score <= best_score + self.randomness_margin
                ]

            # Sort candidates by strength
            candidates.sort(
                key=lambda move: root_move_scores[move],
                reverse=(board.turn == chess.WHITE),
            )

            # Only allow the best few moves
            candidates = candidates[:self.max_random_candidates]

            # Randomly select between similarly strong moves
            if len(candidates) > 1:
                self.best_move = random.choice(candidates)

        return self.best_move

    def _quiescence_search(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool,
        start_time: float,
        quiescence_depth: int,
    ) -> float:
        """Quiescence search with transposition table lookup"""
        self.nodes_searched += 1

        # Time limit check
        if time.time() - start_time > self.time_limit:
            return evaluate_board(board)

        # Check transposition table
        tt_entry = self.tt.get(board)
        if tt_entry and tt_entry['depth'] >= depth:
            if tt_entry['flag'] == TranspositionTable.FLAG_EXACT:
                return tt_entry['score']
            elif tt_entry['flag'] == TranspositionTable.FLAG_LOWERBOUND:
                if tt_entry['score'] >= beta:
                    return beta
            elif tt_entry['flag'] == TranspositionTable.FLAG_UPPERBOUND:
                if tt_entry['score'] <= alpha:
                    return alpha

        # Terminal position
        if board.is_game_over():
            return evaluate_board(board)

        # Stand-pat evaluation
        stand_pat = evaluate_board(board)

        # Alpha-beta pruning with stand-pat
        if is_maximizing:
            if stand_pat >= beta:
                return beta
            if depth <= 0 and quiescence_depth >= self.max_quiescence_depth:
                return stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if depth <= 0 and quiescence_depth >= self.max_quiescence_depth:
                return stand_pat

        # Null-move pruning
        if self.null_move_enabled and depth >= 2 and not board.is_check():
            # Null move: skip this turn
            board_copy = board.copy()
            board_copy.turn = not board_copy.turn
            null_score = -self._quiescence_search(
                board_copy,
                depth - self.null_move_reduction - 1,
                -beta,
                -beta + 1,
                not is_maximizing,
                start_time,
                0
            )
            if null_score >= beta:
                return beta

        # Generate moves
        moves = []
        for move in board.legal_moves:
            if board.is_capture(move) or move.promotion:
                moves.append(move)
            elif board.gives_check(move):
                moves.append(move)
            elif depth > 0:
                moves.append(move)

        if not moves:
            return stand_pat

        # Order moves for better pruning
        moves = self._order_moves_quiescence(board, moves)

        if is_maximizing:
            value = stand_pat
            move_count = 0
            for move in moves:
                board.push(move)

                # LMR (Late Move Reduction)
                reduction = 0
                if (self.lmr_enabled and depth >= self.lmr_min_depth and
                    move_count >= 3 and not board.is_capture(move)):
                    reduction = self.lmr_reduction
                    if board.is_check():
                        reduction = 0

                score = self._quiescence_search(
                    board,
                    depth - 1 - reduction,
                    alpha,
                    beta,
                    False,
                    start_time,
                    quiescence_depth + 1,
                )
                board.pop()

                value = max(value, score)
                alpha = max(alpha, value)

                # Update killer moves
                if score > 0 and depth > 0:
                    self.killer_moves[(depth, board.turn)] = move

                if alpha >= beta:
                    break
                move_count += 1

            # Store in transposition table
            flag = TranspositionTable.FLAG_EXACT
            if value >= beta:
                flag = TranspositionTable.FLAG_LOWERBOUND
            elif value <= alpha:
                flag = TranspositionTable.FLAG_UPPERBOUND
            self.tt.store(board, depth, value, flag)

            return value
        else:
            value = stand_pat
            move_count = 0
            for move in moves:
                board.push(move)

                reduction = 0
                if (self.lmr_enabled and depth >= self.lmr_min_depth and
                    move_count >= 3 and not board.is_capture(move)):
                    reduction = self.lmr_reduction
                    if board.is_check():
                        reduction = 0

                score = self._quiescence_search(
                    board,
                    depth - 1 - reduction,
                    alpha,
                    beta,
                    True,
                    start_time,
                    quiescence_depth + 1,
                )
                board.pop()

                value = min(value, score)
                beta = min(beta, value)

                if score < 0 and depth > 0:
                    self.killer_moves[(depth, board.turn)] = move

                if alpha >= beta:
                    break
                move_count += 1

            flag = TranspositionTable.FLAG_EXACT
            if value >= beta:
                flag = TranspositionTable.FLAG_LOWERBOUND
            elif value <= alpha:
                flag = TranspositionTable.FLAG_UPPERBOUND
            self.tt.store(board, depth, value, flag)

            return value

    def _order_moves(self, board: chess.Board, moves: list) -> list:
        """Order moves using MVV-LVA, SEE, Killer, and History heuristics"""
        def move_score(move):
            score = 0

            # 1. MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                if victim:
                    victim_value = get_piece_value(victim.piece_type)
                    attacker = board.piece_at(move.from_square)
                    attacker_value = get_piece_value(attacker.piece_type) if attacker else 0
                    score += 1000 + victim_value * 10 - attacker_value

                see_score = see(board, move)
                if see_score > 0:
                    score += see_score
                else:
                    score -= abs(see_score) // 2

            # 2. Promotion moves
            if move.promotion:
                score += 800

            # 3. Moves that give check
            board_copy = board.copy()
            board_copy.push(move)
            if board_copy.is_check():
                score += 400

            # 4. Killer moves
            if (1, board.turn) in self.killer_moves and self.killer_moves[(1, board.turn)] == move:
                score += 300
            if (2, board.turn) in self.killer_moves and self.killer_moves[(2, board.turn)] == move:
                score += 200

            # 5. History heuristic
            move_key = (move.from_square, move.to_square)
            score += self.history_heuristic.get(move_key, 0) // 10

            # 6. Center control
            center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
            if move.to_square in center_squares:
                score += 50

            return score

        return sorted(moves, key=move_score, reverse=True)

    def _order_moves_quiescence(self, board: chess.Board, moves: list) -> list:
        """Order moves for quiescence search using SEE"""
        def move_score(move):
            score = 0

            if board.is_capture(move):
                see_score = see(board, move)
                score += see_score * 2

            if move.promotion:
                score += 800

            board_copy = board.copy()
            board_copy.push(move)
            if board_copy.is_check():
                score += 300

            return score

        return sorted(moves, key=move_score, reverse=True)