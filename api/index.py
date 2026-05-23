"""Vercel Python entrypoint for MusicAI.

This intentionally keeps the public preview lightweight instead of importing the
entire legacy Spotify analysis module on cold start.
"""

from pathlib import Path
import os
import sys
from urllib.parse import urlencode

from flask import Flask, jsonify, render_template

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from providers import get_music_providers

app = Flask(
    __name__,
    static_url_path="/static",
    static_folder=str(PROJECT_ROOT / "static"),
    template_folder=str(PROJECT_ROOT / "templates"),
)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "musicai-preview")

SPOTIFY_SCOPES = " ".join(
    [
        "user-read-recently-played",
        "user-top-read",
        "playlist-read-private",
        "playlist-read-collaborative",
        "user-library-read",
        "user-read-email",
        "user-read-private",
    ]
)


def spotify_login_url() -> str:
    client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
    redirect_uri = os.getenv("SPOTIFY_CALLBACK_URL", "https://musicai-rouge.vercel.app/login/")
    if not client_id:
        return "#providers"
    return "https://accounts.spotify.com/authorize?" + urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": SPOTIFY_SCOPES,
        }
    )


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify(
        {
            "ok": True,
            "app": "MusicAI",
            "providers": {
                "spotify": bool(os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET")),
                "genius": bool(os.getenv("GENIUS_API_KEY")),
                "watson": bool(os.getenv("WATSON_API_KEY") and os.getenv("WATSON_SERVICE_URL")),
                "google_youtube": bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET")),
                "lastfm": bool(os.getenv("LASTFM_API_KEY") and os.getenv("LASTFM_SHARED_SECRET")),
            },
        }
    )


@app.route("/", methods=["GET"])
def home():
    login_url = spotify_login_url()
    return render_template(
        "homepage.html",
        content={
            "implicit_url": login_url,
            "refreshable_url": login_url,
            "providers": get_music_providers(login_url),
            "enabled_provider_count": 3,
            "planned_provider_count": 7,
        },
    )


@app.route("/Dashboard", methods=["GET"])
def dashboard_placeholder():
    return jsonify(
        {
            "ok": True,
            "message": "MusicAI preview is live. Full provider dashboard unlocks after OAuth callback URLs and provider keys are configured.",
        }
    )


application = app
