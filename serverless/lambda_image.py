import json
import boto3
from PIL import Image
from io import BytesIO
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print(event)
    headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'}
    http_method = event.get('httpMethod')
    print(http_method)
    if http_method == 'OPTIONS':
        return {'statusCode': 200,'headers': headers,'body': f""} 

    # Parse the input data
    body = json.loads(event['body'])
    image_data = base64.b64decode(body['image'])
    image_format = body['format']
    rotation = body['rotation']
    bucket_name = 'serverless-bucket-test-123'

    # Load the image
    image = Image.open(BytesIO(image_data))

    # Convert format if needed
    if image_format.lower() not in ['jpg', 'jpeg', 'png']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Unsupported format'})
        }
    output_format = 'JPEG' if image_format.lower() in ['jpg', 'jpeg'] else 'PNG'

    # Rotate image if needed
    if rotation:
        image = image.rotate(int(rotation), expand=True)

    # Save the processed image to a buffer
    buffer = BytesIO()
    image.save(buffer, format=output_format)
    buffer.seek(0)

    # Generate a unique filename
    image_key = f'processed_image.{image_format}'

    # Upload the image to S3
    s3.upload_fileobj(buffer, bucket_name, image_key, ExtraArgs={'ContentType': f'image/{image_format}'})

    # Generate the S3 URL
    image_url = f'https://{bucket_name}.s3.amazonaws.com/{image_key}'

    # Return the S3 URL
    return {
        'headers': headers,
        'statusCode': 200,
        'body': json.dumps({'image_url': image_url})
    }
