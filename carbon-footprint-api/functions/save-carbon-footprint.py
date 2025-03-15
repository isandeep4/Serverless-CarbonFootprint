import json
import boto3
import os
import uuid
from datetime import datetime, UTC

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ["DYNAMODB_TABLE"]


def lambda_handler(event, context):
    data = json.loads(event.get("body", "{}"))
    table = dynamodb.Table(TABLE_NAME)
    item = {
        'user_id': str(uuid.uuid4()),
        'transport': data["transport"],
        'food': data["food"],
        'energy': data["energy"],
        'created_at': datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)
    response = {
        "statusCode": 200, 
        "body": json.dumps({"message": "Data saved successfully!",  "item": item}),
        "headers": {
            "Content-Type": "application/json"
        }
    }

    return response
