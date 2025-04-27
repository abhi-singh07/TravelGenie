# travelgenie_rag_ui.py
import streamlit as st
import json
from datetime import datetime
from main import run_full_pipeline

st.set_page_config(page_title="TravelGenie ✈️", layout="centered")
st.title("🧠 TravelGenie - AI Powered Itinerary Planner")

st.subheader("🧳 Enter Your Travel Preferences")

with st.form("user_input_form"):
    country = st.text_input("Destination Country", value="India")
    from_date = st.date_input("Start Date", datetime(2025, 7, 11))
    to_date = st.date_input("End Date", datetime(2025, 7, 17))
    city_range = st.selectbox("How many cities do you want to visit?", ["1 to 3", "3 to 5", "6 to 10"])
    user_pref = st.text_area("Your travel preferences", value="I want to go to hill stations and historical sites.")
    num_people = st.number_input("Number of Travellers", value=4, min_value=1, max_value=20)
    budget_in_usd = st.number_input("Budget (in USD)", value=2000, min_value=500, step=100)
    generate = st.form_submit_button("Generate My Itinerary")

if generate:
    # Store input as JSON
    user_inputs = {
        "country": country,
        "from_date": str(from_date),
        "to_date": str(to_date),
        "num_cities": city_range,
        "user_pref": user_pref,
        "num_people": num_people,
        "budget_in_usd": budget_in_usd
    }

    with open("user_inputs.json", "w") as f:
        json.dump(user_inputs, f, indent=2)

    st.info("Generating itinerary... this may take a minute ⏳")
    response_text = run_full_pipeline()  # This will read inputs, run LLMs, and return final text

    st.success("Itinerary Generated ✅")
    st.subheader("📝 Your AI-Curated Plan")
    st.markdown(response_text)
