# airline/airline.py
from flight.flight import Flight

class Airline:
    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code
        self.flights = []

    def add_flight(self, flight: Flight):
        self.flights.append(flight)

    def get_flights(self):
        return self.flights
