import boto3
from functools import lru_cache
from app.config import settings
@lru_cache
def s3(): return boto3.client("s3",region_name=settings().aws_region)
@lru_cache
def ddb(): return boto3.resource("dynamodb",region_name=settings().aws_region)
@lru_cache
def bedrock(): return boto3.client("bedrock-runtime",region_name=settings().aws_region)
@lru_cache
def agent_runtime(): return boto3.client("bedrock-agent-runtime",region_name=settings().aws_region)
@lru_cache
def textract(): return boto3.client("textract",region_name=settings().aws_region)
