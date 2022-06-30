import boto3
import json
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


BUCKET_NAME = ""
COMPREHEND_ACCESS_ARN = ""


def get_slack_history(bot_token, channel_name):
    """
    Get slack conversation history.
    Upload data to s3 in two type.
     - input text for comprehend
     - data which contains metadata per user
    """

    # WebClient instantiates a client that can call API methods
    # When using Bolt, you can use either `app.client` or the `client` passed to listeners.
    client = WebClient(token=bot_token)

    ### Get channel id
    channel_id = None
    try:
        # Call the conversations.list method using the WebClient
        for result in client.conversations_list():
            if channel_id is not None:
                break
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    channel_id = channel["id"]
                    print(f"Found conversation ID: {channel_id}")
                    break
    except SlackApiError as e:
        print(f"Error: {e}")
        # TODO: error handling

    if channel_id is None:
        print(f"Error: No such channel: {channel_name}")
        # TODO: error handling
        return
    
    ### Get conversation history
    conversation_history = []
    try:
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        conversation_history = client.conversations_history(channel=channel_id, limit=1000)["messages"]
    except SlackApiError as e:
        print("Error creating conversation: {}".format(e))
    
    ### split conversation history per user
    users_list = client.users_list()["members"]
    data = {}
    for user in users_list:
        data[user["id"]] = []
    for line in conversation_history:
        u =  line["user"]
        t = line["text"].replace("\n", " ")
        data[u].append(t)
    for user in users_list:
        file_name = "/tmp/" + user["id"] + "/input.txt"
        if not os.path.exists("/tmp/" + user["id"]):
            os.mkdir("/tmp/" + user["id"])
        with open(file_name, mode='w') as f:
            for item in data[user["id"]]:
                f.write(item)
                f.write("\n")
            f.close()
    print(os.listdir("/tmp"))
            
    ### Upload input text
    s3 = boto3.resource('s3')
    s3_filename_list = []
    for user in users_list:
        local_filename = "/tmp/" + user["id"] + "/input.txt"
        s3_filename = bot_token + "/" + channel_id + "/" + user["id"] + "/input.txt"
        s3.meta.client.upload_file(local_filename, BUCKET_NAME, s3_filename)
        s3_filename_list.append(s3_filename)
    
    return s3_filename_list


def request_analysis(input_filename):
    
    comprehend = boto3.client('comprehend')
    
    job_name = "MachineIntelligence-" + input_filename
    input_s3URI = "s3://" + BUCKET_NAME + "/" + input_filename
    output_s3URI = input_s3URI[:-10]
    
    comprehend.start_sentiment_detection_job(
        DataAccessRoleArn=COMPREHEND_ACCESS_ARN,
        InputDataConfig={
            'S3Uri': input_s3URI,
            'InputFormat': 'ONE_DOC_PER_LINE',
        },
        OutputDataConfig={
            'S3Uri': output_s3URI,
        },
        JobName=job_name,
        LanguageCode='ja'
    )


def lambda_handler(event, context):

    ### get request body
    BOT_TOKEN = event["bot_token"]
    CHANNEL_NAME = event["channel_name"]

    input_filename_list = get_slack_history(BOT_TOKEN, CHANNEL_NAME)
    for input_filename in input_filename_list:
        request_analysis(input_filename)
    
    
    return input_filename_list