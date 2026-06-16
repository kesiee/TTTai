"""ASCII rendering for the tic-tac-toe board."""

from __future__ import annotations

from board import EMPTY, Board


def render(board: Board, highlight: tuple[int, ...] = ()) -> str:
    """Return the board as a string. Empty cells show their 1-9 label so
    the player knows which numbers are still available."""

    def cell(i: int) -> str:
        v = board.cells[i]
        shown = str(i) if v == EMPTY else v
        if i in highlight:
            return f"*{shown}*"
        return f" {shown} "

    rows = []
    for r in range(3):
        a, b, c = 3 * r + 1, 3 * r + 2, 3 * r + 3
        rows.append(cell(a) + "|" + cell(b) + "|" + cell(c))
    sep = "---+---+---"
    return f"\n{sep}\n".join(rows)


def banner() -> str:
    return r"""
  _____ _____ _____      _    ___
 |_   _|_   _|_   _|    / \  |_ _|
   | |   | |   | |     / _ \  | |
   | |   | |   | |    / ___ \ | |
   |_|   |_|   |_|   /_/   \_\___|

      tic-tac-toe vs. an LLM agent
"""
