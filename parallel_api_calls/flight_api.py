import aiohttp
import asyncio

FLIGHT_HEADERS = {
    'x-rapidapi-key': "YOUR_FLIGHT_KEY",
    'x-rapidapi-host': "some-flight-api.p.rapidapi.com"
}

async def fetch_flights(session: aiohttp.ClientSession, city: str) -> dict:
    """
    Example stub—adapt endpoints & payload to your actual flight API.
    """
    try:
        url = "https://some-flight-api.p.rapidapi.com/flights/search"
        payload = {"destination": city, "date": "2025-03-22", "return": "2025-03-23", "adults": 2}
        async with session.post(url, json=payload, headers=FLIGHT_HEADERS) as res:
            data = await res.json()
        # simple clean: take first 5 options
        options = data.get("data", [])[:5]
        return {"city": city, "flights": options}
    except Exception as e:
        return {"city": city, "flights": [], "error": str(e)}
