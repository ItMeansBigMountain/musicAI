"""Normalized music data models for cross-provider MusicAI features."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProviderRef:
    provider: str
    provider_id: str | None = None
    url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Artist:
    name: str
    refs: list[ProviderRef] = field(default_factory=list)
    image_url: str | None = None


@dataclass(frozen=True)
class Album:
    title: str
    artists: list[Artist] = field(default_factory=list)
    refs: list[ProviderRef] = field(default_factory=list)
    release_date: str | None = None
    image_url: str | None = None


@dataclass(frozen=True)
class Track:
    title: str
    artists: list[Artist] = field(default_factory=list)
    refs: list[ProviderRef] = field(default_factory=list)
    album: Album | None = None
    duration_ms: int | None = None
    isrc: str | None = None
    image_url: str | None = None
    popularity: float | None = None


@dataclass(frozen=True)
class Playlist:
    title: str
    refs: list[ProviderRef] = field(default_factory=list)
    owner_name: str | None = None
    description: str | None = None
    image_url: str | None = None
    track_count: int | None = None


@dataclass(frozen=True)
class ListenEvent:
    track: Track
    provider: str
    played_at: str | None = None
    context: str | None = None


@dataclass(frozen=True)
class Lyrics:
    track: Track
    provider: str
    text: str | None = None
    synced: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class AudioFeature:
    track: Track
    provider: str
    danceability: float | None = None
    energy: float | None = None
    valence: float | None = None
    tempo: float | None = None
    mood_tags: list[str] = field(default_factory=list)


def to_dict(value: Any) -> dict[str, Any]:
    return asdict(value)


def normalize_spotify_track(item: dict[str, Any]) -> Track:
    album_data = item.get("album") or {}
    images = album_data.get("images") or item.get("images") or []
    image_url = images[0]["url"] if images else None
    artists = [Artist(name=artist.get("name", "Unknown")) for artist in item.get("artists", [])]
    album = Album(
        title=album_data.get("name", "Unknown album"),
        artists=artists,
        refs=[ProviderRef(provider="spotify", provider_id=album_data.get("id"), url=album_data.get("external_urls", {}).get("spotify"))],
        release_date=album_data.get("release_date"),
        image_url=image_url,
    ) if album_data else None

    return Track(
        title=item.get("name", "Unknown track"),
        artists=artists,
        album=album,
        duration_ms=item.get("duration_ms"),
        isrc=(item.get("external_ids") or {}).get("isrc"),
        image_url=image_url,
        popularity=item.get("popularity"),
        refs=[ProviderRef(provider="spotify", provider_id=item.get("id"), url=item.get("external_urls", {}).get("spotify"), raw=item)],
    )


def normalize_lastfm_track(item: dict[str, Any]) -> Track:
    artist_name = item.get("artist")
    if isinstance(artist_name, dict):
        artist_name = artist_name.get("#text") or artist_name.get("name")
    images = item.get("image") or []
    image_url = next((img.get("#text") for img in reversed(images) if img.get("#text")), None)
    return Track(
        title=item.get("name", "Unknown track"),
        artists=[Artist(name=artist_name or "Unknown")],
        image_url=image_url,
        refs=[ProviderRef(provider="lastfm", provider_id=item.get("mbid"), url=item.get("url"), raw=item)],
    )


def normalize_youtube_video(item: dict[str, Any]) -> Track:
    snippet = item.get("snippet") or {}
    thumbnails = snippet.get("thumbnails") or {}
    image_url = (thumbnails.get("high") or thumbnails.get("medium") or thumbnails.get("default") or {}).get("url")
    video_id = item.get("id")
    if isinstance(video_id, dict):
        video_id = video_id.get("videoId")
    return Track(
        title=snippet.get("title", "Unknown video"),
        artists=[Artist(name=snippet.get("channelTitle", "YouTube"))],
        image_url=image_url,
        refs=[ProviderRef(provider="youtube_music", provider_id=video_id, url=f"https://www.youtube.com/watch?v={video_id}" if video_id else None, raw=item)],
    )
