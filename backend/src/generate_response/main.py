import os, json
import boto3
from aws_lambda_powertools import Logger
from langchain.llms.bedrock import Bedrock
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever

CONVERSATION_HISTORY_TABLE = os.environ["CONVERSATION_HISTORY_TABLE"]
KNOWLEDGE_BASE_DETAILS_SSM_PATH = os.environ["KNOWLEDGE_BASE_DETAILS_SSM_PATH"]

s3 = boto3.client("s3")
ssm = boto3.client('ssm')
logger = Logger()

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    event_body = json.loads(event["body"])
    human_input = event_body["prompt"]
    conversation_id = event["pathParameters"]["conversationid"]
    user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
    param_response = ssm.get_parameter(Name=KNOWLEDGE_BASE_DETAILS_SSM_PATH)
    knowledge_base_details = json.loads(param_response['Parameter']['Value'])

    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
    )

    llm = Bedrock(
        model_id="anthropic.claude-v2", client=bedrock_runtime, region_name="us-east-1", streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()]
    )

    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=knowledge_base_details["knowledgeBaseId"],
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )

    message_history = DynamoDBChatMessageHistory(
        table_name=CONVERSATION_HISTORY_TABLE,
        session_id=conversation_id, # Not used if key provided but still required
        key={ "UserId": user_id, "ConversationId": conversation_id },
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=message_history,
        input_key="question",
        output_key="answer",
        return_messages=True,
    )

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )

    try:
        res = qa({"question": human_input})
        logger.info(f'response from llm: {res}')

        return {
            "statusCode": 200,
            "headers": {
               "Content-Type": "application/json",
               "Access-Control-Allow-Headers": "*",
               "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
            },
            "body": json.dumps(res["answer"]),
        }

    except Exception as e:
       logger.error(f'Exception: {e}')
       raise e
