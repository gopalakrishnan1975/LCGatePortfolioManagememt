import os, httpx
from fastapi import FastAPI, HTTPException
from core.models import Scenario
from core.engine import appraise
app=FastAPI(title="LC Appraisal",version="1.0")
@app.get("/health")
def health():return {"status":"ok"}
@app.post("/v1/appraise")
def run(s:Scenario):
    try:
        response=httpx.post(os.getenv("SIM_URL","http://localhost:8002")+"/v1/simulate",json=s.model_dump(),timeout=45)
        response.raise_for_status()
    except httpx.HTTPError as e:raise HTTPException(503,"Simulation service unavailable") from e
    result=response.json()
    return {"simulation":result,"appraisal":appraise(s,result),"model_version":"1.0","input":s.model_dump()}
