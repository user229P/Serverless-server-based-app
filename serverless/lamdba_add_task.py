import json
import boto3
import jwt
import random

dynamodb = boto3.resource('dynamodb')
task_table = dynamodb.Table('user_task')
user_table = dynamodb.Table('user_table')
user_login_history = dynamodb.Table('user_login_history')
JWT_SECRET = 'sdjosdosdjdmpwonlknjsblsbk22312wdkljdd'

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
        if body.get('token') is None :
            return {'statusCode': 400,'headers': headers,'body': f"Missing token"}


    try:
        token = body.get('token')
        # Verify token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = decoded_token.get('user_id')

        # Check if user exists
        response = user_table.get_item(Key={'user_id': int(user_id)})
        user = response.get('Item')
        if not user:
            return {'statusCode': 403, 'headers': headers, 'body': json.dumps({'message': 'User not found'})}

        title = body.get('title')  # Use UUID or other logic to generate a task ID
        description = body.get('description')
        
        if not title or not description:
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'message': 'Missing title or description'})}
        
        task_table.put_item(
            Item={
                'task_id': random.randint(2, 10000),
                'user_id': int(user_id),
                'description': description,
                'title': title
            }
        )
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': f"Task added by {user['username']}"})
        }
    except jwt.ExpiredSignatureError:
        return {'statusCode': 401, 'headers': headers, 'body': json.dumps({'message': 'Token has expired'})}
    except jwt.InvalidTokenError:
        return {'statusCode': 403, 'headers': headers, 'body': json.dumps({'message': 'Invalid token'})}
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'message': 'Error adding task', 'error': str(e)})}
