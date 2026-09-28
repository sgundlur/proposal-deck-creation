# Proposal Deck Creation

AWS-native RFP / proposal deck generation platform using LangGraph and Amazon Bedrock.

## Architecture

Client/UI -> Application Load Balancer -> FastAPI on ECS Fargate -> LangGraph workflow.

AWS services:
- Amazon S3: RFP/supporting documents, approved templates, renderable manifests and generated PPTX
- Amazon Bedrock Converse: grounded requirement, storyline, planning and slide-content generation
- Amazon Bedrock Knowledge Bases: retrieval from approved historical proposals/LOPs/reference storylines
- Amazon Textract: scanned/complex PDF extraction path
- DynamoDB: proposal job state and metadata
- ECS Fargate + ECR + ALB: application runtime
- CloudWatch Logs: application logs
- AWS CDK: infrastructure as code

## Generation workflow

1. Intake RFP and supporting documents
2. Extract text from PDF/DOCX/PPTX/TXT
3. Retrieve relevant approved reference material
4. Extract requirements and evaluation criteria
5. Build proposal storyline
6. Plan slide sequence and slide types
7. Generate slide-ready content grounded in the RFP/references
8. Validate slide density and schema
9. Render deterministic PPTX with python-pptx
10. Store PPTX and renderable JSON in S3

The design separates LLM decisions/content from deterministic PowerPoint rendering. Validation is a separate step and does not silently rewrite content.

## Repository structure

- `app/main.py` - FastAPI entrypoint and proposal API
- `app/graph.py` - LangGraph orchestration and generation nodes
- `app/llm.py` - Bedrock Converse + Knowledge Base adapters
- `app/extract.py` - document extraction
- `app/ppt.py` - deterministic PPTX renderer
- `app/models.py` - API/domain models
- `app/storage.py` - S3/DynamoDB persistence
- `infra/` - AWS CDK stack
- `docs/` - architecture notes
- `tests/` - automated tests

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
uvicorn app.main:app --reload
```

Generate a deck:

```bash
curl -X POST http://localhost:8000/api/v1/proposals/generate \
  -F "rfp=@rfp.pdf"
```

Then query `/api/v1/proposals/{job_id}` and `/api/v1/proposals/{job_id}/download`.

## AWS deployment

Install the CDK dependencies in `infra/`, bootstrap the target account/region, deploy the stack, push the application image to ECR, and configure `BEDROCK_KNOWLEDGE_BASE_ID` for the approved reference corpus.

Before production exposure, add Okta/OIDC authentication, asynchronous execution (SQS/Step Functions), private networking as required by the organization, tighter IAM resource scoping, and visual PPTX fit validation.

## Grounding rules

The generator must not invent customer facts, metrics, certifications, case studies or commitments. Claims should be traceable to the current RFP or approved reference material. Templates should be approved corporate templates; generated layouts should inherit the approved theme rather than introducing an arbitrary design system.
