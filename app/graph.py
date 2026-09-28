import json
from typing import TypedDict
from langgraph.graph import StateGraph,START,END
from app.llm import ask_json,retrieve
class State(TypedDict,total=False): rfp:str; docs:list[str]; refs:list[dict]; requirements:dict; storyline:dict; plan:list[dict]; deck:dict; validation:dict
SYSTEM="""You are an enterprise proposal architect. Ground every claim in supplied material. Never invent customer facts, metrics, certifications, case studies or commitments. Write concise executive-ready content."""
def intake(s): s["refs"]=retrieve("proposal requirements storyline solution architecture case studies\n"+s["rfp"][:12000]); return s
def req(s): s["requirements"]=ask_json(SYSTEM,f'Extract requirements from this RFP. Return client, opportunity, objectives, scope, requirements, constraints, evaluation_criteria as JSON.\n{s["rfp"][:30000]}'); return s
def story(s): s["storyline"]=ask_json(SYSTEM+" Build a factual proposal storyline.",f'Requirements:{json.dumps(s["requirements"])}\nReferences:{json.dumps(s.get("refs",[]),default=str)[:18000]}\nReturn thesis, sections, differentiators, proof_points as JSON.'); return s
def plan(s): s["plan"]=ask_json(SYSTEM,f'Create a 8-15 slide proposal plan from this storyline. Return an array with slide_number,section,title,slide_type,objective,source_refs.\n{json.dumps(s["storyline"])}'); return s
def content(s):
    slides=[]
    for p in s["plan"]:
        c=ask_json(SYSTEM,f'Generate presentation-ready content for this slide. Return headline, subheadline, bullets, key_takeaway, speaker_notes, table, diagram as JSON.\nSlide:{json.dumps(p)}\nRequirements:{json.dumps(s["requirements"])}')
        slides.append({**p,"content":c})
    s["deck"]={"title":s["requirements"].get("opportunity","Proposal"),"theme":{"primary":"1F4E79","accent":"00A3A3","font":"Aptos"},"slides":slides}; return s
def validate(s):
    errors=[]
    for x in s["deck"]["slides"]:
        if len(x["content"].get("bullets",[]))>6: errors.append(f'Slide {x["slide_number"]}: too many bullets')
    s["validation"]={"valid":not errors,"errors":errors}; return s
def build():
    g=StateGraph(State)
    for n,f in [("intake",intake),("requirements",req),("storyline",story),("plan",plan),("content",content),("validate",validate)]:g.add_node(n,f)
    g.add_edge(START,"intake");g.add_edge("intake","requirements");g.add_edge("requirements","storyline");g.add_edge("storyline","plan");g.add_edge("plan","content");g.add_edge("content","validate");g.add_edge("validate",END);return g.compile()
