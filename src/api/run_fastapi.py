from fastapi import FastAPI, Query, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.query import (
    semantic_search,
    keyword_search,
    combine_results,
)

app = FastAPI()

Instrumentator().instrument(app).expose(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/search")
async def search(
    query: str = Query(
        ...,
        min_length=3,
        title="Search Query",
        description="Text query for semantic and keyword search",
        example="python programming",
    ),
    top_k: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of results to return",
        example=10
    )
):
    """
    Perform combined semantic and keyword search with pagination

    - **query**: Search query (3-100 characters)
    - **top_k**: Results per page (1-100)
    """

    if not query:
        return []

    try:
        semantic_results = semantic_search(query, top_k)
        keyword_results = keyword_search(query, top_k)
        results = combine_results(semantic_results, keyword_results)

        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
