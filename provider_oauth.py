"""Provider OAuth adapters for MusicAI.

The legacy app keeps Spotify in musicAI.py. This module adds provider-neutral
connect/callback helpers for newer integrations.
"""

from __future__ import annotations

import hashlib
import os
import secrets
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import requests

from token_store import ProviderToken, save_provider_token


@dataclass(frozen=True)
class OAuthStart:
    provider: str
    url: str
    state: str | None = None
    token: str | None = None


def _base_url() -> str:
    return os.getenv("MUSICAI_PUBLIC_BASE_URL", "").rstrip("/")


def provider_callback_url(provider: str) -> str:
    configured = os.getenv(f"{provider.upper()}_CALLBACK_URL")
    if configured:
        return configured
    base = _base_url()
    if base:
        return f"{base}/providers/{provider}/callback"
    return f"/providers/{provider}/callback"


def google_scopes() -> str:
    return " ".join(
        [
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/youtube.readonly",
        ]
    )


def start_youtube_oauth() -> OAuthStart:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    if not client_id:
        raise RuntimeError("GOOGLE_CLIENT_ID is not configured")

    state = secrets.token_urlsafe(32)
    params = {
        "client_id": client_id,
        "redirect_uri": provider_callback_url("youtube_music"),
        "response_type": "code",
        "scope": google_scopes(),
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
        "state": state,
    }
    return OAuthStart(
        provider="youtube_music",
        url="https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params),
        state=state,
    )


def exchange_youtube_code(code: str, user_id: str) -> ProviderToken:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise RuntimeError("Google OAuth credentials are not configured")

    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": provider_callback_url("youtube_music"),
            "grant_type": "authorization_code",
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()

    profile = _fetch_google_profile(payload.get("access_token"))
    provider_account_id = profile.get("sub") or profile.get("email")

    token = ProviderToken(
        user_id=user_id,
        provider="youtube_music",
        provider_account_id=provider_account_id,
        access_token=payload.get("access_token"),
        refresh_token=payload.get("refresh_token"),
        expires_at=time.time() + payload.get("expires_in", 3600),
        scopes=payload.get("scope") or google_scopes(),
        metadata={
            "email": profile.get("email"),
            "name": profile.get("name"),
            "picture": profile.get("picture"),
        },
    )
    save_provider_token(token)
    return token


def _fetch_google_profile(access_token: str | None) -> dict[str, Any]:
    if not access_token:
        return {}
    response = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )
    if response.status_code >= 400:
        return {}
    return response.json()


def _lastfm_signature(params: dict[str, str]) -> str:
    secret = os.getenv("LASTFM_SHARED_SECRET", "")
    if not secret:
        raise RuntimeError("LASTFM_SHARED_SECRET is not configured")
    raw = "".join(f"{key}{params[key]}" for key in sorted(params)) + secret
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _lastfm_api(params: dict[str, str]) -> dict[str, Any]:
    api_key = os.getenv("LASTFM_API_KEY", "")
    if not api_key:
        raise RuntimeError("LASTFM_API_KEY is not configured")

    signed = {**params, "api_key": api_key, "format": "json"}
    signed["api_sig"] = _lastfm_signature(
        {key: value for key, value in signed.items() if key != "format"}
    )
    response = requests.post("https://ws.audioscrobbler.com/2.0/", data=signed, timeout=20)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"Last.fm error {payload.get('error')}: {payload.get('message')}")
    return payload


def start_lastfm_auth() -> OAuthStart:
    api_key = os.getenv("LASTFM_API_KEY", "")
    if not api_key:
        raise RuntimeError("LASTFM_API_KEY is not configured")
    payload = _lastfm_api({"method": "auth.getToken"})
    token = payload["token"]
    return OAuthStart(
        provider="lastfm",
        url="https://www.last.fm/api/auth/?" + urlencode(
            {"api_key": api_key, "token": token, "cb": provider_callback_url("lastfm")}
        ),
        token=token,
    )


def complete_lastfm_auth(lastfm_token: str, user_id: str) -> ProviderToken:
    payload = _lastfm_api({"method": "auth.getSession", "token": lastfm_token})
    session = payload["session"]
    token = ProviderToken(
        user_id=user_id,
        provider="lastfm",
        provider_account_id=session.get("name"),
        access_token=session.get("key"),
        refresh_token=None,
        expires_at=None,
        scopes="scrobbles top-artists top-tracks loved-tracks",
        metadata={"username": session.get("name")},
    )
    save_provider_token(token)
    return token


def start_provider_oauth(provider_id: str) -> OAuthStart:
    if provider_id == "youtube_music":
        return start_youtube_oauth()
    if provider_id == "lastfm":
        return start_lastfm_auth()
    raise ValueError(f"Provider {provider_id} is not connectable yet")


def complete_provider_oauth(provider_id: str, args: dict[str, str], user_id: str) -> ProviderToken:
    if provider_id == "youtube_music":
        code = args.get("code")
        if not code:
            raise RuntimeError("Missing Google OAuth code")
        return exchange_youtube_code(code, user_id)
    if provider_id == "lastfm":
        token = args.get("token") or args.get("lastfm_token")
        if not token:
            raise RuntimeError("Missing Last.fm auth token")
        return complete_lastfm_auth(token, user_id)
    raise ValueError(f"Provider {provider_id} is not connectable yet")
