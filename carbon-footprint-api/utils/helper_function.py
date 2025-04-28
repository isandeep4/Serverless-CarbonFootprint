from decimal import Decimal


conversion_factor = {
    "transport": {
        "q1": {
            "walk": 0,  # km traveled per hour
            "car": 30,
            "motorbike": 15,
            "bus": 10,
        },
        "q2": {
            "petrol": 0.2, # co2 kg/km
            "diesel": 0.125,
            "electric": 0.33,
            "hybrid": 0.160
        },
        "q3": {
            "<2h": 1,
            "2h><5h": 3.5,
            "5h><15h": 10,
            "15h><25h": 20,
            ">25h": 30
        },
        "q4": {
            "0h": 0, 
            "<2h": 1,
            "2h><5h": 3.5,
            "5h><15h": 10,
            "15h><25h": 20,
            ">25h": 30
        },
        "q5": {
            "domestic": 500 * 0.25, #km * factor co2 emission kg per km
            "intra_continent": 2000 * 0.25,
            "inter_continent": 6000 * 0.25,
        },
        "q6": {
            "none": 0,
            "25%": 0.25,
            "50%": 0.2,
             "75%": 0.75,
             "all": 1
        }
    },
    "food": {
        "q1": {
            "beef": 40, # $ spent week
            "meat": 25,
            "pork": 15,
            "chicken": 20,
            "seafood": 20,
            "diary": 15,
            "vegan": 15,
        },
        "q2": {
            "0$": 0,
            "1$><20$": 10,
            "20$><50$": 30,
            ">50$": 60
        },
        "q3": {
            "0%": 0,
            "0%><10%": 0.05,
            "10%><20%": 0.15,
            "20%><30%": 0.25,
            ">30%": 0.40
        },
        "q4": {
            "local": 0.85,
            "mall": 1,
            "Both": 1.15
        }
    },
    "home": {
      "q1": {
        "detached": 1.2,
        "semiDetached": 1.0,
        "terrace": 0.9,
        "flat": 0.7
      },
      "q2": {
          "1": 1,
          "2": 2,
          "3": 3,
          ">=4": 4
      },
      "q3": {
          "1": 1,
          "2": 2,
          "3": 3,
          ">=4": 4
      },
      "q4": {
          "gas":  0.184, # co2kg / kwh
          "oil": 0.249,
          "electricity": 0.233,
          "wood": 0.015,
      },
      "q5": {
          "yes": 0.9,
          "no": 1
      },
      "q6": {
        "<14": 0.8,
        "14-17": 0.9,
        "18-21": 1.0,
        ">21": 1.1, 
      }
    },
    "shopping": {
        "q1": {
            "0$": 0,
            "1$><60$": 30,
            "60$><150$": 100,
            ">150$": 160
        },
        "q2": {
          "0$": 0,
          "1$><10$": 5,
          "10$><60$": 30,
          ">60$": 70  
        },
        "q3": {
          "0h": 0,
          "1h><3h": 2,
          "3h><5h": 4,
          "5h><7h": 6 
        },
        "q4": {
          "0$": 0,
          "1$><25$": 12,
          "25$><50$": 37,
          "50$><75$": 62,
          ">75$": 80  
        },
        "q5": {
            "paper": -0.2,
            "plastic": -0.6,
            "glass": -0.1,
            "metal": -0.3,
            "food": -0.5,
        }
    }

}
co2_per_dollar_spent_food = {
    "beef": 1.5,      # kg CO₂ per $
    "meat": 1.2,
    "pork": 0.8,
    "chicken": 0.6,
    "seafood": 0.9,
    "diary": 1.0,
    "vegan": 0.3
}


def calculate_transport_emissions(transport_data):
    print("user data from handler:", transport_data)
    transport_emission = Decimal(0)
    transport_lookup = {item["qId"]: item["answer"] for item in transport_data}
    for question_answer in transport_data:
        if question_answer.get("qId") == "q1":
            q1_answer = transport_lookup.get("q1")
            q1_answer_factor = Decimal(conversion_factor["transport"]["q1"].get(q1_answer))
            if q1_answer == "car":
                q2_answer = transport_lookup.get("q2")
                q2_answer_emission = Decimal(conversion_factor["transport"]["q2"].get(q2_answer, 0))
                q3_answer = transport_lookup.get("q3")
                q3_answer_emission = Decimal(conversion_factor["transport"]["q3"].get(q3_answer, 0))
                transport_emission += q1_answer_factor * q2_answer_emission * q3_answer_emission
            elif q1_answer == "motorbike":
                q3_answer = transport_lookup.get("q3")
                q3_answer_emission = Decimal(conversion_factor["transport"]["q3"].get(q3_answer, 0))
                transport_emission += q1_answer_factor * Decimal('0.1') * q3_answer_emission
            elif q1_answer == "bus":
                transport_emission += q1_answer_factor * Decimal('0.9')
        elif question_answer.get("qId") == "q4":
            q4_answer = transport_lookup.get("q4")
            q4_emission = Decimal(conversion_factor["transport"]["q4"].get(q4_answer, 0)) * Decimal('0.3')
            transport_emission += Decimal(q4_emission)
        elif question_answer.get("qId") == "q5":
            q5_answer = transport_lookup.get("q5", {})
            domestic_flights = Decimal(q5_answer.get("domestic"))
            intra_continent_flights = Decimal(q5_answer.get("intra_continent"))
            inter_continent_flights = Decimal(q5_answer.get("inter_continent"))
            domestic_emission = Decimal(conversion_factor["transport"]["q5"].get("domestic")) * domestic_flights
            intra_continent_emission = Decimal(conversion_factor["transport"]["q5"].get("intra_continent")) * intra_continent_flights
            inter_continent_emission = Decimal(conversion_factor["transport"]["q5"].get("inter_continent")) * inter_continent_flights
            transport_emission += (domestic_emission + intra_continent_emission + inter_continent_emission) / 48
        elif question_answer.get("qId") == "q6":
            q6_answer = transport_lookup.get("q6", None)
            q6_emission = Decimal(conversion_factor["transport"]["q6"].get(q6_answer, 0) )
            transport_emission = transport_emission - (q6_emission * transport_emission)
    print("transport_emission", transport_emission)
    return transport_emission

def calculate_food_emission(food_data):
    print("food_data", food_data)
    food_lookup = { item["qId"]: item["answer"] for item in food_data}
    q1_answer = food_lookup.get("q1")
    q2_answer = food_lookup.get("q2")
    money_spent_restaurant = Decimal(conversion_factor["food"]["q2"].get(q2_answer, 0))
    if isinstance(q1_answer, list):
        avg_money_spent_diet = sum(Decimal(conversion_factor["food"]["q1"].get(answer, 0)) for answer in q1_answer) / len(q1_answer)
        total_money_spent = avg_money_spent_diet + money_spent_restaurant
        avg_co2_per_dollar = sum(Decimal(co2_per_dollar_spent_food[answer]) for answer in q1_answer) / len(q1_answer)
        base_emission = total_money_spent * avg_co2_per_dollar
    else:
        avg_money_spent_diet = Decimal(conversion_factor["food"]["q1"].get(q1_answer, 0))
        total_money_spent = avg_money_spent_diet + money_spent_restaurant
        base_emission = total_money_spent * co2_per_dollar_spent_food[q1_answer]
    q3_answer = food_lookup.get("q3")
    wastage_emission = base_emission * Decimal(conversion_factor["food"]["q3"].get(q3_answer, 0))
    q4_answer = food_lookup.get("q4")
    import_multiplier =  Decimal(conversion_factor["food"]["q4"].get(q4_answer, 1))
    food_emission = (base_emission + wastage_emission) * import_multiplier
    print("food_emission", food_emission)
    return food_emission

def calculate_home_emission(home_data):
    print("home_data", home_data)
    home_lookup = { item["qId"]: item["answer"] for item in home_data}
    q1_answer = home_lookup.get("q1")
    house_type_factor = Decimal(conversion_factor["home"]["q1"].get(q1_answer))
    bedrooms =  Decimal(home_lookup.get("q2", 3))
    people = Decimal(home_lookup.get("q3", 2)) 
    q4_answer = home_lookup.get("q4")
    heating_factor = Decimal(conversion_factor["home"]["q4"].get(q4_answer))
    q5_answer = home_lookup.get("q5")
    LightsOnOff = Decimal(conversion_factor["home"]["q5"].get(q5_answer))
    q6_answer = home_lookup.get("q6")
    room_temperature_factor = Decimal(conversion_factor["home"]["q6"].get(q6_answer))
    base_kwh_per_week = Decimal(230)  # average home
    avg_bedrooms = Decimal(3)
    home_emission = (heating_factor * base_kwh_per_week *
                     (bedrooms / avg_bedrooms) *
                     house_type_factor *
                     LightsOnOff *
                     room_temperature_factor) / people
    print("home_emission", home_emission)
    return home_emission

def calculate_shopping_emission(shopping_data):
    print(shopping_data)
    shopping_lookup = {item["qId"]: item["answer"] for item in shopping_data}
    clothing_emission_per_dollar = Decimal(0.6) # kg co2
    q1_answer = shopping_lookup.get("q1")
    dollar_spent_clothing = Decimal(conversion_factor["shopping"]["q1"].get(q1_answer))
    clothing_emission = dollar_spent_clothing * clothing_emission_per_dollar
    stationary_emission_per_dollar = Decimal(0.3)
    q2_answer = shopping_lookup.get("q2")
    dollar_spent_stationary = Decimal(conversion_factor["shopping"]["q2"].get(q2_answer))
    stationary_emission = stationary_emission_per_dollar * dollar_spent_stationary
    digital_emission_per_hour = Decimal(0.06)
    q3_answer = shopping_lookup.get("q3")
    hour_spent_digital = Decimal(conversion_factor["shopping"]["q3"].get(q3_answer))
    digital_emission = hour_spent_digital * digital_emission_per_hour
    q4_answer = shopping_lookup.get("q4")
    dollar_spent_entertainment = Decimal(conversion_factor["shopping"]["q4"].get(q4_answer))
    entertainment_emission_per_dollar = Decimal(0.07)
    entertainment_emission = entertainment_emission_per_dollar * dollar_spent_entertainment
    q5_answer = shopping_lookup.get("q5")
    if isinstance(q5_answer, list):
        avg_recycle_value = sum(Decimal(conversion_factor["shopping"]["q5"].get(answer)) for answer in q5_answer)
    else:
         avg_recycle_value = Decimal(conversion_factor["shopping"]["q5"].get(q5_answer))   
    shopping_emission = clothing_emission + stationary_emission + digital_emission + entertainment_emission + avg_recycle_value
    print("shopping_emission", shopping_emission)
    return shopping_emission



    









            

