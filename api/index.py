"""Vercel Python entrypoint for the legacy MusicAI Flask app."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from musicAI import application as app

application = app
