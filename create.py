import requests
import os
import time
import logging
import json
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Fields to fetch from the API
fields_to_fetch = (
    "title,url,paperId,citationCount,publicationDate,authors,"
    "references.title,references.url,references.paperId,"
    "references.citationCount,references.publicationDate,references.authors,"
    "citations.title,citations.url,citations.paperId,"
    "citations.citationCount,citations.publicationDate,citations.authors"
)


def make_api_call(url, headers, params=None, max_retries=3):
    """
    Make an API call with retry logic.

    Args:
        url (str): The API endpoint URL.
        headers (dict): Headers to include in the request.
        params (dict, optional): Query parameters to include in the request. Defaults to None.
        max_retries (int, optional): Maximum number of retries in case of failure. Defaults to 3.

    Returns:
        dict: The JSON response from the API, or None if the request fails.
    """
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            logging.warning(
                f"Attempt {attempt + 1}/{max_retries} - Error {response.status_code}: {response.text}"
            )
            time.sleep(2)

    logging.error(f"Failed to get a successful response after {max_retries} attempts")
    return None


def search_semantic_scholar(query, api_key, limit=100, offset=0):
    """
    Search for papers using the Semantic Scholar API.

    Args:
        query (str): The search query.
        api_key (str): API key for authentication.
        limit (int, optional): Number of results to fetch per request. Defaults to 100.
        offset (int, optional): Offset for pagination. Defaults to 0.

    Returns:
        dict: The JSON response containing search results.
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {"x-api-key": api_key}
    params = {
        "query": query,
        "fields": fields_to_fetch,
        "limit": limit,
        "offset": offset,
    }
    return make_api_call(url, headers, params)


def fetch_papers(query, api_key, total_papers, title):
    """
    Fetch a specified number of papers based on a search query.

    Args:
        query (str): The search query.
        api_key (str): API key for authentication.
        total_papers (int): Total number of papers to fetch.
        title (str): Title of the research.

    Returns:
        list: A list of fetched paper data.
    """
    all_papers = []
    limit = 100
    offset = 0
    request_count = 0

    while len(all_papers) < total_papers:
        data = search_semantic_scholar(query, api_key, limit=limit, offset=offset)
        request_count += 1

        if data:
            papers = data.get("data", [])
            if not papers:
                break
            for paper in papers:
                paper["queries"] = [query]
            all_papers.extend(papers)
            offset += limit
            logging.info(
                f"[{title}] Fetched {len(papers)} papers. Total so far: {len(all_papers)}. Total requests: {request_count}"
            )
            time.sleep(1)
        else:
            break

    logging.info(f"[{title}] Total requests made: {request_count}")
    return all_papers[:total_papers]


def main(args):
    # Load environment variables from .env file
    load_dotenv()
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    if not api_key:
        logging.error(
            "API key for Semantic Scholar not found. Make sure it is set in the .env file."
        )
        return

    queries = args.queries.split(",")
    total_papers = args.total_papers
    title = args.title

    output_file = f"{title.replace(' ', '_')}.json"

    logging.info(f"[{title}] Starting paper search...")

    papers = []

    # Process each query
    for query_idx, query in enumerate(queries):
        query = query.strip()
        logging.info(
            f"[{title}] Processing query ({query_idx + 1}/{len(queries)}): '{query}'"
        )
        papers.extend(fetch_papers(query, api_key, total_papers, title))

    logging.info(
        f"[{title}] Total papers fetched before removing duplicates: {len(papers)}"
    )

    # Remove duplicates and merge queries
    papers_dict = {}
    for paper in papers:
        paper_id = paper["paperId"]
        if paper_id in papers_dict:
            papers_dict[paper_id]["queries"].extend(paper["queries"])
            papers_dict[paper_id]["queries"] = list(
                set(papers_dict[paper_id]["queries"])
            )
        else:
            papers_dict[paper_id] = paper

    papers = list(papers_dict.values())
    logging.info(
        f"[{title}] Total unique papers after removing duplicates: {len(papers)}"
    )

    with open(output_file, "w") as f:
        json.dump(papers, f, indent=4)

    logging.info(f"[{title}] JSON generated and saved successfully as '{output_file}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch and save research papers from Semantic Scholar."
    )
    parser.add_argument(
        "--queries",
        type=str,
        required=True,
        help="Comma-separated list of search queries.",
    )
    parser.add_argument(
        "--total_papers",
        type=int,
        required=True,
        help="Total number of papers to fetch for each query.",
    )
    parser.add_argument(
        "--title", type=str, required=True, help="Title for the research."
    )

    args = parser.parse_args()
    main(args)
