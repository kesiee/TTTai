# TTTai — tic-tac-toe vs. an LLM

A tiny terminal tic-tac-toe where your opponent is an LLM agent. You pick the
provider, paste an API key, and play. Powered by
[llmgate](https://pypi.org/project/llmgt/), so swapping providers (Anthropic,
OpenAI, Groq, Gemini, …) is one prompt away.

```
 X | 2 | O
---+---+---
 4 | X | 6
---+---+---
 7 | 8 | O
```

## Setup

Using conda:

```bash
conda env create -f environment.yml
conda activate tttai
```

Or just pip:

```bash
pip install llmgt pyyaml
```

## Play

```bash
python play.py
```

On first run you'll be asked to:

1. Pick a provider (Anthropic / OpenAI / Groq / Gemini / custom)
2. Paste an API key (kept only in your shell env + a local `llmgate.yaml`,
   which is gitignored)
3. Choose to play as X or O

Enter a digit `1`–`9` to place your mark. The AI will think, drop its move, and
explain why.

## Layout

```
play.py            entry point
board.py           board state + win detection
display.py         ASCII rendering
agent.py           LLM move picker (uses llmgate)
game.py            game loop, setup prompts
llmgate.yaml       generated on first run, gitignored
environment.yml    conda env spec
```

## Reset / swap provider

Delete `llmgate.yaml` and run again, or edit it directly — see
`llmgate.yaml.example` for the format.

## License

MIT.
