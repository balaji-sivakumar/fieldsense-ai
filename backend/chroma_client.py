"""Chroma client factory.

If CHROMA_API_KEY is set, connects to Chroma Cloud (reads
CHROMA_API_KEY/CHROMA_TENANT/CHROMA_DATABASE from the environment,
same names as .env.example). Otherwise falls back to a local
on-disk Chroma store under backend/chroma_data/ — same pattern as
database.py falling back to local SQLite before Postgres is
configured. Tests monkeypatch the module-level _client directly to
an ephemeral in-memory client for isolation.
"""

import os
from pathlib import Path

import chromadb

MANUAL_COLLECTION_NAME = "manuals"

_client = None


def get_client():
    global _client
    if _client is None:
        if os.getenv("CHROMA_API_KEY"):
            _client = chromadb.CloudClient()
        else:
            persist_dir = Path(__file__).parent / "chroma_data"
            _client = chromadb.PersistentClient(path=str(persist_dir))
    return _client


def get_manual_collection():
    return get_client().get_or_create_collection(name=MANUAL_COLLECTION_NAME)
