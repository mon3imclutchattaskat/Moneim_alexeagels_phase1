# booking/booking.py
from customer.customer import Customer
from flight.flight import Flight
from services.meal_option import MealOption
from services.additional_service import AdditionalService

class Booking:
    def __init__(self, customer: Customer, flight: Flight, meal_option: MealOption = None, additional_services: list[AdditionalService] = None):
        self.customer = customer
        self.flight = flight
        self.meal_option = meal_option
        self.additional_services = additional_services if additional_services else []
        self.total_price = self.calculate_total_price()

    def calculate_total_price(self):
        total = self.flight.price
        if self.meal_option:
            total += self.meal_option.price
        total += sum(service.price for service in self.additional_services)
        return total
