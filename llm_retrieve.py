import os
import re
import json
import google.generativeai as genai
from datetime import datetime


def llm_retrieve(inputs:json):
    country = inputs["country"]
    from_date = inputs["from_date"]
    to_date = inputs["to_date"]
    num_cities = inputs["num_cities"]
    user_pref = inputs["user_pref"]
    # num_people = inputs["num_people"]

    # Gemini API setup
    GOOGLE_API_KEY = 'AIzaSyCxuYZOEnAasnK_LZY4Tc2fFn5wWozhr4Y'  # Replace with environment variable for security
    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel("models/gemini-1.5-pro-002")

    prompt = f"""You are a travel assistant. Give me an itinerary of {num_cities} cities to visit in {country} in the month of {datetime.strptime(from_date, "%Y-%m-%d").strftime("%B")} along with dates to visit between {from_date} to {to_date}.
The places must be conducive to the season and the city should have an airport. Output in this json format without any comments: {{City Name: {{Arrival Date: Date arriving in, Departure Date: Date Leaving, Airport: Airport code}}}}.
{user_pref}
"""

    response = model.generate_content(prompt)

    itinerary_dic = clean_itinerary(response.text)

    if itinerary_dic and isinstance(itinerary_dic, dict):
        with open("itinerary.json", "w") as file:
            json.dump(itinerary_dic, file, indent=4)
        print("Itinerary saved to itinerary.json")
    else:
        print("Itinerary not saved due to invalid or missing format.")

    return itinerary_dic

def clean_itinerary(itinerary_text: str):
    match = re.search(r'{.*}', itinerary_text, re.DOTALL)
    if match:
        json_str = match.group()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print("JSON decoding failed:", e)
            return "Invalid JSON format"
    else:
        return "Itinerary not generated"

if __name__ == "__main__":
    with open("user_inputs.json", "r") as f:
        inputs = json.load(f)

    itinerary_dic = llm_retrieve(inputs)

    if itinerary_dic and isinstance(itinerary_dic, dict):
        with open("itinerary.json", "w") as file:
            json.dump(itinerary_dic, file, indent=4)
        print("Itinerary saved to itinerary.json")
    else:
        print("Itinerary not saved due to invalid or missing format.")
