import boto3
import os
import json
from datetime import datetime, UTC
from decimal import Decimal 

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ["DYNAMODB_TABLE"]
INSIGHTS_TABLE = os.environ["INSIGHTS_TABLE"]

def get_user_data(user_id):
    table = dynamodb.Table(TABLE_NAME)
    result = table.get_item(Key={"user_id": user_id})
    return result.get("Item", {})

def calculate_emissions(user_data):
    print("user data from handler:", user_data)  # Debugging print
    category_emissions = {}
    total_emissions = Decimal(0)
    for category, item in user_data.items():
        if category in emission_factor:
            category_emissions[category] = Decimal(0)
            for item, itemObj in item.items():
                if item in emission_factor[category]:
                    num_value = Decimal(itemObj.get("value"))  # Extract numeric value
                    item_emission = num_value * emission_factor[category][item]
                    category_emissions[category] += item_emission
                    total_emissions += item_emission
    return { "total_emissions": total_emissions, "category_emissions": category_emissions }

emission_factor = {
   "transport": {"car": Decimal("0.2"), "bus": Decimal("0.05"), "bike": Decimal("0")},
    "food": {"beef": Decimal("27"), "chicken": Decimal("6.9"), "vegetables": Decimal("2")},
    "energy": {"electricity": Decimal("0.5")}
}

def lambda_handler(event, context):
    for record in event["Records"]:
        if record["eventName"] == "INSERT":
            user_data = record["dynamodb"]["NewImage"]
            user_id = user_data["user_id"]["S"]
            formatted_data = {}
            for category, value in user_data.items():
                if category not in ["user_id", "created_at"] and "M" in value:
                    formatted_data[category] = {}
                    for key, v in value["M"].items():
                        formatted_data[category][key] = {"value": v["M"]["value"]["N"]}
            print("formatted_data:", formatted_data)
            emissions_result = calculate_emissions(formatted_data)
            category_emissions = emissions_result["category_emissions"]
            total_emissions = emissions_result["total_emissions"]

            insight_table = dynamodb.Table(INSIGHTS_TABLE)
            
            insight_table_item = {
                'user_id': user_id,
                'transport': category_emissions.get("transport", Decimal(0)),
                'food': category_emissions.get("food", Decimal(0)),
                'energy': category_emissions.get("energy", Decimal(0)),
                'total_emissions': total_emissions,
                'created_at': datetime.utcnow().isoformat()
            }
            insight_table.put_item(Item=insight_table_item)

            return {"statusCode": 200, "body": json.dumps({"message": "Insights saved"})}




