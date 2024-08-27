# flight/flight_search.py
from airport.airport import Airport
from airline.airline import Airline
from flight.flight import Flight

class FlightSearch:
    def __init__(self, airlines: list[Airline]):
        self.airlines = airlines

    def search_flights(self, departure_airport: Airport, arrival_airport: Airport) -> list[Flight]:
        available_flights = []
        for airline in self.airlines:
            for flight in airline.get_flights():
                if flight.departure_airport == departure_airport and flight.arrival_airport == arrival_airport:
                    available_flights.append(flight)
        return available_flights
