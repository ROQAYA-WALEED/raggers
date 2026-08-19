from fastapi import FastAPI

app = FastAPI(title="Mini RAG API")

@app.get("/")
def root():
    return {"message": "RAG API is running"}
