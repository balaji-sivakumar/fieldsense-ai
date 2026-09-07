import asyncio

import chromadb
import pytest

import chroma_client
from tool_registry import dispatch


@pytest.fixture(autouse=True)
def ephemeral_chroma_with_two_models(monkeypatch):
    """Isolated in-memory Chroma seeded with two different models, so
    cross-model leakage would be provable (not just "empty results")."""
    client = chromadb.EphemeralClient()
    monkeypatch.setattr(chroma_client, "_client", client)

    collection = client.get_or_create_collection(name=chroma_client.MANUAL_COLLECTION_NAME)
    collection.add(
        ids=["ACX-200-0", "ACX-999-0"],
        documents=[
            "Fault E27 on the ACX-200 indicates a stalled motor; check the intake filter.",
            "Fault E27 on the ACX-999 indicates a coolant sensor fault; check the coolant loop.",
        ],
        metadatas=[
            {
                "equipment_type": "air_compressor",
                "manufacturer": "DemoAir",
                "model": "ACX-200",
                "document": "ACX-200 Service Manual",
                "section": "Fault E27: Motor Stall",
                "page": 42,
                "content_type": "troubleshooting",
            },
            {
                "equipment_type": "air_compressor",
                "manufacturer": "DemoAir",
                "model": "ACX-999",
                "document": "ACX-999 Service Manual",
                "section": "Fault E27: Coolant Sensor",
                "page": 12,
                "content_type": "troubleshooting",
            },
        ],
    )
    yield
    monkeypatch.setattr(chroma_client, "_client", None)


def run(tool_name: str, args: dict):
    return asyncio.run(dispatch(tool_name, args, session_id="test"))


def test_search_manual_filters_by_model():
    result = run("search_manual", {"asset_model": "ACX-200", "fault_code": "E27"})
    assert result["status"] == "ok"
    body = result["result"]
    assert body["found"] is True
    assert "stalled motor" in body["text"]
    assert "coolant" not in body["text"].lower()


def test_search_manual_never_leaks_other_model():
    result = run("search_manual", {"asset_model": "ACX-999", "fault_code": "E27"})
    body = result["result"]
    assert body["found"] is True
    assert "coolant" in body["text"].lower()
    assert "stalled motor" not in body["text"]


def test_search_manual_unknown_model_returns_not_found():
    result = run("search_manual", {"asset_model": "ACX-000"})
    assert result["status"] == "ok"
    assert result["result"]["found"] is False
