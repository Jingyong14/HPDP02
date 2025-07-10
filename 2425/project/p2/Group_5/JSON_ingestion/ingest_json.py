# DO NOT run this file in your docker folder to avoid confusion between Docker and Python environment
# This program is only to save time for scraping 20000 articles
# To RUN : python ingest_json.py news_articles_batch_uncleaned.json
import argparse
import json
import sys
from elasticsearch import Elasticsearch, helpers, NotFoundError

ES_HOST  = "http://localhost:9200"
ES_INDEX = "news_articles_batch_uncleaned"

def delete_index(es: Elasticsearch):
    try:
        es.indices.delete(index=ES_INDEX)
        print(f"Deleted existing index '{ES_INDEX}'.")
    except NotFoundError:
        print(f"No existing index '{ES_INDEX}' to delete.")

def create_index(es: Elasticsearch):
    es.indices.create(index=ES_INDEX)
    print(f"Created index '{ES_INDEX}'.")

def load_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON root must be an array of objects")
    return data

def prepare_actions(docs):
    for doc in docs:
        title = doc.get("title")
        desc  = doc.get("description")
        if title is None or desc is None:
            # skip if either field is missing
            continue
        yield {
            "_index": ES_INDEX,
            "_source": {
                "title": title,
                "description": desc
            }
        }

def bulk_index(es: Elasticsearch, actions):
    success, _ = helpers.bulk(es, actions)
    print(f"Indexed {success} documents into '{ES_INDEX}'.")

def main():
    parser = argparse.ArgumentParser(
        description="Ingest a JSON file into Elasticsearch (news_articles index)."
    )
    parser.add_argument(
        "json_file",
        help="Path to the JSON file (must be a top-level array of objects)."
    )
    parser.add_argument(
        "--es-host",
        default=ES_HOST,
        help=f"Elasticsearch host URL (default: {ES_HOST})"
    )
    args = parser.parse_args()

    es = Elasticsearch(args.es_host)
    if not es.ping():
        print(f"ERROR: Cannot connect to Elasticsearch at {args.es_host}", file=sys.stderr)
        sys.exit(1)

    delete_index(es)
    create_index(es)

    try:
        docs = load_json(args.json_file)
    except Exception as e:
        print(f"ERROR loading JSON: {e}", file=sys.stderr)
        sys.exit(1)

    actions = prepare_actions(docs)
    bulk_index(es, actions)

if __name__ == "__main__":
    main()
