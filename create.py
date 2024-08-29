from flask import Flask, request, render_template, Response, jsonify
from flask_socketio import SocketIO, emit
import os
import time
import logging
import json
from dotenv import load_dotenv
import requests
from collections import defaultdict

app = Flask(__name__)
socketio = SocketIO(app)

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


def log_message(message):
    """
    Logs a message by emitting it through the socketio connection.

    Args:
        message (str): The message to be logged.
    """
    socketio.emit("log_message", {"message": message})


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
            log_message(
                f"Attempt {attempt + 1}/{max_retries} - Error {response.status_code}: {response.text}"
            )
            time.sleep(2)

    log_message(f"Failed to get a successful response after {max_retries} attempts")
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
            all_papers.extend(papers)
            offset += limit
            log_message(
                f"[{title}] Fetched {len(papers)} papers. Total so far: {len(all_papers)}. Total requests: {request_count}"
            )
            time.sleep(1)
        else:
            break

    log_message(f"[{title}] Total requests made: {request_count}")
    return all_papers[:total_papers]


def generate_json(queries, total_papers, title):
    """
    Generate a JSON string containing information about fetched papers.

    Args:
        queries (list): A list of queries to fetch papers for.
        total_papers (int): The maximum number of papers to fetch for each query.
        title (str): The title of the process.

    Returns:
        str: A JSON string containing information about the fetched papers.
    """
    load_dotenv()
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    if not api_key:
        log_message(
            "API key for Semantic Scholar not found. Make sure it is set in the .env file."
        )
        return None

    papers_dict = {}
    queries_data = defaultdict(list)
    queries_data_more = defaultdict(list)
    paper_data = {}
    links_data = []
    authors_data = {}

    for query_idx, query in enumerate(queries):
        query = query.strip()
        log_message(
            f"[{title}] Processing query ({query_idx + 1}/{len(queries)}): '{query}'"
        )
        query_papers = fetch_papers(query, api_key, total_papers, title)
        for paper in query_papers:
            paper_id = paper["paperId"]
            if paper_id not in papers_dict:
                papers_dict[paper_id] = paper
                paper_data[paper["paperId"]] = {
                    "paperId": paper["paperId"],
                    "title": paper["title"],
                    "url": paper["url"],
                    "citationCount": paper["citationCount"],
                    "publicationDate": paper["publicationDate"],
                    "authorIds": [author["authorId"] for author in paper["authors"]],
                }

                for author in paper["authors"]:
                    authors_data[author["authorId"]] = author["name"]

                for ref in paper.get("references", []):
                    links_data.append(
                        {"source": paper["paperId"], "target": ref["paperId"]}
                    )
                    paper_data[ref["paperId"]] = {
                        "paperId": ref["paperId"],
                        "title": ref["title"],
                        "url": ref["url"],
                        "citationCount": ref["citationCount"],
                        "publicationDate": ref["publicationDate"],
                        "authorIds": [author["authorId"] for author in ref["authors"]],
                    }
                    for author in ref["authors"]:
                        authors_data[author["authorId"]] = author["name"]
                    if ref["paperId"] not in queries_data_more[query]:
                        queries_data_more[query].append(ref["paperId"])

                for cite in paper.get("citations", []):
                    links_data.append(
                        {"source": cite["paperId"], "target": paper["paperId"]}
                    )
                    paper_data[cite["paperId"]] = {
                        "paperId": cite["paperId"],
                        "title": cite["title"],
                        "url": cite["url"],
                        "citationCount": cite["citationCount"],
                        "publicationDate": cite["publicationDate"],
                        "authorIds": [author["authorId"] for author in cite["authors"]],
                    }
                    for author in cite["authors"]:
                        authors_data[author["authorId"]] = author["name"]
                    if cite["paperId"] not in queries_data_more[query]:
                        queries_data_more[query].append(cite["paperId"])

            queries_data[query].append(paper_id)
            queries_data_more[query].append(paper_id)

    log_message(
        f"[{title}] Total unique papers after removing duplicates: {len(paper_data)}"
    )

    result = {
        "title": title.replace(" ", "_"),
        "papers": list(paper_data.values()),
        "links": links_data,
        "queries": queries_data,
        "queries_more": queries_data_more,
        "authors": authors_data,
    }
    return json.dumps(result, indent=4)


@app.route("/")
def index():
    """
    Renders the index.html template.

    Returns:
        The rendered index.html template.
    """
    return render_template("index.html")


@app.route("/generate_json", methods=["POST"])
def generate_json_route():
    """
    Generate JSON route handler.

    This function handles the route for generating JSON data based on the provided queries,
    total number of papers, and title.

    Returns:
        If JSON data is successfully generated, it returns a JSON response with the generated data.
        If JSON data generation fails, it returns a JSON response with an error message and a status code of 500.
    """
    queries = request.form["queries"].split(",")
    total_papers = int(request.form["total_papers"])
    title = request.form["title"]
    json_data = generate_json(queries, total_papers, title)
    if json_data:
        return jsonify({"json_data": json_data})
    else:
        return jsonify({"error": "Failed to generate JSON"}), 500


@app.route("/download_json", methods=["POST"])
def download_json():
    """
    Downloads the JSON data as a file.

    This function retrieves the JSON data from the request form and returns it as a response with the appropriate headers for downloading.

    Returns:
        Response: The response object containing the JSON data as a file.
    """
    content = request.form["jsonval"]
    filename = request.args.get("filename", "data.json")
    return Response(
        content,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename={filename}"},
    )


if __name__ == "__main__":
    socketio.run(app, debug=True)
