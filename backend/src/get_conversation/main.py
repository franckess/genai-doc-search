import os, json
import boto3
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
    conversation_id = event["pathParameters"]["conversationid"]

    response = conversation_table.get_item(
        Key={"userid": user_id, "conversationid": conversation_id}
    )

    history_response = conversation_history_table.get_item(
        Key={"UserId": user_id, "ConversationId": conversation_id}
    )

    item = response["Item"]
    history_item = history_response["Item"]

    conversation = {
        "userid": item["userid"],
        "conversationid": item["conversationid"],
        "created": item["created"],
        "messages": history_item["History"]
    }
    logger.info({"conversation": conversation})

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
        },
        "body": json.dumps(
            {
                "conversation": conversation,
            },
            default=str
        ),
    }
