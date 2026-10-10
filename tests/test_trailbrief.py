"""Unit tests for trailbrief. Run: python -m pytest tests/  (or python -m unittest)."""

import json
import unittest
from unittest.mock import patch

from trailbrief import briefing, fallback
from trailbrief.ollama_client import OllamaError


def sample_trail(**kw):
    base = dict(
        name="Ricketts Glen Falls Trail",
        distance_mi=7.2,
        elevation_gain_ft=1200,
        location="Benton, PA",
        season="fall",
        experience="intermediate",
    )
    base.update(kw)
    return briefing.Trail(**base)


class TestDifficulty(unittest.TestCase):
    def test_easy(self):
        d, _ = briefing.estimate_difficulty(sample_trail(distance_mi=2.0, elevation_gain_ft=200))
        self.assertEqual(d, "Easy")

    def test_moderate(self):
        d, _ = briefing.estimate_difficulty(sample_trail())
        self.assertEqual(d, "Moderate")

    def test_hard(self):
        d, _ = briefing.estimate_difficulty(sample_trail(distance_mi=12.0, elevation_gain_ft=3500))
        self.assertEqual(d, "Hard")

    def test_expert(self):
        d, _ = briefing.estimate_difficulty(sample_trail(distance_mi=18.0, elevation_gain_ft=6000))
        self.assertEqual(d, "Expert")

    def test_moving_hours_sane(self):
        h = briefing.estimate_moving_hours(sample_trail())
        self.assertGreater(h, 3)
        self.assertLess(h, 8)


class TestPrompt(unittest.TestCase):
    def test_prompt_grounds_numbers(self):
        prompt = briefing.build_prompt(sample_trail())
        self.assertIn("Ricketts Glen Falls Trail", prompt)
        self.assertIn("7.2 miles", prompt)
        self.assertIn("1,200 ft", prompt)
        self.assertIn("do not invent", prompt.lower())


class TestFallback(unittest.TestCase):
    def test_sections_present(self):
        out = fallback.render(sample_trail())
        for section in ["## Overview", "## Pacing plan", "## Pack list",
                        "## Watch-outs", "## Leave No Trace"]:
            self.assertIn(section, out)

    def test_fall_packing_is_seasonal(self):
        out = fallback.render(sample_trail(season="fall"))
        self.assertIn("Headlamp", out)
        winter = fallback.render(sample_trail(season="winter"))
        self.assertIn("Microspikes", winter)

    def test_mentions_trail_name(self):
        self.assertIn("Ricketts Glen", fallback.render(sample_trail()))


class TestOllamaPath(unittest.TestCase):
    """Mock the HTTP layer — no Ollama server needed."""

    def _fake_urlopen(self, response_body: dict):
        class Resp:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return json.dumps(response_body).encode()
        return Resp()

    @patch("trailbrief.ollama_client.urllib.request.urlopen")
    def test_generate_parses_response(self, mock_open):
        from trailbrief import ollama_client
        mock_open.return_value = self._fake_urlopen({"response": "## Overview\nNice hike."})
        text = ollama_client.generate("prompt", model="gemma3")
        self.assertIn("Nice hike", text)
        # verify it POSTed to /api/generate with the right model
        req = mock_open.call_args[0][0]
        self.assertTrue(req.full_url.endswith("/api/generate"))
        self.assertEqual(json.loads(req.data)["model"], "gemma3")

    @patch("trailbrief.ollama_client.urllib.request.urlopen")
    def test_generate_raises_ollama_error(self, mock_open):
        import urllib.error
        from trailbrief import ollama_client
        mock_open.side_effect = urllib.error.URLError("connection refused")
        with self.assertRaises(OllamaError):
            ollama_client.generate("prompt")

    @patch("trailbrief.ollama_client.urllib.request.urlopen")
    def test_model_available(self, mock_open):
        from trailbrief import ollama_client
        mock_open.return_value = self._fake_urlopen(
            {"models": [{"name": "gemma3:latest"}, {"name": "llama3.2:3b"}]}
        )
        self.assertTrue(ollama_client.model_available("gemma3"))
        self.assertFalse(ollama_client.model_available("mixtral"))


if __name__ == "__main__":
    unittest.main()
