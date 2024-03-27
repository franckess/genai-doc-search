import os, json
import boto3
from aws_lambda_powertools import Logger

DOCUMENT_TABLE = os.environ["DOCUMENT_TABLE"]

ddb = boto3.resource("dynamodb")
document_table = ddb.Table(DOCUMENT_TABLE)
logger = Logger()

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    response = document_table.scan()
    items = sorted(response["Items"], key=lambda item: item["created"], reverse=True)
    logger.info({"items": items})

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
        },
        "body": json.dumps(items, default=str),
    }
