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

def structure_flight_data(flight_dict):
    structured_data = []

    for (from_city, to_city, date), details in flight_dict.items():
        if isinstance(details, str):
            structured_data.append({
                "from": from_city,
                "to": to_city,
                "date": date,
                "flights": None,
                "note": details
            })
        else:
            flight_options = []
            for category, (price, dep_time, arr_time) in details.items():
                flight_options.append({
                    "type": category,
                    "price_usd": price,
                    "departure_time": dep_time,
                    "arrival_time": arr_time
                })

            structured_data.append({
                "from": from_city,
                "to": to_city,
                "date": date,
                "flights": flight_options,
                "note": None
            })

    return structured_data

def FlightRetriever(input,numadults):
    FullyFinalFlightHash = {}
    real_cities, cities, _, departures, airports = JSONconverter(input)

    for i in range(len(cities) - 1):
        start = airports[i]
        end = airports[i + 1]
        start_city = cities[i]
        end_city = cities[i + 1]
        real_start_city = real_cities[i]
        real_end_city = real_cities[i + 1]
        departuredate = departures[i]

        TempFlightHash = {}
        FinalFlightHash = {}
        conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "79a57437e9mshc890be81f976138p192b96jsna1f56ff57aa4",
            'x-rapidapi-host': "booking-com15.p.rapidapi.com"
        }
        url = f"/api/v1/flights/searchFlights?fromId={start}.AIRPORT&toId={end}.AIRPORT&pageNo=1&adults={numadults}&children=0%2C17&sort=BEST&cabinClass=ECONOMY&currency_code=USD&departDate={departuredate}"

        try:
            conn.request("GET", url, headers=headers)
            res = conn.getresponse()
            data = res.read()
            data_json = json.loads(data.decode("utf-8"))
        except Exception as e:
            conn.close()
            FullyFinalFlightHash[(real_start_city, real_end_city, departuredate)] = f"Error fetching data: {str(e)}"
            continue
        finally:
            conn.close()

        if 'error' in data_json.get('data', {}):
            FullyFinalFlightHash[(real_start_city, real_end_city, departuredate)] = "No flights for these locations. Check alternate way of travel!"
            continue

        for flights in data_json['data']['flightDeals']:
            TempFlightHash[flights['key']] = (flights['priceRounded']['units'], flights['offerToken'])

        for sorts, tokens in TempFlightHash.items():
            token = tokens[1]
            for flights in data_json['data']['flightOffers']:
                if token == flights['token']:
                    FinalFlightHash[sorts] = (
                        tokens[0],
                        flights['segments'][0]['departureTime'],
                        flights['segments'][0]['arrivalTime']
                    )

        FullyFinalFlightHash[(real_start_city, real_end_city, departuredate)] = FinalFlightHash

    return structure_flight_data(FullyFinalFlightHash)
