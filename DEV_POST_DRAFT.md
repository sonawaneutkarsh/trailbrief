# DEV Submission Draft — DO NOT PUBLISH FROM HERE
# Tags for the real post: devchallenge, hf26challenge
# (DEV's submission template auto-adds these when you start from the challenge page)

---

# I built a hiking guide that runs on a laptop with no internet — meet trailbrief 🥾

## What I built

**trailbrief** is a small Python CLI that writes you a personalized hiking
briefing. You tell it the trail — name, distance, elevation gain, location,
season, your experience level — and it hands back a practical plan: an
overview, a pacing plan, a season-aware pack list, watch-outs, and a Leave No
Trace reminder.

The twist: the briefing is written by **Gemma, running locally through
Ollama**. No accounts, no API keys, no data leaving your machine. And because
the whole point is getting *outside*, there's a proper offline fallback —
when no model is reachable (read: you're already on the trail with zero
bars), a built-in template engine still produces a genuinely useful briefing
instead of an error message.

Repo: [link your GitHub repo here before publishing]

## Demo

Here's a real run — offline mode, since I don't have a GPU farm in my dorm:

```
$ python3 -m trailbrief \
    --name "Ricketts Glen Falls Trail" \
    --distance 7.2 --elevation 1200 \
    --location "Benton, PA" \
    --season fall \
    --experience intermediate --offline

# Trail Briefing: Ricketts Glen Falls Trail
*Benton, PA · 7.2 mi · 1,200 ft gain · Fall · Moderate*

## Overview
A moderate day out: 7.2 miles and 1,200 ft of gain asks for steady pacing
and a real lunch stop. Expect about 4.2 hours of moving time, plus stops.

## Pacing plan
Start no later than 8 AM — with 4.2 hours of moving time plus breaks, you
want a buffer before dark. ...

## Pack list
- Insulating mid-layer — temps swing 20°F+ through the day
- Headlamp with fresh batteries (shorter days sneak up on you)
- Bright colors — it's hunting season in many areas
...

## Watch-outs
Daylight is the constraint: sunset comes early and temperatures drop fast
once the sun dips. Leaf-covered rocks are slippery.
```

With Ollama running (`ollama pull gemma3`, then drop the `--offline` flag),
the same inputs go to the model instead — with a twist I'll get to below.

## How it works

The architecture is deliberately boring, in the good way:

1. **Deterministic core.** Difficulty and moving time are computed from your
   numbers with a Naismith-style rule (2 mph + 30 min per 1,000 ft of gain).
   No vibes, just arithmetic.
2. **Grounded prompt.** Those computed numbers are baked into the prompt, and
   the model is explicitly told to use them and *not invent trail features,
   facilities, or water sources*. This is the part most "AI hiking apps"
   get wrong — a chatbot happily hallucinating a water fountain at mile 6
   is how people get hurt.
3. **Local inference.** The prompt goes to `localhost:11434` — Ollama, plain
   HTTP, stdlib only. Default model is `gemma3`.
4. **Honest fallback.** Model unreachable? The template engine takes over
   with season-aware packing (fall gets headlamp + hunter-orange reminders,
   winter gets microspikes), elevation-aware safety notes, and
   experience-level tips.

The full test suite (12 tests, `python -m unittest discover -s tests`) covers
the difficulty bands, prompt grounding, fallback content, and the Ollama HTTP
layer with mocks — no server needed to verify.

## Why open innovation matters for this build

This project only makes sense *because* the AI is open:

- **It works where the internet doesn't.** A cloud API can't brief you on a
  ridgeline with no signal. A 3–9B open-weight model on your laptop can.
  The "touch grass" theme isn't decoration here — offline capability is the
  entire point, and only open weights make it possible.
- **Your location stays yours.** Where you hike is personal data. With local
  inference, your trail plans never touch a server you don't control.
- **It costs nothing to run.** No per-token billing for a hobby tool you use
  twice a month. The economics of a closed API would kill this project;
  open weights make it free forever.
- **Models are swappable, not load-bearing.** Don't like Gemma's briefing
  style? `--model llama3.2` and you're done — no code changes, no
  renegotiating with a vendor. The deterministic core (difficulty math,
  grounding, fallback) stays identical no matter which weights you plug in.

A closed model could write a prettier paragraph. It couldn't do any of the
four things above. That's the whole argument.

## What I'd do next

Trailhead weather overlays, GPX import so distance/elevation come from the
file instead of your memory, and a `--compare` mode that briefs the same
trail with two models side by side. All doable without touching the core.

## Prize categories

- Overall
- **Best Use of Gemma** — Gemma (via Ollama) is the default briefing engine;
  the prompt, grounding strategy, and model-swap design are built around it.

---
*Built October 10, 2026 for the Hacktoberfest Week 1 DEV Challenge ("Touch Grass").
Tags: #devchallenge #hf26challenge*
