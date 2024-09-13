import json
import boto3
from werkzeug.security import check_password_hash
import jwt
import datetime
import random
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('user_table')
user_login_history = dynamodb.Table('user_login_history')
JWT_SECRET = 'sdjosdosdjdmpwonlknjsblsbk22312wdkljdd'  # Replace with a secure key

def lambda_handler(event, context):
    # Extract data from request
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
        if body.get('username') is None or body.get('password') is None:
            return {'statusCode': 400,'headers': headers,'body': f"Missing username, password"}


    username = body['username']
    password = body['password']

    # Retrieve user from DynamoDB
    try:
        response = user_table.scan(
            FilterExpression=Attr('username').eq(username.lower())
        )
        items = response.get('Items', [])
        if not items:
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({"message": "User not found"})
            }
        user = items[0]  # Assuming usernames are unique
        if not user or not check_password_hash(user['password'], password):
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'message': 'Invalid credentials'})
            }

        user_login_his = user_login_history.scan(
            FilterExpression=Attr('user_id').eq(user.get('user_id')) & Attr('is_logged_in').eq(True)
        )
        if len(user_login_his.get("Items")) > 0:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'access_token': user_login_his.get('Items')[0].get("token")})
            }

        # Create JWT token
        token = jwt.encode({'user_id': str(user.get('user_id'))}, JWT_SECRET, algorithm='HS256')
        user_login_history.put_item(
            Item={
                "user_id": user.get('user_id'),
                "user_login_id": random.randint(2, 9000),
                "login_time": datetime.datetime.now().isoformat(),
                "logout_time": None,
                "token": token,
                "is_logged_in": True
            }
        )
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'access_token': token})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'message': 'Error logging in user', 'error': str(e)})
        }
