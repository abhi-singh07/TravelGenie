# travelgenie_rag_ui.py

import streamlit as st
from datetime import datetime
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain_ollama import ChatOllama  # Updated for Ollama
import json

# -----------------------------
# Load precomputed RAG JSON
# -----------------------------
with open("final_rag_input.json") as f:
    rag_data = json.load(f)

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

Generate a friendly, well-structured travel itinerary in natural language. Include clear daily highlights, attraction names, restaurant suggestions, and summarize overall budget insights. Make it engaging and easy to follow. Do not return inner thoughts or markdown formatting. Just provide the final narrative result.
"""
)

# -----------------------------
# Get LLM using LLaMA 3.2 from Ollama
# -----------------------------
def get_llm():
    return ChatOllama(model='llama3.2')  # or 'llama3:8b-instruct' if available

# -----------------------------
# LangChain Pipeline
# -----------------------------
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

# -----------------------------
# Streamlit App
# -----------------------------
st.title("🧠 TravelGenie - AI Generated Itinerary with LangChain RAG")

with st.form("User Input"):
    destination = st.text_input("Destination", rag_data['user_info']['destination'])
    budget = st.number_input("Budget (INR)", value=rag_data['user_info']['budget_in_inr'])
    from_date = st.date_input("Start Date", datetime.strptime(rag_data['user_info']['from_date'], "%Y-%m-%d"))
    to_date = st.date_input("End Date", datetime.strptime(rag_data['user_info']['to_date'], "%Y-%m-%d"))
    generate = st.form_submit_button("Generate Itinerary")

if generate:
    rag_data['user_info']['destination'] = destination
    rag_data['user_info']['budget_in_inr'] = budget
    rag_data['user_info']['from_date'] = str(from_date)
    rag_data['user_info']['to_date'] = str(to_date)

    itinerary_result = generate_itinerary_from_rag(rag_data)

    st.subheader("📝 Your AI-Generated Travel Plan")
    st.markdown(itinerary_result)