import boto3
import json
AWS_ACCESS_KEY = "AKIAY6MI7NBZ6EVPEWOD"
AWS_SECRET_ACCESS_KEY = "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"

boto3Session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
dynamoClient = boto3Session.resource('dynamodb')
table = dynamoClient.Table('trinityTable')

data = ""
with open('student_data.json', 'r') as file:
    data = json.load(file)

for i in data:
    print(i)
    response = table.put_item(Item = i)