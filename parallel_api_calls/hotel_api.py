import aiohttp
import asyncio

HOTEL_HEADERS = {
    'x-rapidapi-key': "YOUR_HOTEL_KEY",
    'x-rapidapi-host': "booking-com15.p.rapidapi.com"
}

async def fetch_hotels(session: aiohttp.ClientSession, city: str) -> dict:
    """Fetch & clean top hotels for a single city."""
    try:
        # 1. get dest_id
        async with session.get(
            f"https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination?query={city}",
            headers=HOTEL_HEADERS
        ) as res:
            dest_data = await res.json()
        dest_id = next(
            (d["dest_id"] for d in dest_data["data"] if d["search_type"] == "city"),
            None
        )
        if not dest_id:
            return {"city": city, "hotels": []}

        # 2. search hotels
        params = {
            "dest_id": dest_id,
            "search_type": "CITY",
            "adults": 2,
            "children_age": "10,17",
            "room_qty": 1,
            "arrival_date": "2025-03-22",
            "departure_date": "2025-03-23",
            "sort_by": "bayesian_review_score",
            "currency_code": "USD"
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        async with session.get(
            f"https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels?{query}",
            headers=HOTEL_HEADERS
        ) as res:
            hotel_data = await res.json()
        hotels = hotel_data["data"]["hotels"][:5]

        # 3. fetch details in parallel
        tasks = [
            session.get(
                f"https://booking-com15.p.rapidapi.com/api/v1/hotels/getDescriptionAndInfo"
                f"?hotel_id={h['hotel_id']}&languagecode=en-us",
                headers=HOTEL_HEADERS
            )
            for h in hotels
        ]
        responses = await asyncio.gather(*tasks)
        for h, resp in zip(hotels, responses):
            h["details"] = await resp.json()

        return {"city": city, "hotels": hotels}
    except Exception as e:
        return {"city": city, "hotels": [], "error": str(e)}
