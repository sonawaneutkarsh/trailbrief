"""Offline template fallback — a genuinely useful briefing with no model at all.

Used automatically when Ollama is unreachable, so trailbrief works on the
trail with zero signal. Season-aware packing, elevation-aware safety notes,
and a Naismith-style pacing plan.
"""

from __future__ import annotations

from .briefing import Trail, estimate_difficulty, estimate_moving_hours


_SEASON_PACK = {
    "spring": [
        "Waterproof shell — spring showers arrive fast",
        "Traction aids if the route holds late-season snow",
        "Extra socks in a dry bag (mud season is real)",
    ],
    "summer": [
        "3+ liters of water — heat is the main hazard",
        "Sun protection: hat, sunglasses, sunscreen",
        "Start at dawn to dodge afternoon thunderstorms",
    ],
    "fall": [
        "Insulating mid-layer — temps swing 20°F+ through the day",
        "Headlamp with fresh batteries (shorter days sneak up on you)",
        "Bright colors — it's hunting season in many areas",
    ],
    "winter": [
        "Microspikes/snowshoes and knowledge of avalanche terrain",
        "Insulated water bottles or a thermos (tubes freeze)",
        "Emergency bivy — winter margins are thin",
    ],
}

_SEASON_WATCHOUTS = {
    "spring": "Meltwater can turn tame crossings into real hazards, and shaded north faces may still hold ice.",
    "summer": "Afternoon thunderstorms are the killer — be below treeline by noon and watch the sky, not just the forecast.",
    "fall": "Daylight is the constraint: sunset comes early and temperatures drop fast once the sun dips. Leaf-covered rocks are slippery.",
    "winter": "Short days, deep cold, and avalanche terrain demand conservative turn-around times. If in doubt, bail early.",
}

_EXPERIENCE_TIPS = {
    "beginner": "Keep your pack light, tell someone your plan, and turn back cheerfully if anything feels off — the mountain keeps.",
    "intermediate": "Pace by effort on climbs, not speed; eat before you're hungry and drink before you're thirsty.",
    "advanced": "You know the drill — but even strong hikers get caught by weather windows. Build in a margin.",
}


def render(trail: Trail) -> str:
    difficulty, why = estimate_difficulty(trail)
    hours = estimate_moving_hours(trail)
    season = trail.season.lower()
    pack = _SEASON_PACK.get(season, _SEASON_PACK["fall"])
    watch = _SEASON_WATCHOUTS.get(season, _SEASON_WATCHOUTS["fall"])
    tip = _EXPERIENCE_TIPS.get(trail.experience.lower(), _EXPERIENCE_TIPS["intermediate"])

    start_advice = (
        "Start no later than 8 AM — with "
        f"{hours:.1f} hours of moving time plus breaks, you want a buffer before dark."
        if hours >= 4
        else "A relaxed start works — this fits comfortably in a half day."
    )

    lines = [
        f"# Trail Briefing: {trail.name}",
        f"*{trail_summary_line(trail)}*",
        "",
        "## Overview",
        f"A {difficulty.lower()} day out: {why} Expect about {hours:.1f} hours of "
        "moving time, plus stops.",
        "",
        "## Pacing plan",
        start_advice,
        "Climb steadily and save something for the descent — most injuries happen "
        "on tired legs going down.",
        "",
        "## Pack list",
        "- Navigation: map + compass/GPS (phone dies, paper doesn't)",
        "- 2+ liters of water and calorie-dense food",
    ]
    lines += [f"- {item}" for item in pack]
    lines += [
        "",
        "## Watch-outs",
        f"Elevation: {trail.elevation_gain_ft:,} ft of gain means weather can differ "
        "sharply from the trailhead — carry a layer even if it starts warm.",
        watch,
        "",
        "## For you",
        tip,
        "",
        "## Leave No Trace",
        "Pack it in, pack it out — and stay on trail through muddy sections.",
        "",
        "_Generated offline by trailbrief's template engine (no model reachable)._",
    ]
    return "\n".join(lines)


def trail_summary_line(trail: Trail) -> str:
    difficulty, _ = estimate_difficulty(trail)
    return (
        f"{trail.location} · {trail.distance_mi:.1f} mi · "
        f"{trail.elevation_gain_ft:,} ft gain · {trail.season.title()} · {difficulty}"
    )
