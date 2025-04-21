import os
import re
import json
import google.generativeai as genai
from datetime import datetime

def llm_generate(inputs:json, trip_plan:json, data_list:json):
    country = inputs["country"]
    from_date = inputs["from_date"]
    to_date = inputs["to_date"]
    # num_cities = inputs["num_cities"]
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
Include:
- Clear day-wise breakdown (Day 1, Day 2...)
- Top attractions in each city
- Flights with departure/arrival details
- Recommended hotels with pricing
- Restaurant suggestions per city (search good ones or suggest based on popular areas)
- End summary with cost breakdown and travel tips.

User Inputs:
Destination: {country}
Dates: {from_date} to {to_date}
Budget in USD: ${budget_in_usd}
Travellers: {num_people}
User Preference: {user_pref}

Trip Plan:
{trip_plan}

Structured Trip Data:
{data_list}

Now write a friendly, professional and complete travel itinerary in natural language and the following format. Include hotel names, rates, dates and times whenever you can.
End with a total spend percentage of budget.

Day 1:
City 1: Hotel1
Attraction 1: short desc
Attraction 2: short desc
Flight to city 2

Day 2:
...

Note that the hotel and flight prices provided are for the entire stay/trip, and the budget is for the entire journey.

Make sure the trip is within the budget, or respond with:
The planned trip exceeds the budget. Please consider reducing the number of travelers or the number of cities to stay within your budget.

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
        print(f"Final Itinerary generated and saved to generated_itinerary.txt")
    else:
        print("Itinerary not generated.")
