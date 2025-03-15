import boto3
import os
import json
from decimal import Decimal 

dynamodb = boto3.resource('dynamodb')
INSIGHTS_TABLE = os.environ["INSIGHTS_TABLE"]

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def lambda_handler(event, context):
    user_id = event["queryStringParameters"]["user_id"]
    table = dynamodb.Table(INSIGHTS_TABLE)
    response = table.get_item(Key={"user_id": user_id})

    return {
        "statusCode": 200,
        "body": json.dumps(response.get("Item", {}),default=decimal_to_float)
    }