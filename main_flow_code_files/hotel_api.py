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

def restructure_hotel_data(raw_data):
    structured_data = []
    for city, rankings in raw_data.items():
        city_entry = {
            "city": city,
            "hotels_by": {}
        }
        for criterion, hotels in rankings.items():
            city_entry["hotels_by"][criterion] = [
                {"name": hotel_name, "price": round(price, 2)} for hotel_name, price in hotels
            ]
        structured_data.append(city_entry)
    return structured_data

def HotelRetriever(input, numadults):
    realcities, cities, arrivals, departures, _ = JSONconverter(input)
    conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "cd3649e95amsh19e77450d847972p129963jsn55e782c26fc6",
        'x-rapidapi-host': "booking-com15.p.rapidapi.com"
    }
    FinalHotelArray = {}
    for i in range(len(cities)):
        real_city_name = realcities[i]
        city_name = cities[i]
        arrival_date = arrivals[i]
        departure_date = departures[i]

        conn.request("GET", f"/api/v1/hotels/searchDestination?query={city_name}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        data_json = json.loads(data.decode("utf-8"))

        dest_id = None
        for dest in data_json['data']:
            if dest['search_type'] == "city":
                dest_id = dest['dest_id']
                break
        if not dest_id:
            continue

        Sortings = ['bayesian_review_score', 'popularity', 'price']
        HotelArray = {}
        for sorts in Sortings:
            url = f"/api/v1/hotels/searchHotels?dest_id={dest_id}&search_type=CITY&adults={numadults}&arrival_date={arrival_date}&departure_date={departure_date}&sort_by={sorts}&currency_code=USD"
            conn.request("GET", url, headers=headers)
            res = conn.getresponse()
            data = res.read()
            data_json = json.loads(data.decode("utf-8"))
            num = 0
            for hotels in data_json['data']['hotels']:
                if num == 3:
                    break
                if sorts not in HotelArray:
                    HotelArray[sorts] = [(hotels['property']['name'], hotels['property']['priceBreakdown']['grossPrice']['value'])]
                else:
                    HotelArray[sorts].append((hotels['property']['name'], hotels['property']['priceBreakdown']['grossPrice']['value']))
                num += 1
        FinalHotelArray[real_city_name] = HotelArray
    return restructure_hotel_data(FinalHotelArray)