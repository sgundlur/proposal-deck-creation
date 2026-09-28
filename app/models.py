from datetime import datetime,timezone
from enum import StrEnum
from pydantic import BaseModel,Field
class JobStatus(StrEnum): CREATED="created"; RUNNING="running"; COMPLETED="completed"; FAILED="failed"
class SourceDocument(BaseModel): name:str; s3_key:str; content_type:str; extracted_text:str=""
class SlideSpec(BaseModel): slide_number:int; section:str; title:str; slide_type:str; objective:str; source_refs:list[str]=[]; content:dict={}
class RenderableDeck(BaseModel): title:str; theme:dict={}; slides:list[SlideSpec]
class ProposalJob(BaseModel):
    job_id:str; status:JobStatus; created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc)); rfp:SourceDocument
    supporting_documents:list[SourceDocument]=[]; storyline:dict={}; deck:RenderableDeck|None=None; output_s3_key:str|None=None; manifest_s3_key:str|None=None; error:str|None=None
