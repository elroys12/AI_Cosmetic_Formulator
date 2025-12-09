# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from ai_pipeline import run_ai

app = FastAPI()

class QueryIn(BaseModel):
    topic: str

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/ai/analyze")
def analyze(req: QueryIn):
    result = run_ai(req.topic)
    return {"result": str(result)}
