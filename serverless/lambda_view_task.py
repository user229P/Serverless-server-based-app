import json
import boto3
import jwt
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
task_table = dynamodb.Table('user_task')
user_table = dynamodb.Table('user_table')
JWT_SECRET = 'sdjosdosdjdmpwonlknjsblsbk22312wdkljdd'

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    http_method = event.get('requestContext', {}).get('http', {}).get('method', None)
    
    if isinstance(event, str):
        body = json.loads(event)
    else:
        body = json.loads(event.get('body', '{}'))
    
    if http_method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ""}

    elif http_method is None:
        if 'token' not in body:
            return {'statusCode': 400, 'headers': headers, 'body': "Missing token"}
        
    token = body.get('token')

    try:
        # Verify token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = decoded_token.get('user_id')

        # Check if user exists
        response = user_table.get_item(Key={'user_id': int(user_id)})
        user = response.get('Item')

        if not user:
            return {'statusCode': 403, 'headers': headers, 'body': json.dumps({'message': 'User not found'}), 'headers': headers}
        
        response_task = task_table.scan(
            FilterExpression=Attr('user_id').eq(user.get('user_id'))
        )
        tasks = response_task.get('Items')
        tasks_case = []
        for task in tasks:
            task["user_id"] = str(task["user_id"])
            task["task_id"] = str(task["task_id"])
            tasks_case.append(task)
            

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({"tasks": tasks_case})
        }

    except jwt.ExpiredSignatureError:
        return {'statusCode': 401, 'headers': headers, 'body': json.dumps({'message': 'Token has expired'})}
    except jwt.InvalidTokenError:
        return {'statusCode': 403, 'headers': headers, 'body': json.dumps({'message': 'Invalid token'})}
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'message': 'Error processing request', 'error': str(e)})}
