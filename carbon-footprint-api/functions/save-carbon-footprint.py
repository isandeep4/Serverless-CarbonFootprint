import json
import boto3
import os
import uuid
from datetime import datetime, UTC
from decimal import Decimal

def convert_floats(obj):
    if isinstance(obj, list):
        return [convert_floats(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))  # convert float -> Decimal
    else:
        return obj
def convert_decimals_to_floats(obj):
    """Recursively convert Decimals to floats for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals_to_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals_to_floats(elem) for elem in obj]
    return obj

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ["DYNAMODB_TABLE"]


def lambda_handler(event, context):
    data = json.loads(event.get("body", "{}"))
    table = dynamodb.Table(TABLE_NAME)
    item = {
        'user_id': data["id"],
        'transport': data["travelQuestionnaire"],
        'food': data["foodQuestionnaire"],
        'home': data["homeQuestionnaire"],
        'shopping': data["shoppingQuestionnaire"],
        'created_at': datetime.utcnow().isoformat()
    }
    item = convert_floats(item)
    table.put_item(Item=item)
    response_item = convert_decimals_to_floats(item)
    response = {
        "statusCode": 200, 
        "body": json.dumps({"message": "Data saved successfully!",  "item": response_item}),
        "headers": {
            "Content-Type": "application/json"
        }
    }

    return response
