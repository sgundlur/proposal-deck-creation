# AWS deployment

ECS Fargate behind an ALB. CDK provisions core runtime dependencies. Configure a Bedrock Knowledge Base with an S3 data source containing approved historical proposals, LOPs, case studies and reference storylines.

Production flow: build image -> push ECR -> deploy ECS -> configure Bedrock Knowledge Base -> restrict task IAM -> put Okta/OIDC in front of ALB.