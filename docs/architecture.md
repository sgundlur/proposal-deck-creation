# Architecture

Client/UI -> ALB -> FastAPI on ECS Fargate. S3 stores inputs, templates and generated decks. Bedrock Knowledge Bases indexes approved reference material. LangGraph orchestrates requirement extraction, storyline, slide planning, content generation and validation. python-pptx performs deterministic rendering.

Future hardening: Okta/OIDC, SQS/Step Functions for asynchronous jobs, human clarification checkpoints, template geometry extraction, visual fit validation and CloudWatch evaluation/observability.