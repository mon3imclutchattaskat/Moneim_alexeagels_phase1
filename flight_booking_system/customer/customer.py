# customer/customer.py
class Customer:
    def __init__(self, name: str, contact_info: str, passport_number: str):
        self.name = name
        self.contact_info = contact_info
        self.passport_number = passport_number
