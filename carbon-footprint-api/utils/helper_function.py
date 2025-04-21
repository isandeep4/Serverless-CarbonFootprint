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
    }
}
carbonIntensity = {
  "beef": 60,
  "meat": 20,
  "pork": 12,
  "chicken": 6,
  "seafood": 10,
  "diary": 15,
  "vegan": 1,
}


def calculate_transport_emissions(transport_data):
    print("user data from handler:", transport_data)
    transport_emission = Decimal(0)
    transport_lookup = {item["qId"]: item["answer"] for item in transport_data}
    for question_answer in transport_data:
        if question_answer.get("qId") == "q1":
            q1_answer = transport_lookup.get("q1")
            q1_answer_factor = conversion_factor["transport"]["q1"][question_answer.get("answer")]
            if q1_answer == "car":
                q2_answer = transport_lookup.get("q2")
                q2_answer_emission = conversion_factor["transport"]["q2"].get(q2_answer, 0)
                q3_answer = transport_lookup.get("q3")
                q3_answer_emission = conversion_factor["transport"]["q3"].get(q3_answer, 0)
                transport_emission += q1_answer_factor * q2_answer_emission * q3_answer_emission
            elif q1_answer == "motorbike":
                q3_answer = transport_lookup.get("q3")
                q3_answer_emission = conversion_factor["transport"]["q3"].get(q3_answer, 0)
                transport_emission += q1_answer_factor * 0.1 * q3_answer_emission
            elif q1_answer == "bus":
                transport_emission += q1_answer_factor * 0.9
        elif question_answer.get("qId") == "q4":
            q4_answer = transport_lookup.get("q4")
            q4_emission = conversion_factor["transport"]["q4"].get(q4_answer, 0) * 0.3
            transport_emission += q4_emission
        elif question_answer.get("qId") == "q5":
            q5_answer = transport_lookup.get("q5", {})
            domestic_flights = q5_answer.get("domestic")
            intra_continent_flights = q5_answer.get("intra_continent")
            inter_continent_flights = q5_answer.get("inter_continent")
            domestic_emission = conversion_factor["transport"]["q5"].get("domestic") * domestic_flights
            intra_continent_emission = conversion_factor["transport"]["q5"].get("intra_continent") * intra_continent_flights
            inter_continent_emission = conversion_factor["transport"]["q5"].get("inter_continent") * inter_continent_flights
            transport_emission += domestic_emission + intra_continent_emission + inter_continent_emission
        elif question_answer.get("qId") == "q6":
            q6_answer = transport_lookup.get("q6", None)
            q6_emission = conversion_factor["transport"]["q6"].get(q6_answer, 0) 
            transport_emission = transport_emission - q6_emission * transport_emission
    return transport_emission
