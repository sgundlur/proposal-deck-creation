from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    aws_region:str="eu-west-1"; s3_bucket:str; bedrock_knowledge_base_id:str|None=None
    bedrock_model_id:str="amazon.nova-pro-v1:0"; dynamodb_jobs_table:str="proposal-deck-jobs"; max_upload_mb:int=50
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
@lru_cache
def settings(): return Settings()
