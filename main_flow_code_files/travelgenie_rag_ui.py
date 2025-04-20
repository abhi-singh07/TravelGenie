# travelgenie_rag_ui.py

import streamlit as st
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama
import json
import subprocess
import time

# -----------------------------
# Streamlit App Inputs
# -----------------------------
st.title("🧠 TravelGenie - AI Generated Itinerary with LangChain RAG")

with st.form("User Input"):
    destination = st.text_input("Destination", "India")
    budget = st.number_input("Budget (INR)", value=60000)
    from_date = st.date_input("Start Date", datetime(2025, 6, 1))
    to_date = st.date_input("End Date", datetime(2025, 6, 10))
    traveller_count = st.number_input("Number of Travellers", min_value=1, value=2)
    city_range = st.selectbox("City Count", ["1 to 3", "3 to 5", "6 to 10"], index=1)
    user_pref = st.text_area("Preferences (e.g. beach, temples, cold weather)", "I want to go to hill stations and mountains.")
    generate = st.form_submit_button("Generate Itinerary")

if generate:
    # Save user config to JSON for llm_retrieve to read
    user_inputs = {
        "country": destination,
        "from_date": str(from_date),
        "to_date": str(to_date),
        "num_cities": city_range,
        "user_pref": user_pref,
        "num_people": traveller_count
    }
    with open("user_inputs.json", "w") as f:
        json.dump(user_inputs, f, indent=2)

    # Run llm_retrieve.py to generate itinerary
    subprocess.run(["python3", "llm_retrieve.py"])

    # Pause to ensure file write completes
    time.sleep(2)

    # Run main.ipynb pipeline to generate final output JSON
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "main.ipynb", "--inplace"])

    # Load the final merged JSON
    with open("/Users/dhruv/Desktop/information_storage_retrieval/Project/TravelGenie/parallel_api_calls/combined_data_hotel_attraction_flight_Apr_19th.json") as f:
        enriched_data = json.load(f)

    # -----------------------------
    # Prepare RAG Format
    # -----------------------------
    first_entry = enriched_data[0]
    user_info = {
        "destination": enriched_data[-1]["city"],
        "from_date": enriched_data[0]["arrival_date"],
        "to_date": enriched_data[-1]["departure_date"],
        "budget_in_inr": budget,
        "traveller_count": traveller_count
    }

    selected_cities = [city["city"] for city in enriched_data]

    rag_daily = []
    for i, entry in enumerate(enriched_data, start=1):
        rag_daily.append({
            "day": i,
            "city": entry["city"],
            "attractions": [a["name"] for a in entry["attractions"][:3]],
            "restaurant": "TBD",
            "notes": f"Hotel: {entry['hotels']['popularity'][0]['name']} (₹{entry['hotels']['popularity'][0]['price']})"
        })

    rag_data = {
        "user_info": user_info,
        "selected_cities": selected_cities,
        "daily_itinerary": rag_daily
    }

    # -----------------------------
    # Prompt Template
    # -----------------------------
    prompt_template = PromptTemplate(
        input_variables=["destination", "from_date", "to_date", "budget", "cities", "itinerary"],
        template="""
You are an AI travel planner.

Given the following input:

- Destination: {destination}
- Travel Dates: {from_date} to {to_date}
- Total Budget: ₹{budget}
- Cities to Visit: {cities}

Daily Plans:
{itinerary}

Generate a friendly, well-structured travel itinerary in natural language. 
Include clear daily highlights, attraction names, hotels, flight, restaurant they can eat based on the cities and summarize overall budget insights.
 Make it engaging and easy to follow. Do not return inner thoughts or markdown formatting. 
Just provide the final narrative result.

Note: Understand the json we have given and plan each city in a way using our data and the date range given for each cities so that they can travel it convinently and utilize their tour till the last day.

"""
    )

    def get_llm():
        return ChatOllama(model='llama3.2')

    def generate_itinerary_from_rag(rag_data):
        itinerary_text = ""
        for day in rag_data['daily_itinerary']:
            itinerary_text += f"\nDay {day['day']} - {day['city']}\n"
            itinerary_text += "  - Attractions: " + ", ".join(day['attractions']) + "\n"
            itinerary_text += f"  - Restaurant: {day['restaurant']}\n"
            itinerary_text += f"  - Notes: {day['notes']}\n"

        filled_prompt = prompt_template.format(
            destination=rag_data['user_info']['destination'],
            from_date=rag_data['user_info']['from_date'],
            to_date=rag_data['user_info']['to_date'],
            budget=rag_data['user_info']['budget_in_inr'],
            cities=" → ".join(rag_data['selected_cities']),
            itinerary=itinerary_text
        )

        llm = get_llm()
        response = llm.invoke(filled_prompt)
        return response.content if hasattr(response, 'content') else response

    # Run LLM and display
    itinerary_result = generate_itinerary_from_rag(rag_data)

    st.subheader("📝 Your AI-Generated Travel Plan")
    st.markdown(itinerary_result)
