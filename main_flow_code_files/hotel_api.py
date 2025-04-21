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
        'x-rapidapi-key': "86b9527b5bmsh140e1c25a2909fbp1edddfjsn36a907e79010",
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
                    HotelArray[sorts] = [(hotels['property']['name'], hotels['property']['priceBreakdown']['grossPrice']['value'],hotels['property']['reviewScore'])]
                else:
                    HotelArray[sorts].append((hotels['property']['name'], hotels['property']['priceBreakdown']['grossPrice']['value'],hotels['property']['reviewScore']))
                num += 1
        FinalHotelArray[real_city_name] = HotelArray
    return restructure_hotel_data(FinalHotelArray)
