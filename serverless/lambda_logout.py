import json
import boto3
from werkzeug.security import check_password_hash
import jwt
import datetime
from boto3.dynamodb.conditions import Attr  # Import Attr for filter expressions

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
        if body.get('token') is None:
            return {'statusCode': 400,'headers': headers,'body': f"Missing token"}


    # Retrieve user from DynamoDB
    try:
        # Create JWT token
        token = body["token"]
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = decoded_token['user_id']

        # Check if user exists
        response = user_table.get_item(Key={'user_id': int(user_id)})
        user = response.get('Item')
        if not user:
            return {'statusCode': 403, 'body': json.dumps({'message': 'User not found'}), 'headers': headers}

        user_login_his = user_login_history.scan(
            FilterExpression=Attr('user_id').eq(user.get('user_id')) & Attr('is_logged_in').eq(True)
        )

        if len(user_login_his.get("Items")) == 0:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'User logged out successfully'})
            }

        user_login_history.update_item(
            Key={
                "user_login_id": user_login_his.get('Items')[0]['user_login_id'],
            },
            UpdateExpression="set logout_time = :logout_time, is_logged_in = :is_logged_in",
            ExpressionAttributeValues={
                ':logout_time': datetime.datetime.now().isoformat(),
                ':is_logged_in': False
            }
        )

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'User logged out successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'message': 'Error logging out user', 'error': str(e)})
        }
