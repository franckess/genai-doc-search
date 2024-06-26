import os, json
from datetime import datetime
import boto3
import shortuuid
from aws_lambda_powertools import Logger

CONVERSATION_TABLE = os.environ["CONVERSATION_TABLE"]
CONVERSATION_HISTORY_TABLE = os.environ["CONVERSATION_HISTORY_TABLE"]

ddb = boto3.resource("dynamodb")
conversation_table = ddb.Table(CONVERSATION_TABLE)
conversation_history_table = ddb.Table(CONVERSATION_HISTORY_TABLE)
logger = Logger()

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
    conversation_id = shortuuid.uuid()
    timestamp = datetime.utcnow()
    timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    conversation_table.put_item(Item={
        "userid": user_id,
        "conversationid": conversation_id,
        "created": timestamp_str,
    })

    conversation_history_table.put_item(Item={
        "UserId": user_id,
        "ConversationId": conversation_id,
        "History": []
    })

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
        },
        "body": json.dumps({"conversationid": conversation_id}),
    }
