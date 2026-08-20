import argparse
import uvicorn
from fastapi import FastAPI
from .ingestion.ingest import run_ingestion
from .api.routes import router

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest", action="store_true", help="Run ingestion pipeline")
    parser.add_argument("--api", action="store_true", help="Start API server")
    args = parser.parse_args()

    if args.ingest:
        run_ingestion()
    elif args.api:
        app = FastAPI()
        app.include_router(router)
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("Specify --ingest or --api")

if __name__ == "__main__":
    main()