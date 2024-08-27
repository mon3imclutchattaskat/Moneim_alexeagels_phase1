# ui/main_ui.py
from tkinter import Tk, Label, Entry, StringVar, OptionMenu, messagebox
from tkinter import ttk
from airport.airport import Airport
from airline.airline import Airline
from flight.flight_search import FlightSearch
from customer.customer import Customer
from booking.booking_service import BookingService
from services.meal_option import MealOption
from services.additional_service import AdditionalService
from flight.flight import Flight

class MainUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("Flight Booking System")
        self.root.geometry("700x450")  # Set a larger window size for better layout

        # Use the ttk theme to make the GUI look more modern
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # Add custom styles
        self.setup_styles()

        # Setup UI
        self.setup_ui()

        # Initialize system components
        self.airport1 = Airport("JFK", "John F. Kennedy International Airport")
        self.airport2 = Airport("LAX", "Los Angeles International Airport")
        
        self.airline1 = Airline("Delta Airlines", "DL")
        self.airline2 = Airline("United Airlines", "UA")
        
        self.flights = [
            Flight("DL100", self.airline1, self.airport1, self.airport2, "2024-09-01 08:00", "2024-09-01 11:00", 300.0, 10),
            Flight("UA200", self.airline2, self.airport1, self.airport2, "2024-09-01 09:00", "2024-09-01 12:00", 320.0, 5)
        ]
        for flight in self.flights:
            flight.airline.add_flight(flight)

        self.flight_search = FlightSearch([self.airline1, self.airline2])
        self.booking_service = BookingService()

    def setup_styles(self):
        # Add custom styles
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', foreground='#333', font=('Helvetica', 12))
        self.style.configure('TButton', background='#4CAF50', foreground='white', font=('Helvetica', 12, 'bold'))
        self.style.map('TButton', background=[('active', '#45a049')])

        # OptionMenu styles
        self.style.configure('TMenubutton', background='#ddd', foreground='#333', font=('Helvetica', 12))

        # Entry styles
        self.style.configure('TEntry', font=('Helvetica', 12), padding=(5, 5))

    def setup_ui(self):
        # Use ttk.Frame with padding and better alignment
        frame = ttk.Frame(self.root, padding=(20, 20, 20, 20), style='TFrame')
        frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Labels and Entry widgets with better padding and positioning
        ttk.Label(frame, text="Departure Airport:", style='TLabel').grid(row=0, column=0, sticky="e", padx=(0, 10), pady=(5, 5))
        ttk.Label(frame, text="Arrival Airport:", style='TLabel').grid(row=1, column=0, sticky="e", padx=(0, 10), pady=(5, 5))
        ttk.Label(frame, text="Customer Name:", style='TLabel').grid(row=2, column=0, sticky="e", padx=(0, 10), pady=(5, 5))
        ttk.Label(frame, text="Contact Info:", style='TLabel').grid(row=3, column=0, sticky="e", padx=(0, 10), pady=(5, 5))
        ttk.Label(frame, text="Passport Number:", style='TLabel').grid(row=4, column=0, sticky="e", padx=(0, 10), pady=(5, 5))
        ttk.Label(frame, text="Meal Option:", style='TLabel').grid(row=5, column=0, sticky="e", padx=(0, 10), pady=(5, 5))

        # Input fields
        self.departure_airport_var = StringVar(self.root)
        self.arrival_airport_var = StringVar(self.root)
        self.customer_name_var = StringVar(self.root)
        self.contact_info_var = StringVar(self.root)
        self.passport_number_var = StringVar(self.root)
        self.meal_option_var = StringVar(self.root)

        # Dropdown menus
        airports = ["JFK", "LAX"]
        self.departure_airport_var.set(airports[0])
        self.arrival_airport_var.set(airports[1])

        OptionMenu(frame, self.departure_airport_var, *airports).grid(row=0, column=1, pady=(5, 5), padx=(0, 10))
        OptionMenu(frame, self.arrival_airport_var, *airports).grid(row=1, column=1, pady=(5, 5), padx=(0, 10))

        # Text entries
        ttk.Entry(frame, textvariable=self.customer_name_var, style='TEntry').grid(row=2, column=1, pady=(5, 5), padx=(0, 10))
        ttk.Entry(frame, textvariable=self.contact_info_var, style='TEntry').grid(row=3, column=1, pady=(5, 5), padx=(0, 10))
        ttk.Entry(frame, textvariable=self.passport_number_var, style='TEntry').grid(row=4, column=1, pady=(5, 5), padx=(0, 10))

        meal_options = ["None", "Vegetarian", "Non-Vegetarian"]
        self.meal_option_var.set(meal_options[0])
        OptionMenu(frame, self.meal_option_var, *meal_options).grid(row=5, column=1, pady=(5, 5), padx=(0, 10))

        # Buttons with styling and padding
        search_button = ttk.Button(frame, text="Search Flights", command=self.search_flights, style='TButton')
        search_button.grid(row=6, column=0, pady=(20, 5), sticky="e")
        book_button = ttk.Button(frame, text="Book Flight", command=self.book_flight, style='TButton')
        book_button.grid(row=6, column=1, pady=(20, 5), sticky="w")

    def search_flights(self):
        departure_code = self.departure_airport_var.get()
        arrival_code = self.arrival_airport_var.get()

        # In a real application, these would search a database or API for flights
        departure_airport = Airport(departure_code, "Dummy Airport")
        arrival_airport = Airport(arrival_code, "Dummy Airport")

        available_flights = self.flight_search.search_flights(departure_airport, arrival_airport)
        
        if available_flights:
            flight_info = "\n".join([f"{flight.flight_number} - {flight.departure_time} to {flight.arrival_time}, ${flight.price}" for flight in available_flights])
            messagebox.showinfo("Available Flights", flight_info)
        else:
            messagebox.showinfo("No Flights", "No flights available for the selected route.")

    def book_flight(self):
        try:
            customer_name = self.customer_name_var.get()
            contact_info = self.contact_info_var.get()
            passport_number = self.passport_number_var.get()
            meal_option = self.meal_option_var.get()

            customer = Customer(customer_name, contact_info, passport_number)

            # In a real application, you would allow the user to select a specific flight
            selected_flight = self.flights[0]  # Just select the first available flight for simplicity

            meal = None if meal_option == "None" else MealOption(meal_option, 20.0)
            additional_services = []  # Add logic to select additional services if needed

            booking = self.booking_service.make_booking(customer, selected_flight, meal, additional_services)
            messagebox.showinfo("Booking Confirmed", f"Booking confirmed for {booking.customer.name} on flight {booking.flight.flight_number} with total price {booking.total_price}")
        except Exception as e:
            messagebox.showerror("Booking Error", str(e))

    def run(self):
        self.root.mainloop()

