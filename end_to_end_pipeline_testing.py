import json
from main import run_full_pipeline
from IPython.display import Markdown, display


user_inputs = {
    "country": "India",
    "from_date": "2025-07-12",
    "to_date": "2025-07-19",
    "num_cities": "3 to 5",
    "user_pref": "I want to go to hill stations and historic temples",
    "num_people": 4,
    "budget_in_usd": 2500
}

with open("user_inputs.json", "w") as f:
    json.dump(user_inputs, f, indent=2)

print("✅ user_inputs.json saved")

itinerary_text = run_full_pipeline()
print("✅ Pipeline completed")


display(Markdown("### ✨ AI‑Generated Travel Itinerary"))
display(Markdown(itinerary_text))
