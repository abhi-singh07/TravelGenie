import os
import re
import json
import google.generativeai as genai
from datetime import datetime

def llm_generate(inputs: json, trip_plan: json, data_list: json):
    country = inputs["country"]
    from_date = inputs["from_date"]
    to_date = inputs["to_date"]
    user_pref = inputs["user_pref"]
    num_people = inputs["num_people"]
    budget_in_usd = inputs["budget_in_usd"]

    trip_plan = json.dumps(trip_plan, indent=2)
    data_list = json.dumps(data_list, indent=2)

    # Gemini API setup
    GOOGLE_API_KEY = 'AIzaSyCxuYZOEnAasnK_LZY4Tc2fFn5wWozhr4Y'  # Replace with environment variable for security
    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel("models/gemini-1.5-pro-002")

    prompt = f"""
        You are an expert travel planner AI.

        Use the structured JSON data provided below to generate a complete day-by-day travel itinerary for the user.

        ### Include:
        - A clear day-wise breakdown (Day 1, Day 2, etc.)
        - Top attractions in each city with short descriptions
        - Flights (departure/arrival, airline, and **total price for all travelers**)
        - Recommended hotels (total price for the stay)(prices are total for all travelers not per night)
        - Restaurant suggestions with estimated per-person cost

        User Inputs:
        - Destination: {country}
        - Dates: {from_date} to {to_date}
        - Budget per person (USD): ${budget_in_usd}
        - Number of Travelers: {num_people}
        - Preferences: {user_pref}

        ---

        Trip Plan:
        {trip_plan}

        Structured Trip Data:
        {data_list}

        ---
        Note:
        - Flight prices are total for all travelers, not per person.
        - Hotel prices are total for the entire stay, not per night.

        ### At the End of Itinerary:

        Perform the following calculations **explicitly**:

        1. **Total Group Budget** = Budget per person × Number of travelers  
        = ${budget_in_usd} × {num_people} = ${budget_in_usd * num_people}

        2. **Cost Breakdown**:  
        - Total Flights = $...
        - Total Hotels = $...
        - Total Attractions = $...
        - Total Restaurants = $...
        - **Total Estimated Cost** = sum of above

        3. **Budget Percentage Used** = (Total Estimated Cost / Total Group Budget) × 100  
        → Show this percentage clearly, e.g.,  
        "You used 67% of your total budget."

        4. **Only IF the Total Estimated Cost exceeds the Total Group Budget**, display this warning message:

        > ⚠️ The planned trip exceeds the budget. Please consider reducing the number of travelers or the number of cities to stay within your budget.

        Otherwise, do **not** show this message.

        ---

        End the itinerary with a few helpful travel tips for the user.
        """



    response = model.generate_content(prompt)
    return response.text


if __name__ == "__main__":
    with open("user_inputs.json", "r") as f:
        inputs = json.load(f)

    with open("itinerary.json", "r") as f:
        trip_plan = json.load(f)

    with open("combined_data_hotel_attraction_flight_final.json", "r") as f:
        data_list = json.load(f)

    final_itinerary = llm_generate(inputs, trip_plan, data_list)

    if final_itinerary:
        with open("generated_itinerary.txt", "w") as f:
            f.write(final_itinerary)
        print("Final Itinerary generated and saved to generated_itinerary.txt")
    else:
        print("Itinerary not generated.")
