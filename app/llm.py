import json
from app.aws import bedrock,agent_runtime
from app.config import settings
def ask(system,user):
    r=bedrock().converse(modelId=settings().bedrock_model_id,system=[{"text":system}],messages=[{"role":"user","content":[{"text":user}]}],inferenceConfig={"temperature":0.2,"maxTokens":8000})
    return r["output"]["message"]["content"][0]["text"]
def ask_json(system,user): return json.loads(ask(system+"\nReturn ONLY valid JSON.",user))
def retrieve(query):
    if not settings().bedrock_knowledge_base_id:return []
    r=agent_runtime().retrieve(knowledgeBaseId=settings().bedrock_knowledge_base_id,retrievalQuery={"text":query},retrievalConfiguration={"vectorSearchConfiguration":{"numberOfResults":8}})
    return r.get("retrievalResults",[])
