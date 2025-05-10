import os
from typing import Dict, List

from psycopg2.extras import RealDictCursor

from src.utils.config import QUESTION_URL
from src.utils.helper import get_db_connection
from src.utils.logger import setup_logger
from src.utils.work_pinecone import PineconeClient

logger = setup_logger(level=10)

# db_params = {
#     "dbname": os.getenv("POSTGRES_DB"),
#     "user": os.getenv("POSTGRES_USER"),
#     "password": os.getenv("POSTGRES_PASSWORD"),
#     "host": "localhost",
#     "port": os.getenv("POSTGRES_PORT", "5432"),
# }


def keyword_search(query: str, top_k: int = 10) -> List[Dict[str, float]]:
    """
    Perform a keyword-based full-text search on the 'questions' table in PostgreSQL.

    Args:
        query (str): The search query string.
        top_k (int, optional): The maximum number of results to return. Defaults to 10.

    Returns:
        List[Dict[str, float]]: A list of dictionaries, each containing:
            - 'id' (int or str): The unique identifier of the question.
            - 'score' (float): The relevance rank score computed by ts_rank_cd.
            - 'title' (str): The title of the question.
    
    Raises:
        ConnectionError: If the database connection could not be established.
        Exception: For any other errors during query execution.
    """
    
    sql_query = """
        SELECT 
            id, title,
            ts_rank_cd(tsv, plainto_tsquery('russian', %s)) AS rank
        FROM questions
        WHERE tsv @@ plainto_tsquery('russian', %s)
        ORDER BY rank DESC
        LIMIT %s
    """

SELECT * FROM questions
WHERE language = 'en' AND to_tsvector('english', text) @@ plainto_tsquery('english', 'query');

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise ConnectionError("Failed to establish database connection")

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql_query, (query, query, top_k))
            results = cur.fetchall()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        conn.close()

    return [{"id": row["id"], "score": row["rank"], "title": row["title"]} for row in results]


def semantic_search(
        text_query: str,
        top_k: int = 10, 
        rerank: bool = False
) -> List[Dict[str, float]]:
    """
    Perform a semantic search query using Pinecone dense index.

    Args:
        text_query (str): The input text query for semantic search.
        top_k (int, optional): Number of top results to return. Defaults to 10.
        rerank (bool, optional): Whether to apply reranking using a specified model. Defaults to False.

    Returns:
        List[Dict[str, float]]: The search results returned by Pinecone, or None if the search fails.
            The structure depends on Pinecone client's `search_records` method.
    """

    pc = PineconeClient()

    try:
        response = pc.dense_index.search_records(
            namespace=pc.namespace,
            query={
                "inputs": {
                    "text": text_query,
                },
                "top_k": top_k,
            },
            rerank={
                "model": "cohere-rerank-3.5",
                "rank_fields": ["title"]
            } if rerank else None
        )
        return response.result.hits
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return []


def combine_results(
        semantic_results: List[Dict[str, float]], 
        keyword_results: List[Dict[str, float]], 
        weight_semantic: float = 0.7, 
        weight_keyword: float = 0.3
    ) -> List[Dict[str, float]]:
    """
    Combine semantic and keyword search results into a single ranked list.

    This function merges two lists of search results - one from semantic search and one from keyword search -
    by matching document IDs and computing a weighted combined score.
    It returns the results sorted by the combined score in descending order.

    Args:
        semantic_results (List[Dict[str]]): List of semantic search results. Each item should have keys:
            - "_id": unique document identifier
            - "_score": semantic relevance score (float)
            - "fields": dict containing at least "title" (str) and "url" (str)
        keyword_results (List[Dict[str]]): List of keyword search results. Each item should have keys:
            - "id": unique document identifier
            - "score": keyword relevance score (float)
            - "title": document title (str)
        weight_semantic (float): Weight for semantic scores in the combined score. Defaults to 0.7.
        weight_keyword (float): Weight for keyword scores in the combined score. Defaults to 0.3.

    Returns:
        List[Dict[str, Any]]: Sorted list of combined results, each containing:
            - "question_id": document ID
            - "score": combined weighted score
            - "title": document title
            - "url": document URL
    """

    combined = {}

    for row in semantic_results:
        combined[row["_id"]] = {
            "semantic_score": row["_score"],
            "keyword_score": 0.0,
            "title": row["fields"]["title"],
            "url": row["fields"]["url"],
        }

    for row in keyword_results:
        if row["id"] in combined:
            combined[row["id"]]["keyword_score"] = row["score"]
        else:
            combined[row["id"]] = {
                "semantic_score": 0.0,
                "keyword_score": row["score"],
                "title": row["title"],
                "url": QUESTION_URL.format(row["id"]),
            }

    final_results = []

    for question_id, data in combined.items():
        final_score = weight_semantic * data["semantic_score"] + weight_keyword * data["keyword_score"]
        final_results.append({
            "question_id": question_id,
            "score": final_score,
            "title": data['title'],
            "url": data['url'],
        })
    final_results.sort(key=lambda x: x["score"], reverse=True)
    
    return final_results


if __name__ == '__main__':
    semantic_answer = semantic_search("git")
    print(semantic_answer)
    # # print(semantic_answer.result.hits)

    # keyword_answer = keyword_search("git")
    # # print(keyword_answer)

    # result = combine_results(
    #     semantic_results=semantic_answer.result.hits,
    #     keyword_results=keyword_answer,
    # )
    # print(f'{result}')
    pass
