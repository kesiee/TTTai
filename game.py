"""Main game loop: ASCII board, human input, LLM opponent."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml
from llmgate import LLMGate
from llmgate.exceptions import LLMGateError

from agent import LLMAgent
from board import Board
from display import banner, render


CONFIG_PATH = Path("llmgate.yaml")

PROVIDER_PRESETS = {
    "1": ("anthropic", "claude-sonnet-4-5", "ANTHROPIC_API_KEY"),
    "2": ("openai", "gpt-4o-mini", "OPENAI_API_KEY"),
    "3": ("groq", "llama-3.1-8b-instant", "GROQ_API_KEY"),
    "4": ("gemini", "gemini-2.0-flash", "GEMINI_API_KEY"),
}


def _prompt(msg: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        try:
            answer = input(f"{msg}{suffix}: ").strip()
        except EOFError:
            print()
            sys.exit(0)
        if answer:
            return answer
        if default is not None:
            return default


def setup_gate() -> LLMGate:
    """Pick a provider, collect an API key, write llmgate.yaml, return a Gate."""
    if CONFIG_PATH.exists():
        reuse = _prompt(
            f"Found existing {CONFIG_PATH}. Reuse it? (y/n)", default="y"
        ).lower()
        if reuse.startswith("y"):
            return LLMGate(str(CONFIG_PATH))

    print("\nPick a provider:")
    for key, (prov, model, _env) in PROVIDER_PRESETS.items():
        print(f"  {key}) {prov:<10} — {model}")
    print("  5) custom (enter your own provider + model)")
    choice = _prompt("Choice", default="1")

    if choice in PROVIDER_PRESETS:
        provider, model, env_var = PROVIDER_PRESETS[choice]
    else:
        provider = _prompt("Provider")
        model = _prompt("Model")
        env_var = f"{provider.upper()}_API_KEY"

    existing = os.environ.get(env_var)
    if existing:
        use = _prompt(f"Found {env_var} in env. Use it? (y/n)", default="y").lower()
        if not use.startswith("y"):
            existing = None
    if not existing:
        api_key = _prompt(f"Paste {env_var}")
        os.environ[env_var] = api_key

    config = {
        "provider": provider,
        "model": model,
        "api_key": f"${{{env_var}}}",
        "temperature": 0.2,
        "max_tokens": 200,
    }
    CONFIG_PATH.write_text(yaml.safe_dump(config, sort_keys=False))
    print(f"Wrote {CONFIG_PATH} (gitignored).\n")
    return LLMGate(str(CONFIG_PATH))


def pick_human_mark() -> str:
    while True:
        choice = _prompt("Play as X or O? (X goes first)", default="X").upper()
        if choice in ("X", "O"):
            return choice
        print("Please type X or O.")


def get_human_move(board: Board, mark: str) -> int:
    available = board.available()
    while True:
        try:
            raw = input(f"Your move ({mark}), pick {available}: ").strip()
        except EOFError:
            print()
            sys.exit(0)
        if not raw.isdigit():
            print("  Enter a single digit 1-9.")
            continue
        n = int(raw)
        if n not in available:
            print(f"  {n} isn't available. Available: {available}")
            continue
        return n


def play() -> None:
    print(banner())
    gate = setup_gate()
    human = pick_human_mark()
    ai_mark = "O" if human == "X" else "X"
    agent = LLMAgent(gate, ai_mark)

    print(f"\nYou are '{human}'. The AI is '{ai_mark}'. X moves first.\n")

    board = Board()
    turn = "X"

    while True:
        print(render(board))
        print()
        winner = board.winner()
        if winner:
            line = board.winning_line() or ()
            print(render(board, highlight=line))
            print(f"\n>> '{winner}' wins! <<")
            print("You won!" if winner == human else "The AI got you. gg.")
            return
        if board.is_full():
            print("\n>> Draw. <<")
            return

        if turn == human:
            move = get_human_move(board, human)
            board.place(move, human)
        else:
            print(f"AI ({ai_mark}) thinking...")
            try:
                move, reason = agent.choose_move(board)
            except LLMGateError as err:
                print(f"\n!! LLM call failed ({type(err).__name__}).")
                print(f"   {str(err)[:300]}{'...' if len(str(err)) > 300 else ''}\n")
                print("Edit llmgate.yaml (try a different model — e.g. "
                      "gemini-2.5-flash or gemini-1.5-flash) and rerun.")
                return
            board.place(move, ai_mark)
            print(f"AI plays {move}. ({reason})\n")

        turn = "O" if turn == "X" else "X"


def main() -> None:
    try:
        play()
    except KeyboardInterrupt:
        print("\nbye.")
    except LLMGateError as err:
        print(f"\n!! LLM setup failed ({type(err).__name__}): {err}")
