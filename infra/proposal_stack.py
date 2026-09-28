from aws_cdk import Stack,CfnOutput,Duration,RemovalPolicy,aws_dynamodb as dynamodb,aws_ec2 as ec2,aws_ecs as ecs,aws_ecr as ecr,aws_elasticloadbalancingv2 as elbv2,aws_iam as iam,aws_logs as logs,aws_s3 as s3
from constructs import Construct
class ProposalDeckStack(Stack):
 def __init__(self,scope:Construct,id:str,**kw):
  super().__init__(scope,id,**kw)
  bucket=s3.Bucket(self,"Artifacts",encryption=s3.BucketEncryption.S3_MANAGED,block_public_access=s3.BlockPublicAccess.BLOCK_ALL,versioned=True,removal_policy=RemovalPolicy.RETAIN)
  jobs=dynamodb.Table(self,"Jobs",partition_key=dynamodb.Attribute(name="job_id",type=dynamodb.AttributeType.STRING),billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,point_in_time_recovery=True,removal_policy=RemovalPolicy.RETAIN)
  vpc=ec2.Vpc(self,"Vpc",max_azs=2,nat_gateways=1); cluster=ecs.Cluster(self,"Cluster",vpc=vpc); repo=ecr.Repository(self,"Repository",image_scan_on_push=True)
  log_group=logs.LogGroup(self,"Logs",retention=logs.RetentionDays.ONE_MONTH,removal_policy=RemovalPolicy.RETAIN)
  role=iam.Role(self,"TaskRole",assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")); bucket.grant_read_write(role); jobs.grant_read_write_data(role)
  role.add_to_policy(iam.PolicyStatement(actions=["bedrock:InvokeModel","bedrock:Retrieve","textract:StartDocumentTextDetection","textract:GetDocumentTextDetection"],resources=["*"]))
  td=ecs.FargateTaskDefinition(self,"Task",cpu=1024,memory_limit_mib=2048,task_role=role)
  c=td.add_container("Api",image=ecs.ContainerImage.from_ecr_repository(repo,"latest"),logging=ecs.LogDrivers.aws_logs(stream_prefix="proposal",log_group=log_group),environment={"AWS_REGION":self.region,"S3_BUCKET":bucket.bucket_name,"DYNAMODB_JOBS_TABLE":jobs.table_name}); c.add_port_mappings(ecs.PortMapping(container_port=8000))
  svc=ecs.FargateService(self,"Service",cluster=cluster,task_definition=td,desired_count=1,assign_public_ip=False)
  alb=elbv2.ApplicationLoadBalancer(self,"Alb",vpc=vpc,internet_facing=True); listener=alb.add_listener("Http",port=80); listener.add_targets("Api",port=8000,targets=[svc],health_check=elbv2.HealthCheck(path="/health",interval=Duration.seconds(30)))
  CfnOutput(self,"ApiUrl",value=f"http://{alb.load_balancer_dns_name}"); CfnOutput(self,"Bucket",value=bucket.bucket_name); CfnOutput(self,"Ecr",value=repo.repository_uri)
