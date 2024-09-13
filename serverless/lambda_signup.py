import json
import boto3
from werkzeug.security import generate_password_hash
import random
from boto3.dynamodb.conditions import Attr  # Import Attr for filter expressions


dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('user_table')

def lambda_handler(event, context):
    headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'}
    http_method = event.get('requestContext', {}).get('http', {}).get('method', None)
    if isinstance(event,(str,)):
        body = json.loads(event)
    else:
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body= event
    if http_method == 'OPTIONS':
        return {'statusCode': 200,'headers': headers,'body': f""}        
    elif http_method is None:
        if body.get('username') is None or body.get('password') is None or body.get('email') is None:
            return {'statusCode': 400,'headers': headers,'body': f"Missing username, password or email"}

    
    username = body['username']
    password = body['password']
    email = body['email']

    response = user_table.scan(
            FilterExpression=Attr('username').eq(username.lower())
        )
    items = response.get('Items', [])
    if len(items) > 0:
        return {"statusCode": 404, 'headers': {'Content-Type': 'application/json'},
        "body": json.dumps({"message": "Username Already used, use different username"})}
    hashed_password = generate_password_hash(password)
    
    user_table.put_item(
        Item={
            'user_id':  random.randint(2, 1000),
            'username': username.lower(),
            'password': hashed_password,
            'email': email
        }
    )
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'User registered successfully'})
    }
