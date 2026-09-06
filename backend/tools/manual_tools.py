# Hardcoded stand-in for real Chroma-backed retrieval (built in M4).
# Shape matches what search_manual will return once RAG is wired in,
# so downstream code doesn't need to change when the stub is replaced.
_STUB_RESULT = {
    "document": "ACX-200 Service Manual",
    "section": "Fault E27",
    "page": 42,
    "content_type": "troubleshooting",
    "text": (
        "Fault E27 indicates a stalled motor. Check the intake filter "
        "and motor thermal cutoff before attempting a restart."
    ),
}


def search_manual(asset_model: str, fault_code: str | None = None, question: str | None = None) -> dict:
    return {"asset_model": asset_model, **_STUB_RESULT}
