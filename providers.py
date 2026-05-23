"""Music provider registry for MusicAI.

This module keeps the landing page and future OAuth adapters provider-driven instead
of hard-coding Spotify into the product experience.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class MusicProvider:
    id: str
    name: str
    tagline: str
    auth_type: str
    capabilities: tuple[str, ...]
    env_vars: tuple[str, ...] = field(default_factory=tuple)
    status: str = "planned"
    cta: str = "Coming soon"
    setup_url: str | None = None
    connect_route: str | None = None

    @property
    def is_configured(self) -> bool:
        return all(os.getenv(var) for var in self.env_vars) if self.env_vars else True

    @property
    def display_status(self) -> str:
        if self.status == "available" and not self.is_configured:
            return "needs-keys"
        return self.status


def get_music_providers(spotify_login_url: str | None = None) -> list[dict]:
    """Return provider cards for the MusicAI connection dashboard."""
    providers: Iterable[MusicProvider] = (
        MusicProvider(
            id="spotify",
            name="Spotify",
            tagline="Playlists, liked songs, top artists, recent listening, playback.",
            auth_type="OAuth 2.0",
            capabilities=("library", "playlists", "listening history", "playback"),
            env_vars=("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_CALLBACK_URL"),
            status="available",
            cta="Connect Spotify",
            setup_url=spotify_login_url,
        ),
        MusicProvider(
            id="apple_music",
            name="Apple Music",
            tagline="MusicKit library, playlists, recommendations, Apple ecosystem users.",
            auth_type="MusicKit + developer token",
            capabilities=("library", "playlists", "recommendations"),
            env_vars=("APPLE_TEAM_ID", "APPLE_KEY_ID", "APPLE_PRIVATE_KEY"),
            status="planned",
        ),
        MusicProvider(
            id="youtube_music",
            name="YouTube Music",
            tagline="YouTube playlists, music videos, channels, watch/listen behavior.",
            auth_type="Google OAuth 2.0",
            capabilities=("playlists", "videos", "channels", "search"),
            env_vars=("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"),
            status="available",
            cta="Connect YouTube",
            connect_route="/providers/youtube_music/connect",
        ),
        MusicProvider(
            id="soundcloud",
            name="SoundCloud",
            tagline="Independent artists, likes, tracks, creator discovery.",
            auth_type="OAuth 2.0",
            capabilities=("likes", "tracks", "artists", "discovery"),
            env_vars=("SOUNDCLOUD_CLIENT_ID", "SOUNDCLOUD_CLIENT_SECRET"),
            status="planned",
        ),
        MusicProvider(
            id="deezer",
            name="Deezer",
            tagline="Catalog search, playlists, albums, users, global music metadata.",
            auth_type="OAuth 2.0",
            capabilities=("library", "playlists", "catalog"),
            env_vars=("DEEZER_APP_ID", "DEEZER_SECRET"),
            status="planned",
        ),
        MusicProvider(
            id="lastfm",
            name="Last.fm",
            tagline="Scrobbles, taste history, artist similarity, long-term listening identity.",
            auth_type="API key + session auth",
            capabilities=("scrobbles", "top artists", "similarity", "history"),
            env_vars=("LASTFM_API_KEY", "LASTFM_SHARED_SECRET"),
            status="available",
            cta="Connect Last.fm",
            connect_route="/providers/lastfm/connect",
        ),
        MusicProvider(
            id="audius",
            name="Audius",
            tagline="Open artist discovery and Web3/independent music graph.",
            auth_type="public API / OAuth optional",
            capabilities=("discovery", "artists", "tracks", "trending"),
            status="planned",
        ),
        MusicProvider(
            id="musicbrainz",
            name="MusicBrainz + ListenBrainz",
            tagline="Open metadata, listening history, tags, recordings, artist relationships.",
            auth_type="public API + optional token",
            capabilities=("metadata", "recordings", "artist graph", "listens"),
            env_vars=("LISTENBRAINZ_TOKEN",),
            status="api-key",
            cta="Add token later",
        ),
        MusicProvider(
            id="lyrics",
            name="Lyrics Providers",
            tagline="Genius, Musixmatch, and LRCLIB fallback for lyric analysis.",
            auth_type="API keys / public lookup",
            capabilities=("lyrics", "sentiment", "emotion", "themes"),
            env_vars=("GENIUS_API_KEY",),
            status="api-key",
            cta="Configured by env",
        ),
        MusicProvider(
            id="recognition",
            name="Song Recognition",
            tagline="AudD, ACRCloud, or Shazam-like recognition from audio snippets.",
            auth_type="API keys",
            capabilities=("fingerprinting", "recognition", "metadata"),
            env_vars=("AUDD_API_TOKEN", "ACRCLOUD_ACCESS_KEY"),
            status="planned",
        ),
    )

    return [
        {
            "id": provider.id,
            "name": provider.name,
            "tagline": provider.tagline,
            "auth_type": provider.auth_type,
            "capabilities": list(provider.capabilities),
            "status": provider.display_status,
            "cta": provider.cta,
            "url": provider.setup_url or provider.connect_route,
        }
        for provider in providers
    ]
