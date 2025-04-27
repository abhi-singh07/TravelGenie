import aiohttp
import asyncio

ATTRACTION_HEADERS = {
    # 'x-rapidapi-key': "f0f12faf53mshdfd57ac1512d103p1d6d3ajsn88fef3a18e5a",(Abhishek's key)
    'x-rapidapi-key': "79a57437e9mshc890be81f976138p192b96jsna1f56ff57aa4",
    'x-rapidapi-host': "tourist-attraction.p.rapidapi.com",
    'Content-Type': "application/x-www-form-urlencoded"
}
BASE_URL = "https://tourist-attraction.p.rapidapi.com"

def encode_form(data: dict) -> bytes:
    return "&".join([f"{k}={v}" for k, v in data.items()]).encode("utf-8")

async def fetch_location_id(session: aiohttp.ClientSession, city: str) -> str:
    print(f"[Attraction] 🔍 Fetching location_id for: {city}")
    payload = encode_form({
        "q": city,
        "language": "en_US"
    })
    async with session.post(f"{BASE_URL}/typeahead", data=payload, headers=ATTRACTION_HEADERS) as res:
        text = await res.text()
        try:
            parsed = await res.json()
        except Exception:
            print(f"[Attraction] ⚠️ Failed to parse JSON for location_id: {text}")
            return ""

    loc_id = (
        parsed.get("results", {})
              .get("data", [{}])[0]
              .get("result_object", {})
              .get("location_id", "")
    )
    print(f"[Attraction] ✅ location_id for {city} = {loc_id}")
    return loc_id

async def fetch_attractions(session: aiohttp.ClientSession, city: str) -> dict:
    try:
        loc_id = await fetch_location_id(session, city)
        if not loc_id:
            print(f"[Attraction] ❌ No location_id for {city}, returning empty list.")
            return {"city": city, "attractions": []}

        print(f"[Attraction] 🔍 Fetching attractions for {city}")
        payload = encode_form({
            "location_id": loc_id,
            "language": "en_US",
            "currency": "USD",
            "offset": "0"
        })
        async with session.post(f"{BASE_URL}/search", data=payload, headers=ATTRACTION_HEADERS) as res:
            text = await res.text()
            try:
                raw = await res.json()
            except Exception:
                print(f"[Attraction] ⚠️ Failed to parse JSON for attractions: {text}")
                return {"city": city, "attractions": []}

        data_list = raw.get("results", {}).get("data", [])
        print(f"[Attraction] 🌐 Raw results count for {city}: {len(data_list)}")

        attractions = [
            {
                "name":             item.get("name"),
                "num_reviews":      item.get("num_reviews"),
                "rating":           item.get("rating"),
                "ranking_position": item.get("ranking_position"),
                "neighborhood_info":item.get("neighborhood_info"),
                "description":      item.get("description"),
                "subcategory":      item.get("subcategory")
            }
            for item in data_list
        ]

        print(f"[Attraction] ✅ Returning {len(attractions)} attractions for {city}")
        return {"city": city, "attractions": attractions}

    except Exception as e:
        print(f"[Attraction] ❗ Error for {city}: {e}")
        return {"city": city, "attractions": [], "error": str(e)}
