import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
load_dotenv()

import pickle

STORISMA_EMAIL = os.getenv("STORISMA_EMAIL")
STORISMA_PASSWORD = os.getenv("STORISMA_PASSWORD")


def parse_csrf_token(content):
    try:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Find the input element with name="_token" and get its value
        csrf_token = soup.find('input', {'name': '_token'})['value']
        return csrf_token
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CSRF token: {e}")
        return None


def parse_zero_token(content):
    try:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Find the input element with name="_token" and get its value
        csrf_token = soup.find('input', {'name': 'zero'})['value']
        return csrf_token
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CSRF token: {e}")
        return None


class Storisma:
    def __init__(self, email, password):
        self.base_url = "https://storisma.pl"
        self.session = requests.Session()
        self.email = email
        self.password = password

    def login(self):
        with self.session as session:
            response = session.get(f"{self.base_url}/customer/login")

        form_data = {
            "_token": parse_csrf_token(response.content),
            "email": self.email,
            "password": self.password,
            'zero': parse_zero_token(response.content)
        }
        print(form_data)

        try:
            with self.session as session:
                response = session.post(f"{self.base_url}/customer/login", data=form_data, cookies=session.cookies)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            print("Form submitted successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Error submitting form: {e}")
        return response

    def create_product_variations(self, product_sku):
        params = {
            "family": '1',
            "sku": str(product_sku)

        }

        with self.session as session:
            response = session.get(f"{self.base_url}/marketplace/account/catalog/products/create", params=params)
        response.raise_for_status()

        csrf_token = parse_csrf_token(response.content)

        form_data = {
            "_token": csrf_token,
            "type": "configurable",
            "attribute_family_id": "1",
            "sku": product_sku,
            "super_attributes[color][]": ["22", "32", "33"],  # Multiple values for super_attributes[color][]
            "super_attributes[size][]": ["54", "55", "56"],  # Multiple values for super_attributes[size][]

        }

        try:
            with self.session as session:
                response = session.post(f"{self.base_url}/marketplace/account/catalog/products/create", params=params, data=form_data)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            print("Form submitted successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Error submitting form: {e}")

    def get_profile_page(self):
        with self.session as session:
            response = session.get("https://storisma.pl/customer/account/profile")
            print(response.content)






storisma = Storisma(STORISMA_EMAIL, STORISMA_PASSWORD)
response = storisma.login()
print(response.status_code == 200)
print(response.text)
#print(storisma.get_profile_page())
#storisma.create_product_variations("532123")