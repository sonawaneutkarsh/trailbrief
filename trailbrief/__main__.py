"""`python -m trailbrief` — command-line interface."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .briefing import Trail, build_prompt, trail_summary
from . import fallback
from .ollama_client import OllamaError, generate, model_available


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="trailbrief",
        description="Personalized hiking briefings from a local open-weight model.",
    )
    p.add_argument("--name", required=True, help="Trail name")
    p.add_argument("--distance", type=float, required=True, help="Distance in miles")
    p.add_argument("--elevation", type=int, required=True, help="Elevation gain in feet")
    p.add_argument("--location", required=True, help="Where the trail is")
    p.add_argument(
        "--season",
        required=True,
        choices=["spring", "summer", "fall", "winter"],
        help="Season of the hike",
    )
    p.add_argument(
        "--experience",
        default="intermediate",
        choices=["beginner", "intermediate", "advanced"],
        help="Hiker experience level (default: intermediate)",
    )
    p.add_argument("--model", default="gemma3", help="Ollama model (default: gemma3)")
    p.add_argument(
        "--host",
        default="http://localhost:11434",
        help="Ollama host (default: http://localhost:11434)",
    )
    p.add_argument(
        "--offline",
        action="store_true",
        help="Skip the model and use the offline template engine",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    trail = Trail(
        name=args.name,
        distance_mi=args.distance,
        elevation_gain_ft=args.elevation,
        location=args.location,
        season=args.season,
        experience=args.experience,
    )

    print(trail_summary(trail), file=sys.stderr)
    print("─" * 60, file=sys.stderr)

    if not args.offline:
        if model_available(args.model, args.host):
            try:
                print(generate(build_prompt(trail), model=args.model, host=args.host))
                return 0
            except OllamaError as exc:
                print(f"[model failed: {exc} — using offline template]", file=sys.stderr)
        else:
            print(
                f"[model '{args.model}' not found at {args.host} — using offline template]",
                file=sys.stderr,
            )

    print(fallback.render(trail))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
