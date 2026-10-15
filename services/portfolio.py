from fastapi import FastAPI, HTTPException
from core.models import Portfolio
from core.engine import optimize
app=FastAPI(title="LC Portfolio",version="1.0")
@app.get("/health")
def health():return {"status":"ok"}
@app.post("/v1/optimize")
def run(p:Portfolio):
    try:return optimize(p)
    except ValueError as e:raise HTTPException(422,str(e)) from e
