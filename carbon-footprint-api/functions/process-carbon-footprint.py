import boto3
import os
import json
from datetime import datetime, UTC
from decimal import Decimal 
from utils.helper_function import calculate_food_emission, calculate_home_emission, calculate_shopping_emission, calculate_transport_emissions

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

def lambda_handler(event, context):
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
            transport_emission = calculate_transport_emissions(formatted_data["transport"])
            food_emission = calculate_food_emission(formatted_data["food"])
            home_emission = calculate_home_emission(formatted_data["home"])
            shopping_emission =  calculate_shopping_emission(formatted_data["shopping"]) 
            total_emission = transport_emission + food_emission + home_emission + shopping_emission
            print("result:", total_emission) 

            regional_emission = 40 #weekly
            global_emission = 100 #weekly
            percentage_difference = ((regional_emission - total_emission) / regional_emission) * 100

            insight_table = dynamodb.Table(INSIGHTS_TABLE)
            
            insight_table_item = {
                'user_id': formatted_data["user_id"],
                'transport': transport_emission,
                'food': food_emission,
                'home': home_emission,
                'shopping': shopping_emission,
                'total_emissions': total_emission,
                'created_at': formatted_data["created_at"],
                "regional_emission": regional_emission,
                "difference_percentage": percentage_difference,
                "global_emission": global_emission
            }
            insight_table.put_item(Item=insight_table_item)

            return {"statusCode": 200, "body": json.dumps({"message": "Insights saved"})}




