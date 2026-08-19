import argparse
from ingestion.ingest import run_ingestion
import uvicorn

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest", action="store_true", help="Run ingestion pipeline")
    parser.add_argument("--api", action="store_true", help="Start API server")
    args = parser.parse_args()

    if args.ingest:
        run_ingestion()
    elif args.api:
        from api.routes import router
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("Specify --ingest or --api")

if __name__ == "__main__":
    main()