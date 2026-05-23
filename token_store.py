"""Encrypted SQLite token storage for MusicAI provider accounts.

This replaces the legacy user_tokens.json pattern with one row per user/provider.
Tokens are encrypted with Fernet using MUSICAI_TOKEN_SECRET or FLASK_SECRET_KEY.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("MUSICAI_TOKEN_DB", "musicai_tokens.db"))
TOKEN_SECRET_ENV = "MUSICAI_TOKEN_SECRET"


@dataclass
class ProviderToken:
    user_id: str
    provider: str
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: float | None = None
    scopes: str | None = None
    provider_account_id: str | None = None
    metadata: dict[str, Any] | None = None


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS provider_tokens (
            user_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            provider_account_id TEXT,
            access_token_enc TEXT,
            refresh_token_enc TEXT,
            expires_at REAL,
            scopes TEXT,
            metadata_json TEXT,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            PRIMARY KEY (user_id, provider)
        )
        """
    )
    conn.commit()
    return conn


def _token_secret() -> str:
    secret = os.getenv(TOKEN_SECRET_ENV) or os.getenv("FLASK_SECRET_KEY")
    if not secret or secret == "something secret":
        raise RuntimeError(
            "Set MUSICAI_TOKEN_SECRET or a strong FLASK_SECRET_KEY before storing provider tokens."
        )
    return secret


def _fernet():
    import importlib

    fernet_module = importlib.import_module("cryptography.fernet")
    Fernet = fernet_module.Fernet

    digest = hashlib.sha256(_token_secret().encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def _openssl_encrypt(value: str) -> str:
    import subprocess

    env = {**os.environ, "MUSICAI_OPENSSL_SECRET": _token_secret()}
    result = subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-a", "-pass", "env:MUSICAI_OPENSSL_SECRET"],
        input=value,
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    return result.stdout.strip()


def _openssl_decrypt(value: str) -> str:
    import subprocess

    env = {**os.environ, "MUSICAI_OPENSSL_SECRET": _token_secret()}
    result = subprocess.run(
        ["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-a", "-pass", "env:MUSICAI_OPENSSL_SECRET"],
        input=value + "\n",
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    return result.stdout


def encrypt_token(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return "fernet:" + _fernet().encrypt(value.encode("utf-8")).decode("utf-8")
    except ImportError:
        return "openssl:" + _openssl_encrypt(value)


def decrypt_token(value: str | None) -> str | None:
    if not value:
        return None
    if value.startswith("fernet:"):
        return _fernet().decrypt(value.removeprefix("fernet:").encode("utf-8")).decode("utf-8")
    if value.startswith("openssl:"):
        return _openssl_decrypt(value.removeprefix("openssl:"))
    # Backward compatibility for rows written before explicit scheme prefixes.
    return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")


def save_provider_token(token: ProviderToken) -> None:
    now = time.time()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO provider_tokens (
                user_id, provider, provider_account_id, access_token_enc,
                refresh_token_enc, expires_at, scopes, metadata_json,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, provider) DO UPDATE SET
                provider_account_id=excluded.provider_account_id,
                access_token_enc=excluded.access_token_enc,
                refresh_token_enc=excluded.refresh_token_enc,
                expires_at=excluded.expires_at,
                scopes=excluded.scopes,
                metadata_json=excluded.metadata_json,
                updated_at=excluded.updated_at
            """,
            (
                token.user_id,
                token.provider,
                token.provider_account_id,
                encrypt_token(token.access_token),
                encrypt_token(token.refresh_token),
                token.expires_at,
                token.scopes,
                json.dumps(token.metadata or {}),
                now,
                now,
            ),
        )
        conn.commit()


def load_provider_token(user_id: str, provider: str) -> ProviderToken | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM provider_tokens WHERE user_id = ? AND provider = ?",
            (user_id, provider),
        ).fetchone()

    if not row:
        return None

    return ProviderToken(
        user_id=row["user_id"],
        provider=row["provider"],
        provider_account_id=row["provider_account_id"],
        access_token=decrypt_token(row["access_token_enc"]),
        refresh_token=decrypt_token(row["refresh_token_enc"]),
        expires_at=row["expires_at"],
        scopes=row["scopes"],
        metadata=json.loads(row["metadata_json"] or "{}"),
    )


def list_provider_tokens(user_id: str) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT user_id, provider, provider_account_id, expires_at, scopes,
                   metadata_json, created_at, updated_at
            FROM provider_tokens
            WHERE user_id = ?
            ORDER BY provider
            """,
            (user_id,),
        ).fetchall()

    return [
        {
            "user_id": row["user_id"],
            "provider": row["provider"],
            "provider_account_id": row["provider_account_id"],
            "expires_at": row["expires_at"],
            "scopes": row["scopes"],
            "metadata": json.loads(row["metadata_json"] or "{}"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]


def delete_provider_token(user_id: str, provider: str) -> None:
    with _connect() as conn:
        conn.execute(
            "DELETE FROM provider_tokens WHERE user_id = ? AND provider = ?",
            (user_id, provider),
        )
        conn.commit()
