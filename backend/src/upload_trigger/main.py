import os, json
from datetime import datetime
import boto3
import PyPDF2
import shortuuid
import urllib
from aws_lambda_powertools import Logger
import json

DOCUMENT_TABLE = os.environ["DOCUMENT_TABLE"]
BUCKET = os.environ["BUCKET"]
KNOWLEDGE_BASE_DETAILS_SSM_PATH = os.environ["KNOWLEDGE_BASE_DETAILS_SSM_PATH"]

ddb = boto3.resource("dynamodb")
bedrock = boto3.client('bedrock-agent')
document_table = ddb.Table(DOCUMENT_TABLE)
s3 = boto3.client("s3")
ssm = boto3.client('ssm')
logger = Logger()


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    print(key)  
    split = key.split("/")
    user_id = split[0]
    file_name = split[1]
    document_id = shortuuid.uuid()

    s3.download_file(BUCKET, key, f"/tmp/{file_name}")

    with open(f"/tmp/{file_name}", "rb") as f:
        reader = PyPDF2.PdfReader(f)
        pages = str(len(reader.pages))

    timestamp = datetime.utcnow()
    timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    document = {
        "userid": user_id,
        "documentid": document_id,
        "filename": file_name,
        "created": timestamp_str,
        "pages": pages,
        "filesize": str(event["Records"][0]["s3"]["object"]["size"]),
    }

    document_table.put_item(Item=document)

    # Simplistically trigger ingestion job. This does not cater
    # for situations were a job is already running or how to avoid unecessarily 
    # triggering jobs if multiple documents are uploaded in quick succession etc

    param_response = ssm.get_parameter(Name=KNOWLEDGE_BASE_DETAILS_SSM_PATH)
    knowledge_base_details = json.loads(param_response['Parameter']['Value'])

    try:
        bedrock.start_ingestion_job(
            knowledgeBaseId=knowledge_base_details['knowledgeBaseId'],
            dataSourceId=knowledge_base_details['dataSourceId'],
            userId=user_id
        )
    except Exception as e:
        logger.error(f'Error triggering bedrock knowledge base sync: {e}')
