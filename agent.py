"""LLM-driven tic-tac-toe agent.

Talks to any provider through llmgate. Asks for a JSON move, validates it,
retries once if the model returns garbage or picks an occupied cell.
"""

from __future__ import annotations

import json
import random
import re

from llmgate import LLMGate

from board import Board

SYSTEM_PROMPT = """You are a tic-tac-toe player. The board has 9 cells, numbered 1-9:

 1 | 2 | 3
---+---+---
 4 | 5 | 6
---+---+---
 7 | 8 | 9

You play to win. If you cannot win, you play to block your opponent. Otherwise
pick a strategic square (corners and the center are strong).

Respond with ONLY a JSON object on a single line, in this exact format:
{"move": <int 1-9>, "reason": "<short explanation>"}
Do not add markdown fences or any text outside the JSON."""


def _user_prompt(board: Board, you: str, opponent: str) -> str:
    rendered_rows = []
    for r in range(3):
        cells = []
        for c in range(3):
            i = 3 * r + c + 1
            v = board.cells[i]
            cells.append(str(i) if v == " " else v)
        rendered_rows.append(" " + " | ".join(cells))
    rendered = "\n---+---+---\n".join(rendered_rows)
    available = board.available()
    return (
        f"You are playing as '{you}'. Your opponent is '{opponent}'.\n\n"
        f"Current board:\n{rendered}\n\n"
        f"Empty cells (valid moves): {available}\n\n"
        "Pick the best empty cell. Reply with the JSON object only."
    )


_JSON_RE = re.compile(r"\{[^{}]*\}", re.DOTALL)


def _extract_move(text: str, available: list[int]) -> tuple[int, str] | None:
    match = _JSON_RE.search(text)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    move = data.get("move")
    reason = str(data.get("reason", "")).strip()
    if isinstance(move, str) and move.isdigit():
        move = int(move)
    if not isinstance(move, int) or move not in available:
        return None
    return move, reason


class LLMAgent:
    def __init__(self, gate: LLMGate, mark: str) -> None:
        self.gate = gate
        self.mark = mark
        self.opponent = "O" if mark == "X" else "X"

    def choose_move(self, board: Board) -> tuple[int, str]:
        available = board.available()
        if not available:
            raise RuntimeError("agent asked to move on a full board")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _user_prompt(board, self.mark, self.opponent)},
        ]

        last_text = ""
        for attempt in range(2):
            response = self.gate.chat_messages(messages)
            last_text = response.text or ""
            parsed = _extract_move(last_text, available)
            if parsed is not None:
                return parsed
            messages.append({"role": "assistant", "content": last_text})
            messages.append({
                "role": "user",
                "content": (
                    f"That reply was invalid. Valid moves are {available}. "
                    "Reply with ONLY the JSON object: "
                    '{"move": <int>, "reason": "<short>"}'
                ),
            })

        fallback = random.choice(available)
        return fallback, f"(fallback — model output unparseable: {last_text[:80]!r})"
