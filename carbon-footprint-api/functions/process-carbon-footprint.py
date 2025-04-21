import boto3
import os
import json
from datetime import datetime, UTC
from decimal import Decimal 
from helper_function import conversion_factor, carbonIntensity

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ["DYNAMODB_TABLE"]
INSIGHTS_TABLE = os.environ["INSIGHTS_TABLE"]

def unwrap_dynamodb_value(value):
    if 'S' in value:
        return value['S']
    elif 'N' in value:
        return float(value['N']) if '.' in value['N'] else int(value['N'])
    elif 'M' in value:
        return {k: unwrap_dynamodb_value(v) for k, v in value['M'].items()}
    elif 'L' in value:
        return [unwrap_dynamodb_value(item) for item in value['L']]
    else:
        return value

def lambda_handler(event):
    print("stream data", event)
    for record in event["Records"]:
        if record["eventName"] == "INSERT":
            user_data = record["dynamodb"]["NewImage"]
            formatted_data = {
                "user_id": user_data["user_id"]["S"],
                "created_at": user_data["created_at"]["S"]
            }
            for category, value in user_data.items():
                if category not in ["user_id", "created_at"] and "L" in value:
                    formatted_data[category] = []
                    items = unwrap_dynamodb_value(value)
                    for item in items:
                        qId = unwrap_dynamodb_value(item.get("qId", {}))
                        # question = unwrap_dynamodb_value(item.get("question", {}))
                        answer = unwrap_dynamodb_value(item.get("answer", {}))
                        if not answer:
                            continue
                        processed_answer = answer
                        if isinstance(answer, dict):
                            if "value" in answer:
                                processed_answer = answer["value"]
                            else:
                                processed_answer = answer
                        formatted_data[category].append({
                            "qId": qId,
                            # 'question': question,
                            'answer': processed_answer
                        })
            print("formatted_data:", formatted_data)
            result = calculate_emissions(formatted_data)

            # insight_table = dynamodb.Table(INSIGHTS_TABLE)
            
            # insight_table_item = {
            #     'user_id': user_id,
            #     'transport': category_emissions.get("transport", Decimal(0)),
            #     'food': category_emissions.get("food", Decimal(0)),
            #     'energy': category_emissions.get("energy", Decimal(0)),
            #     'total_emissions': total_emissions,
            #     'created_at': created_at
            # }
            # insight_table.put_item(Item=insight_table_item)

            # return {"statusCode": 200, "body": json.dumps({"message": "Insights saved"})}




