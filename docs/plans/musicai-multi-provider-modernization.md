# MusicAI Multi-Provider Modernization Work Queue

> **For Hermes:** Use this as the active work queue for developing MusicAI from Spotify-only “SPOTTY AI” into a modern cross-platform music intelligence app.

**Goal:** Modernize MusicAI with a cleaner UI, provider-based OAuth architecture, and integrations beyond Spotify.

**Architecture:** Keep the current Flask app working while adding a provider registry and normalized connection dashboard. Start with Spotify as the only fully wired OAuth flow, then add provider modules for Apple Music, YouTube, SoundCloud, Deezer, Last.fm, Audius, MusicBrainz/ListenBrainz, and lyrics/audio-intelligence providers.

**Tech Stack:** Flask, Jinja templates, CSS, requests, OAuth 2.0 provider adapters, encrypted token storage later.

---

## Phase 1 — Visual + product foundation

- Rebrand homepage from “SPOTTY AI” to “MusicAI”.
- Replace old Bootstrap-heavy landing page with a modern music-intelligence hero.
- Add provider cards for Spotify, Apple Music, YouTube Music, SoundCloud, Deezer, Last.fm, Audius, MusicBrainz/ListenBrainz, Genius/Musixmatch, AudD/ACRCloud.
- Mark providers as `connected`, `available`, `planned`, or `api-key`.
- Keep existing Spotify login working.

## Phase 2 — Provider architecture

- Create `providers/` package.
- Add a provider registry with scopes, auth type, capabilities, and env var names.
- Normalize provider data into shared concepts: artist, track, album, playlist, listening event, lyric, audio fingerprint, mood tag.
- Add database-backed token storage design.

## Phase 3 — OAuth expansion

- Implement OAuth adapters in this order:
  1. Spotify existing flow cleanup
  2. Last.fm auth/API session
  3. YouTube Data API OAuth
  4. SoundCloud OAuth
  5. Deezer OAuth
  6. Apple Music / MusicKit developer token flow
  7. Audius API/no-auth discovery

## Phase 4 — Intelligence features

- Cross-platform taste profile.
- Playlist and liked-song sentiment/mood analysis.
- Lyrics analysis with Genius/Musixmatch/LRCLIB fallback.
- Song recognition with AudD/ACRCloud.
- Artist trend/event cards with Bandsintown/Ticketmaster.
- Weekly “your music identity” report.

## Phase 5 — Production hardening

- Move tokens out of `user_tokens.json` into encrypted DB storage.
- Add tests for provider registry and auth URL generation.
- Add rate limiting/caching.
- Add provider setup docs and `.env.example` updates.
- Deploy with proper secret management.

## User input needed later

- OAuth app credentials for each vendor the user wants live: Spotify, Apple, Google/YouTube, SoundCloud, Deezer, Last.fm, Musixmatch, AudD/ACRCloud.
- Decision on deployment target: Render, Vercel + API, Azure App Service, or container.
