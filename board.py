"""Tic-tac-toe board state and rules.

Cells are indexed 1-9, left-to-right, top-to-bottom:

    1 | 2 | 3
   ---+---+---
    4 | 5 | 6
   ---+---+---
    7 | 8 | 9
"""

from __future__ import annotations

EMPTY = " "
WIN_LINES = (
    (1, 2, 3), (4, 5, 6), (7, 8, 9),  # rows
    (1, 4, 7), (2, 5, 8), (3, 6, 9),  # cols
    (1, 5, 9), (3, 5, 7),             # diagonals
)


class Board:
    def __init__(self) -> None:
        self.cells: dict[int, str] = {i: EMPTY for i in range(1, 10)}

    def place(self, pos: int, mark: str) -> None:
        if pos not in self.cells:
            raise ValueError(f"position {pos} out of range (1-9)")
        if self.cells[pos] != EMPTY:
            raise ValueError(f"position {pos} already taken by '{self.cells[pos]}'")
        if mark not in ("X", "O"):
            raise ValueError(f"mark must be 'X' or 'O', got {mark!r}")
        self.cells[pos] = mark

    def available(self) -> list[int]:
        return [i for i, c in self.cells.items() if c == EMPTY]

    def is_full(self) -> bool:
        return not self.available()

    def winner(self) -> str | None:
        for a, b, c in WIN_LINES:
            if self.cells[a] != EMPTY and self.cells[a] == self.cells[b] == self.cells[c]:
                return self.cells[a]
        return None

    def winning_line(self) -> tuple[int, int, int] | None:
        for line in WIN_LINES:
            a, b, c = line
            if self.cells[a] != EMPTY and self.cells[a] == self.cells[b] == self.cells[c]:
                return line
        return None

    def is_over(self) -> bool:
        return self.winner() is not None or self.is_full()
