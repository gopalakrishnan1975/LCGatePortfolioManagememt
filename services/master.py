import json, os
from pathlib import Path
from fastapi import FastAPI
app=FastAPI(title="LC Master Data",version="1.0")
root=Path(os.getenv("MASTER_DIR","master_data"))
@app.get("/health")
def health():return {"status":"ok"}
@app.get("/v1/master/{dataset}")
def get_master(dataset:str):
    from fastapi import HTTPException
    if dataset not in ("lcs","treatments"):raise HTTPException(404,"Unknown dataset")
    return json.loads((root/(dataset+".json")).read_text())
