# import boto3
import json
import logging

import requests
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def lambda_handler(event, context):

    ### get request
    # USER_TOKEN = 'xoxp-3520750066675-3514126860774-3577573220384-e8db3feed159abbd81e967571ffa9e28'
    # BOT_TOKEN = 'xoxb-3520750066675-3556193162788-Nr7idPBHOrMmqR12ljcT8bME'
    # CHANNEL_NAME = "授業"
    BOT_TOKEN = event["bot_token"]
    CHANNEL_NAME = event["channel_name"]

    ### get slack log
    # WebClient instantiates a client that can call API methods
    # When using Bolt, you can use either `app.client` or the `client` passed to listeners.
    client = WebClient(token=BOT_TOKEN)
    logger = logging.getLogger(__name__)

    # get channel id
    channel_id = None
    try:
        # Call the conversations.list method using the WebClient
        for result in client.conversations_list():
            if channel_id is not None:
                break
            for channel in result["channels"]:
                if channel["name"] == CHANNEL_NAME:
                    channel_id = channel["id"]
                    #Print result
                    print(f"Found conversation ID: {channel_id}")
                    break
    except SlackApiError as e:
        print(f"Error: {e}")
        # TODO: error handling
    
    if channel_id is None:
        print(f"Error: No such channel: {CHANNEL_NAME}")
        # TODO: error handling
        return
    
    # Store conversation history
    conversation_history = []
    try:
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        conversation_history = client.conversations_history(channel=channel_id)["messages"]
        # logger.info("{} messages found in {}".format(len(conversation_history), id))

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
    
    return conversation_history

    # comprehend client
    # comprehend = boto3.client('comprehend')

    ### comprehend接続のテスト 
    # input_text = "とても美味しいです！"
    # response = comprehend.detect_sentiment(
    #     Text='input_text',
    #     LanguageCode='ja'
    # )    
    # sentiment_score = response.get('SentimentScore')
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps({
    #         'sentiment_score': sentiment_score
    #     })
    # }

# if __name__ == "__main__":
#     res = lambda_handler(None, None)
#     print(res)