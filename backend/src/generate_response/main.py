import os, json
import boto3
from aws_lambda_powertools import Logger
from langchain.llms.bedrock import Bedrock
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

MEMORY_TABLE = os.environ["MEMORY_TABLE"]
BUCKET = os.environ["BUCKET"]


s3 = boto3.client("s3")
logger = Logger()


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    event_body = json.loads(event["body"])
    file_name = event_body["fileName"]
    human_input = event_body["prompt"]
    conversation_id = event["pathParameters"]["conversationid"]

    user = event["requestContext"]["authorizer"]["claims"]["sub"]

    s3.download_file(BUCKET, f"{user}/{file_name}/index.faiss", "/tmp/index.faiss")
    s3.download_file(BUCKET, f"{user}/{file_name}/index.pkl", "/tmp/index.pkl")

    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
    )

    embeddings, llm = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v1",
        client=bedrock_runtime,
        region_name="us-east-1",
    ), Bedrock(
        model_id="anthropic.claude-v2", client=bedrock_runtime, region_name="us-east-1", streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()]
    )

    faiss_index = FAISS.load_local("/tmp", embeddings)
    doc_chain = load_qa_chain(llm, chain_type="map_reduce")

    message_history = DynamoDBChatMessageHistory(
        table_name=MEMORY_TABLE, session_id=conversation_id
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
        retriever=faiss_index.as_retriever(),
        memory=memory,
        return_source_documents=True
        )

    try:
        res = qa({"question": human_input})
        logger.info(f'response from llm: {res}')

  
    except Exception as e:
       logger.error(f'Exception: {e}')
    finally:
        buffer = b''
        stopReason = None
        wikiCommand = None
        count=0
        # while (stopReason is None):
        for chunk in res:
            # json_output = json.loads(chunk)
            logger.info(f'chunk: {chunk}')
            # streamData=json.loads(chunk.get('chunk').get('bytes').decode('utf-8'))
            # stopReason=streamData.get('stop_reason')
            # if (stopReason == 'stop' and count == 0):
            #     logger.info("Sorry but I'm not sure about that. Could you please elaborate a little more?")
            # buffer += streamData.get('generation').encode()
            # if (streamData.get('generation') == '```'):
            #     if (wikiCommand is None):
            #         wikiCommand = 'start'
            #     else:
            #         wikiCommand = None
            # if (streamData.get('generation') == '\n' and wikiCommand is None and len(buffer) != 0):
            #     if (buffer.decode('utf-8') != '\n'):
            #         say(buffer.decode('utf-8'))
            #     buffer = b''
            # if(stopReason == 'length'):
            #     say("Sorry, but I ran out of credits to finish my answer...")
            # count+=1
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