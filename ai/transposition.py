"""
Transposition Table using python-chess built-in transposition key
"""

import chess


class TranspositionTable:
    """
    Transposition table using python-chess's built-in transposition key.
    Uses depth-preferred replacement strategy.
    """

    FLAG_EXACT = 0
    FLAG_LOWERBOUND = 1
    FLAG_UPPERBOUND = 2

    def __init__(self, max_entries: int = 200000):
        """
        Initialize transposition table

        Args:
            max_entries: Maximum number of entries to store
                        200k entries ≈ ~40MB in Python
        """
        self.max_entries = max_entries
        self.table = {}
        self.hits = 0
        self.misses = 0
        self.age = 0
        self.new_entries = 0
        self.overwritten = 0

    def _get_key(self, board: chess.Board) -> int:
        """Get the transposition key from the board"""
        # python-chess has built-in transposition key
        return board._transposition_key()

    def get(self, board: chess.Board) -> dict | None:
        """Get an entry from the table"""
        key = self._get_key(board)
        entry = self.table.get(key)

        if entry is None:
            self.misses += 1
            return None

        # Check age - if too old, consider it expired
        if entry.get('age', 0) < self.age - 100:
            self.misses += 1
            return None

        self.hits += 1
        return entry

    def store(self, board: chess.Board, depth: int, score: float, flag: int, move: chess.Move | None = None):
        """
        Store an entry in the table with depth-preferred replacement.
        Only replace if new entry is deeper or same depth.
        """
        key = self._get_key(board)

        # Check if entry exists
        existing = self.table.get(key)

        # Replace only if new depth is >= existing depth
        if existing is not None:
            if existing.get('depth', 0) > depth:
                # Existing entry is deeper - keep it
                self.overwritten += 1
                return

            # Replace with new entry
            self.overwritten += 1
        else:
            self.new_entries += 1

        # Store new entry
        self.table[key] = {
            'depth': depth,
            'score': score,
            'flag': flag,
            'move': move,
            'age': self.age,
        }

        # If table gets too large, remove oldest entries
        if len(self.table) > self.max_entries * 1.2:  # 20% over limit
            self._cleanup()

    def _cleanup(self):
        """Remove oldest entries when table is full"""
        # Get all entries sorted by age (oldest first)
        items = sorted(self.table.items(), key=lambda x: x[1].get('age', 0))

        # Remove oldest 25%
        remove_count = len(items) // 4
        for i in range(remove_count):
            del self.table[items[i][0]]

    def increment_age(self):
        """Increment the age counter for aging entries"""
        self.age += 1

    def clear(self):
        """Clear the table (only for new games)"""
        self.table.clear()
        self.hits = 0
        self.misses = 0
        self.age = 0
        self.new_entries = 0
        self.overwritten = 0

    def get_stats(self) -> dict:
        """Get table statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'size': len(self.table),
            'max_entries': self.max_entries,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'new_entries': self.new_entries,
            'overwritten': self.overwritten,
            'age': self.age,
        }