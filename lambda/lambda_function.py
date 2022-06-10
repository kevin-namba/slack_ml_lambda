import json
import boto3

comprehend = boto3.client('comprehend')

def lambda_handler(event, context):
    input_text = "とても美味しいです！"
    #comprehend接続のテスト 
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
    #
    url = "https://slack.com/api/conversations.history" 
    token = "xoxb-3520750066675-3556193162788-Nr7idPBHOrMmqR12ljcT8bME"

    header={
        "Authorization": "Bearer {}".format(token)
    }
    
    payload  = {
        "channel" : "C03EW561RJB"
    }
    
    res = requests.get(url, headers=header, params=payload)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'slack': res.json()
        })
    }