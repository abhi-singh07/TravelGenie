import os
import re
import json
import google.generativeai as genai
from datetime import datetime

country = "Netherlands"
from_date = "2025-06-01"
to_date = "2025-06-10"
num_cities = "3 to 5"
user_pref = "I want to go to hill stations and beaches."
num_people = 5

GOOGLE_API_KEY = 'AIzaSyAhZpOTfkUrnAqJOJ1l0OidlmfvcDUxsek'
genai.configure(api_key=GOOGLE_API_KEY)

def llm_retrieve():    
    # Define the model
    model = genai.GenerativeModel("models/gemini-1.5-pro-002")

    # Create a prompt for LLM
    prompt = f"""You are a travel assistant. Give me an itinerary of {num_cities} cities to visit in {country} in the month of {datetime.strptime(from_date, "%Y-%m-%d").strftime("%B")} along with dates to visit between {from_date} to {to_date}.
    The places must be conducive to the season and the city should have an airport. Output in this json formatwithout any comments: {{City Name: {{Arrival Date: Date arriving in, Departure Date: Date Leaving, Airport: Airport code}}}}.
    {user_pref}
    """

    # Send request to Gemini API
    response = model.generate_content(prompt)

    return clean_itinerary(response.text)

def clean_itinerary(itinerary_text:str):
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

itinerary_dic = llm_retrieve()

if itinerary_dic:
    with open("itinerary.json", "w") as file:
        json.dump(itinerary_dic, file, indent=4)
    print("Itinerary saved to itinerary.json")
else:
    print("Itinerary not saved due to invalid or missing format.")
