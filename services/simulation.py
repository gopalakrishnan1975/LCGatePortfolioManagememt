from fastapi import FastAPI
from core.models import Scenario
from core.engine import simulate
app=FastAPI(title="LC Queue Simulation",version="1.0")
@app.get("/health")
def health():return {"status":"ok"}
@app.post("/v1/simulate")
def run(s:Scenario):return simulate(s)
