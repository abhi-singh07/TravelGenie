# main.py
import asyncio
import aiohttp
import json
from attraction_api import fetch_attractions
from hotel_api import HotelRetriever
from flight_api import FlightRetriever
from llm_retrieve import llm_retrieve
from llm_generate import llm_generate


def run_full_pipeline():
    # Load user inputs
    with open("user_inputs.json", "r") as f:
        inputs = json.load(f)

    # Step 1: Generate trip plan (itinerary skeleton)
    trip_plan = llm_retrieve(inputs)

    # Step 2: Run attraction/hotel/flight retrievals
    async def gather_all():
        async with aiohttp.ClientSession() as session:
            attraction_tasks = [fetch_attractions(session, city) for city in trip_plan.keys()]
            attraction_results = await asyncio.gather(*attraction_tasks)

        hotel_results = HotelRetriever(trip_plan, numadults=inputs['num_people'])
        flight_results = FlightRetriever(trip_plan, numadults=inputs['num_people'])
        return attraction_results, hotel_results, flight_results

    attractions, hotels, flights = asyncio.run(gather_all())

    # Step 3: Merge all results into single structure
    combined = {city: {"city": city, "attractions": [], "hotels": [], "flights": []} for city in trip_plan}

    for entry in attractions:
        combined[entry["city"]]["attractions"] = entry["attractions"]

    for city, hotel_data in hotels.items():
        combined[city]["hotels"] = hotel_data

    for entry in flights:
        from_city = entry["from"]
        to_city = entry["to"]
        date = entry["date"]
        flights_data = entry.get("flights")
        note = entry.get("note")

        combined[from_city].setdefault("flights", []).append({
            "to": to_city,
            "date": date,
            "flights": flights_data,
            "note": note
        })

    final_list = list(combined.values())

    # Step 4: Save merged data for debugging
    with open("combined_data_hotel_attraction_flight_final.json", "w") as f:
        json.dump(final_list, f, indent=2)

    # Step 5: Run LLM final generation
    final_itinerary = llm_generate(inputs, trip_plan, final_list)

    with open("generated_itinerary.txt", "w") as f:
        f.write(final_itinerary)

    return final_itinerary
