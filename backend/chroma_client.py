"""Chroma client factory.

If CHROMA_API_KEY is set, connects to Chroma Cloud (reads
CHROMA_API_KEY/CHROMA_TENANT/CHROMA_DATABASE from the environment,
same names as .env.example). Otherwise falls back to a local
on-disk Chroma store under backend/chroma_data/ — same pattern as
database.py falling back to local SQLite before Postgres is
configured. Tests monkeypatch the module-level _client directly to
an ephemeral in-memory client for isolation.

NOTE: api_key is passed explicitly rather than relying on
chromadb.CloudClient()'s own no-arg env-var resolution — as installed
(chromadb==1.5.9), that path has a real bug: it validates CHROMA_API_KEY
exists, then discards the resolved value and sends str(None) as the
actual auth token, causing every call to fail with "Permission denied"
regardless of how correct the credentials are. tenant/database aren't
affected (their env-var fallback does work), but passing everything
explicitly here sidesteps the bug entirely rather than depending on
this being fixed upstream.
"""

import os
from pathlib import Path

import chromadb

MANUAL_COLLECTION_NAME = "manuals"

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("CHROMA_API_KEY")
        if api_key:
            _client = chromadb.CloudClient(
                api_key=api_key,
                tenant=os.getenv("CHROMA_TENANT"),
                database=os.getenv("CHROMA_DATABASE"),
            )
        else:
            persist_dir = Path(__file__).parent / "chroma_data"
            _client = chromadb.PersistentClient(path=str(persist_dir))
    return _client


def get_manual_collection():
    return get_client().get_or_create_collection(name=MANUAL_COLLECTION_NAME)


def check_connection() -> bool:
    """Used by /health for the M7 degraded-state UI requirement."""
    try:
        get_manual_collection().count()
        return True
    except Exception:
        return False


def warm_up() -> None:
    """Force the default embedding model to download/load now, during
    startup, instead of on the first real search_manual call.

    Confirmed live (2026-09-26): a fresh container has no cached ONNX
    model, so the first .query() call triggers an ~80MB download that
    took 30+ seconds — well past tool_registry's 10s tool timeout,
    causing a real "search_manual timed out" failure on the first
    query after any redeploy. .count() alone doesn't trigger this (no
    embedding needed to just read metadata); only add()/query() do.
    """
    try:
        get_manual_collection().query(query_texts=["warm up"], n_results=1)
    except Exception:
        pass  # best-effort — check_connection() is the real health signal
