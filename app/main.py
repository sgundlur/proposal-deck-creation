import os,tempfile
from fastapi import FastAPI,UploadFile,File,HTTPException
from app.config import settings
from app.models import *
from app.storage import *
from app.extract import extract
from app.graph import build
from app.ppt import render
app=FastAPI(title="Proposal Deck Creation API",version="0.1.0")
def save(job):table().put_item(Item=job.model_dump(mode="json"))
def load(id):
 r=table().get_item(Key={"job_id":id}).get("Item");return ProposalJob.model_validate(r) if r else None
@app.get("/health")
def health():return {"status":"ok"}
@app.post("/api/v1/proposals/generate",response_model=ProposalJob)
async def generate(rfp:UploadFile=File(...),supporting_files:list[UploadFile]|None=File(None)):
 id=new_id(); prefix=f"jobs/{id}/input";data=await rfp.read();key=f"{prefix}/{rfp.filename}";put(key,data,rfp.content_type or "application/octet-stream");rd=SourceDocument(name=rfp.filename or "rfp",s3_key=key,content_type=rfp.content_type or "",extracted_text=extract(data,rfp.filename or ""));docs=[]
 for f in supporting_files or []:
  d=await f.read();k=f"{prefix}/{f.filename}";put(k,d,f.content_type or "application/octet-stream");docs.append(SourceDocument(name=f.filename or "support",s3_key=k,content_type=f.content_type or "",extracted_text=extract(d,f.filename or "")))
 job=ProposalJob(job_id=id,status=JobStatus.RUNNING,rfp=rd,supporting_documents=docs);save(job)
 try:
  result=build().invoke({"rfp":rd.extracted_text,"docs":[d.extracted_text for d in docs]})
  with tempfile.TemporaryDirectory() as t:
   p=render(result["deck"],os.path.join(t,"proposal.pptx"));out=f"jobs/{id}/output/proposal.pptx";put(out,open(p,"rb").read(),"application/vnd.openxmlformats-officedocument.presentationml.presentation")
  manifest=f"jobs/{id}/output/renderable.json";put_json(manifest,result["deck"]);job.status=JobStatus.COMPLETED;job.storyline=result["storyline"];job.output_s3_key=out;job.manifest_s3_key=manifest;save(job)
 except Exception as e: job.status=JobStatus.FAILED;job.error=str(e);save(job)
 return job
@app.get("/api/v1/proposals/{job_id}",response_model=ProposalJob)
def status(job_id):
 j=load(job_id)
 if not j:raise HTTPException(404,"Job not found")
 return j
@app.get("/api/v1/proposals/{job_id}/download")
def download(job_id):
 j=load(job_id)
 if not j or not j.output_s3_key:raise HTTPException(404,"Deck unavailable")
 return {"url":presign(j.output_s3_key)}
