# flight/flight.py
from airport.airport import Airport

class Flight:
    def __init__(self, flight_number: str, airline, departure_airport: Airport, arrival_airport: Airport, departure_time: str, arrival_time: str, price: float, available_seats: int):
        self.flight_number = flight_number
        self.airline = airline
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.price = price
        self.available_seats = available_seats

    def book_seat(self):
        if self.available_seats > 0:
            self.available_seats -= 1
        else:
            raise Exception("No seats available")
