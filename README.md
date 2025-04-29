# TravelGenie: Your Personalized LLM-Powered Travel Planner

**TravelGenie** is an AI-driven travel agent that curates a fully personalized travel itinerary based on user preferences and given budget.

## How It Works

### 1. Inputs

The following inputs are collected from the user:
- **Country**: The destination country for the trip.
- **Dates**: Travel start and end dates.
- **Budget**: Total budget available for the trip.
- **Traveler Count**: Number of travelers.
- **City Count**: Number of cities the user wants to visit within the country.
- **User Preference**: Any specifc type of interest like temples, mountains, beaches etc. 

These values are used to construct a detailed context prompt for a **Gemini-based LLM**, which generates a structured **JSON output**.

---

### 2. LLM JSON Output

The JSON output from the LLM includes:
- List of selected **cities**.
- **Arrival and departure dates** for each city.
- **Airport codes** corresponding to each city.

This structured information forms the backbone for the next stage of the pipeline.

---

### 3. API Integrations

The generated JSON is used as input to query three specialized APIs:
- **Flights API**: To retrieve available flights between the selected cities.
- **Attractions API**: To fetch popular tourist attractions and experiences.
- **Hotels API**: To find suitable accommodations within the given budget.

The outputs from these APIs are ranked based on multiple factors, such as:
- Popularity scores.
- Bayesian review scores.
- Price points.
- Proximity to city centers or attractions.
- Traveler ratings.

Precise rates (for flights, hotels, and attractions) are extracted, ensuring the final itinerary remains **budget-aware** and feasible.

---

### 4. Final Itinerary Generation

The API outputs are collated and appended together. This enriched dataset is then **fed back into the Gemini Model**, which uses all available information to generate a **complete, coherent, and budget-specific travel itinerary**.

The final output includes:
- City-to-city transportation plans.
- Handpicked attractions with entry fees and timings.
- Accommodation suggestions mapped to arrival/departure dates.
- A well-distributed budget breakdown, ensuring an optimal experience without overspending.

---

## Key Features

- ✈️ **Seamless Multi-City Planning**  
- 💸 **Strict Budget Management**  
- 🏨 **Curated Hotel and Attraction Suggestions**  
- 🗓️ **Smart Scheduling Aligned with User Dates**  
- 📈 **Data-Driven Ranking for Best Recommendations**  
- 🤖 **End-to-End LLM Powered Personalization**  

---

## Future Enhancements

TravelGenie is constantly evolving. Planned future upgrades include:
- Real-time dynamic pricing updates.
- Integration with Visa and travel insurance providers.
- Custom experience packages like adventure tours, wellness retreats, etc.
- Group travel planning with shared budgets and preferences.
- Voice command support for itinerary modifications.

---

TravelGenie isn't just an itinerary generator - it's your personal AI travel concierge, optimizing your journey from the moment you start dreaming about it to the day you return home.

## How to Run

Follow these simple steps to get started with TravelGenie:

1. **Clone the Repository**  
   - Click on the green **<> Code** button in the GitHub repository.
   - Copy the **HTTPS URL**.
   - Open your terminal, navigate to the directory where you want to place the project, and run:  
     ```
     git clone {copied-https-url}
     ```

2. **Open the Project**  
   - After cloning, a folder named **TravelGenie** will be created.
   - Open this folder in any IDE (recommended: **VSCode**).

3. **Install Required Packages**  
   - Open a terminal inside the **TravelGenie** folder (if not already).
   - Install all the necessary Python packages by running:  
     ```
     pip install -r requirements.txt
     ```

4. **Start the Application**  
   - After installing the packages, run the following command to start the application:  
     ```
     python app.py
     ```
   - A local **UI link** will be generated. Open this link in any web browser (**Recommended: Chrome**).

5. **Use the UI**  
   - Fill in your travel preferences like country, dates, budget, etc.
   - Click on **Generate** to receive your personalized travel plan.

---

> ⚡ **Note:**  
> Sometimes the APIs may hit their free usage limits. If you encounter any issues:
> - Go to the **base URL** mentioned in the code.
> - Subscribe for a new free API key.
> - Replace the value of `"x-rapidapi-key"` in the code with your new key.
> - Restart the application (`python app.py`) and continue planning!


