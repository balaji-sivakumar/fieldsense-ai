from chroma_client import get_manual_collection

N_RESULTS = 3


def search_manual(asset_model: str, fault_code: str | None = None, question: str | None = None) -> dict:
    collection = get_manual_collection()

    if question:
        query_text = question
    elif fault_code:
        query_text = f"fault code {fault_code} troubleshooting"
    else:
        query_text = f"{asset_model} troubleshooting guidance"

    # Model filter is required by the tool's JSON Schema (asset_model is
    # a required argument), so retrieval can never search across models —
    # see CLAUDE.md: "Retrieval must first identify the asset model and
    # then filter searches to the correct model."
    result = collection.query(query_texts=[query_text], n_results=N_RESULTS, where={"model": asset_model})

    ids = result["ids"][0]
    if not ids:
        return {"asset_model": asset_model, "found": False}

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    top_meta = metadatas[0]

    return {
        "asset_model": asset_model,
        "found": True,
        "document": top_meta["document"],
        "section": top_meta["section"],
        "page": top_meta["page"],
        "content_type": top_meta["content_type"],
        "text": documents[0],
        "related_sections": [{"section": m["section"], "page": m["page"]} for m in metadatas[1:]],
    }
