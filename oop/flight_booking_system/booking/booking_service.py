# booking/booking_service.py
from booking.booking import Booking
from flight.flight import Flight
from customer.customer import Customer
from services.meal_option import MealOption
from services.additional_service import AdditionalService

class BookingService:
    def make_booking(self, customer: Customer, flight: Flight, meal_option: MealOption = None, additional_services: list[AdditionalService] = None) -> Booking:
        if flight.available_seats > 0:
            flight.book_seat()
            booking = Booking(customer, flight, meal_option, additional_services)
            return booking
        else:
            raise Exception("No seats available on this flight")
