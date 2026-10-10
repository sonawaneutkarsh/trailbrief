"""Core briefing logic: trail model, difficulty estimation, prompt building."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Trail:
    name: str
    distance_mi: float
    elevation_gain_ft: int
    location: str
    season: str  # spring | summer | fall | winter
    experience: str = "intermediate"  # beginner | intermediate | advanced


def estimate_difficulty(trail: Trail) -> tuple[str, str]:
    """Return (label, explanation) from distance + elevation heuristics.

    Score ~= miles + (elevation ft / 1000). Tuned so a flat 3-miler is Easy
    and a 12-mile / 4000-ft day is Hard.
    """
    score = trail.distance_mi + trail.elevation_gain_ft / 1000.0
    if score < 5:
        return "Easy", (
            f"{trail.distance_mi:.1f} miles with {trail.elevation_gain_ft:,} ft of gain "
            "is a relaxed outing for most hikers."
        )
    if score < 10:
        return "Moderate", (
            f"{trail.distance_mi:.1f} miles and {trail.elevation_gain_ft:,} ft of gain "
            "asks for steady pacing and a real lunch stop."
        )
    if score < 16:
        return "Hard", (
            f"{trail.distance_mi:.1f} miles with {trail.elevation_gain_ft:,} ft of gain "
            "is a full-day effort — start early and budget extra time."
        )
    return "Expert", (
        f"{trail.distance_mi:.1f} miles and {trail.elevation_gain_ft:,} ft of gain "
        "is a serious undertaking. Only attempt with training and a bail-out plan."
    )


def estimate_moving_hours(trail: Trail) -> float:
    """Naismith-ish estimate: 2 mph + 30 min per 1000 ft of gain."""
    return trail.distance_mi / 2.0 + (trail.elevation_gain_ft / 1000.0) * 0.5


def build_prompt(trail: Trail) -> str:
    """Build the prompt sent to the local model."""
    difficulty, why = estimate_difficulty(trail)
    hours = estimate_moving_hours(trail)
    return f"""You are a knowledgeable hiking guide writing a trail briefing.

Trail: {trail.name}
Location: {trail.location}
Distance: {trail.distance_mi:.1f} miles round trip
Elevation gain: {trail.elevation_gain_ft:,} ft
Season: {trail.season}
Hiker experience: {trail.experience}
Estimated difficulty: {difficulty} ({why})
Estimated moving time: {hours:.1f} hours

Write a concise, practical briefing with exactly these sections, using the
numbers above (do not invent trail features, facilities, or water sources):

## Overview
One short paragraph: what kind of day this is.

## Pacing plan
When to start and how to split the effort, based on the estimated moving time.

## Pack list
Season-appropriate essentials for a {trail.experience} hiker in {trail.season}.

## Watch-outs
Elevation, weather, and daylight risks specific to these stats and season.

## Leave No Trace
One line reminder.

Keep the whole briefing under 300 words. Plain markdown, no fluff."""


def trail_summary(trail: Trail) -> str:
    difficulty, _ = estimate_difficulty(trail)
    return (
        f"{trail.name} — {trail.location} | "
        f"{trail.distance_mi:.1f} mi, {trail.elevation_gain_ft:,} ft gain | "
        f"{trail.season.title()} | {difficulty}"
    )
