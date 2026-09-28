import json,uuid
from app.aws import s3,ddb
from app.config import settings
def put(key,data,content_type): s3().put_object(Bucket=settings().s3_bucket,Key=key,Body=data,ContentType=content_type); return key
def put_json(key,value): return put(key,json.dumps(value,indent=2,ensure_ascii=False).encode(),"application/json")
def presign(key): return s3().generate_presigned_url("get_object",Params={"Bucket":settings().s3_bucket,"Key":key},ExpiresIn=900)
def new_id(): return uuid.uuid4().hex
def table(): return ddb().Table(settings().dynamodb_jobs_table)
