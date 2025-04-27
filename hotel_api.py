import json
import http.client
import urllib.parse

def JSONconverter(input):
    cities = list(input.keys())
    arrivals = []
    departures = []
    airports = []
    encoded_cities = []

    for keys, values in input.items():
        encoded_city = urllib.parse.quote(keys)
        encoded_cities.append(encoded_city)
        arrivals.append(values["Arrival Date"])
        departures.append(values["Departure Date"])
        airports.append(values["Airport"])

    return cities, encoded_cities, arrivals, departures, airports

def restructure_hotel_data(hotel_data):
    restructured = {}

    for city, sorting_data in hotel_data.items():
        restructured[city] = {}
        for sort_type, hotels in sorting_data.items():
            restructured[city][sort_type] = [
                {
                    "name": name,
                    "price": price,
                    "review_score": review_score
                }
                for name, price, review_score in hotels
            ]

    return restructured

def HotelRetriever(input, numadults):
    realcities, cities, arrivals, departures, _ = JSONconverter(input)
    conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "79a57437e9mshc890be81f976138p192b96jsna1f56ff57aa4",
        'x-rapidapi-host': "booking-com15.p.rapidapi.com"
    }
    FinalHotelArray = {}
    for i in range(len(cities)):
        real_city_name = realcities[i]
        city_name = cities[i]
        arrival_date = arrivals[i]
        departure_date = departures[i]

        try:
            conn.request("GET", f"/api/v1/hotels/searchDestination?query={city_name}", headers=headers)
            res = conn.getresponse()
            data = res.read()
            data_json = json.loads(data.decode("utf-8"))

            dest_id = None
            for dest in data_json.get('data', []):
                if dest.get('search_type') == "city":
                    dest_id = dest.get('dest_id')
                    break
            if not dest_id:
                print(f"[Hotel] ❌ No dest_id for {real_city_name}, skipping")
                continue

            Sortings = ['bayesian_review_score', 'popularity', 'price']
            HotelArray = {}
            for sorts in Sortings:
                try:
                    url = f"/api/v1/hotels/searchHotels?dest_id={dest_id}&search_type=CITY&adults={numadults}&arrival_date={arrival_date}&departure_date={departure_date}&sort_by={sorts}&currency_code=USD"
                    conn.request("GET", url, headers=headers)
                    res = conn.getresponse()
                    data = res.read()
                    data_json = json.loads(data.decode("utf-8"))

                    hotel_list = data_json.get('data', {}).get('hotels', [])
                    HotelArray[sorts] = []
                    for hotel in hotel_list[:3]:
                        name = hotel['property'].get('name', "")
                        price = hotel['property'].get('priceBreakdown', {}).get('grossPrice', {}).get('value', 0)
                        review_score = hotel['property'].get('reviewScore', 0)
                        HotelArray[sorts].append((name, price, review_score))

                except Exception as err:
                    print(f"[Hotel] ⚠️ Error during hotel search for {real_city_name}, sort {sorts}: {err}")

            FinalHotelArray[real_city_name] = HotelArray

        except Exception as e:
            print(f"[Hotel] ⚠️ Failed to fetch destination for {real_city_name}: {e}")

    return restructure_hotel_data(FinalHotelArray)
