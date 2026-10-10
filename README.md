# trailbrief 🥾

Personalized hiking briefings from a **local open-weight model** — built for
[DEV's Hacktoberfest Week 1 challenge](https://dev.to/challenges/hacktoberfest-week1-2026-10-05)
("Touch Grass": get people off the screen and into the world).

You describe a trail; trailbrief asks Gemma (via Ollama, running entirely on
your laptop) to write you a briefing: pacing plan, season-aware pack list,
watch-outs, Leave No Trace. No accounts, no API keys, no data leaving your
machine. And when you're already on the trail with zero signal, a built-in
template engine produces a genuinely useful briefing offline.

## Setup

```bash
# 1. Clone and enter
git clone <your-repo-url> trailbrief && cd trailbrief

# 2. (Optional) Install Ollama and pull Gemma for AI briefings
#    https://ollama.com  →  ollama pull gemma3

# 3. No Python dependencies — stdlib only
python3 -m trailbrief --help
```

## Usage

```bash
# AI briefing (needs Ollama running with gemma3)
python3 -m trailbrief \
  --name "Ricketts Glen Falls Trail" \
  --distance 7.2 --elevation 1200 \
  --location "Benton, PA" \
  --season fall \
  --experience intermediate

# Offline briefing (works with no model, no internet)
python3 -m trailbrief \
  --name "Ricketts Glen Falls Trail" \
  --distance 7.2 --elevation 1200 \
  --location "Benton, PA" \
  --season fall --offline

# Use a different model or remote Ollama host
python3 -m trailbrief --name "X" --distance 5 --elevation 800 \
  --location "Y" --season summer --model llama3.2 --host http://myserver:11434
```

## How it works

1. **Difficulty + pacing** are computed deterministically from distance and
   elevation (Naismith-style: 2 mph + 30 min per 1,000 ft).
2. Those numbers are baked into a **grounded prompt** — the model is told to
   use them and not invent trail features.
3. The prompt goes to `http://localhost:11434/api/generate` (Ollama).
   Default model: `gemma3`.
4. If the model is unreachable, the **offline template engine** takes over:
   season-aware pack lists, elevation-aware safety notes, experience-level
   tips. Still a real briefing, not an error message.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

12 tests: difficulty bands, prompt grounding, fallback content, and the Ollama
HTTP layer (mocked — no server needed).

## Sample output

See [sample_output.txt](sample_output.txt) for a real offline run.

## Why open?

- **Offline on the trail.** A cloud API can't brief you where there's no
  signal. A local open-weight model can.
- **Your data stays yours.** Trail plans and location stay on your laptop.
- **Free forever.** No per-token billing for a hobby tool.
- **Swappable.** Don't like Gemma's style? `--model llama3.2` and you're done —
  no code changes, no vendor lock-in.
