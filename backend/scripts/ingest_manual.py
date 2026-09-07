"""Ingest the synthetic ACX-200 service manual into Chroma.

Usage:
    cd backend && source venv/bin/activate
    python scripts/ingest_manual.py

Uses chroma_client.get_client() — Chroma Cloud if CHROMA_API_KEY is
set in .env, otherwise a local on-disk store under backend/chroma_data/.
Safe to re-run: deletes and recreates the collection each time so
edits to the manual content are reflected (Chroma silently ignores
re-added documents with duplicate IDs, which would otherwise mask
content changes).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from chroma_client import MANUAL_COLLECTION_NAME, get_client
from data.manuals.acx200_service_manual import DOCUMENT_NAME, EQUIPMENT_TYPE, MANUFACTURER, MODEL, SECTIONS


def main() -> None:
    client = get_client()

    try:
        client.delete_collection(MANUAL_COLLECTION_NAME)
    except Exception:
        pass  # collection didn't exist yet

    collection = client.get_or_create_collection(name=MANUAL_COLLECTION_NAME)

    ids = [f"{MODEL}-{i}" for i in range(len(SECTIONS))]
    documents = [s["text"] for s in SECTIONS]
    metadatas = [
        {
            "equipment_type": EQUIPMENT_TYPE,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "document": DOCUMENT_NAME,
            "section": s["section"],
            "page": s["page"],
            "content_type": s["content_type"],
        }
        for s in SECTIONS
    ]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Ingested {len(ids)} chunks from {DOCUMENT_NAME} into collection '{MANUAL_COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()
