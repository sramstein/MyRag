import argparse
import sys
import uvicorn
from src.config import load_settings
from src.rag_engine import RagEngine

def main():
    parser = argparse.ArgumentParser(description="MyRag CLI - Ingestion, Queries, and Server Runner")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents into the vector store")
    ingest_parser.add_argument("--path", "-p", type=str, default="./data/sample_docs", help="File or directory path")
    ingest_parser.add_argument("--url", "-u", type=str, default=None, help="URL to scrape and ingest")
    ingest_parser.add_argument("--clear", action="store_true", help="Clear existing vectors before ingestion")

    # Query command
    query_parser = subparsers.add_parser("query", help="Ask a question directly via CLI")
    query_parser.add_argument("question", type=str, help="The question to ask")
    query_parser.add_argument("--stream", action="store_true", help="Stream the answer response")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Run the FastAPI server")
    serve_parser.add_argument("--host", type=str, default=None, help="Host to bind")
    serve_parser.add_argument("--port", "-P", type=int, default=None, help="Port to bind")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # Stats command
    subparsers.add_parser("stats", help="Show vector store and model statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    settings = load_settings()

    if args.command == "ingest":
        engine = RagEngine(settings)
        if args.url:
            print(f"📥 Ingesting URL: {args.url} ...")
            res = engine.ingest_url(args.url)
        else:
            print(f"📥 Ingesting path: {args.path} (clear={args.clear}) ...")
            res = engine.ingest_path(args.path, clear_existing=args.clear)
        print("✅ Result:", res)

    elif args.command == "query":
        engine = RagEngine(settings)
        print(f"\n💬 Question: {args.question}\n" + "-" * 50)
        if args.stream:
            print("🤖 Answer: ", end="", flush=True)
            for chunk in engine.query_stream(args.question):
                print(chunk, end="", flush=True)
            print("\n")
        else:
            res = engine.query(args.question)
            print(f"🤖 Answer:\n{res['answer']}\n")
            if res.get("sources"):
                print("📚 Sources:")
                for s in res["sources"]:
                    print(f"  • {s['title']} (Score: {s['score']}) - {s['source']}")

    elif args.command == "stats":
        engine = RagEngine(settings)
        stats = engine.get_stats()
        print("\n📊 RAG Engine Statistics:")
        for k, v in stats.items():
            print(f"  {k}: {v}")

    elif args.command == "serve":
        host = args.host or settings.app.host
        port = args.port or settings.app.port
        print(f"🚀 Starting MyRag Server on http://{host}:{port}")
        uvicorn.run("src.api:app", host=host, port=port, reload=args.reload)

if __name__ == "__main__":
    main()
