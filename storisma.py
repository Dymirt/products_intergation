import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

STORISMA_EMAIL = os.getenv("STORISMA_EMAIL")
STORISMA_PASSWORD = os.getenv("STORISMA_PASSWORD")

super_attributes_color = {
    'red': '1',
    'green': '2',
    'yellow': '3',
    'black': '4',
    'white': '5',
    'pink': '12',
    'gray': '13',
    'beige': '14',
    'orange': '15',
    'navy_blue': '16',
    'purple': '17',
    'gold': '18',
    'silver': '19',
    'multicolor': '20',
    'other': '22',
    'blue': '32',
    'brown': '33',
}

super_attributes_size = {
    'xs': '6',
    's': '7',
    'm': '8',
    'l': '9',
    'xl': '10',
    'xxl': '11',
    'universal': '12',
}

categories = {
    'Damskie': '4',
    'Sukienki i kombinezony': '2',
    'Bluzki i koszule': '9',
    'Swetry i bluzy': '8',
    'T-shirty': '10',
    'Marynarki i kurtki': '7',
    'Płaszcze': '6',
    'Spodnie': '11',
    'Spódnice': '13',
    'Kimona': '41',
    'Zestawy': '40'
}


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
        self.urls = {
            'products_url': f"{self.base_url}/marketplace/account/catalog/products",
            'login_url': f"{self.base_url}/customer/login"
        }

    def login(self):
        with self.session as session:
            response_get = session.get(self.urls.get('login_url'))

        form_data = {
            "_token": parse_csrf_token(response_get.content),
            "email": self.email,
            "password": self.password,
            'zero': parse_zero_token(response_get.content)
        }

        response_post = self._make_form_post_request(self.urls.get('login_url'), form_data)
        if "Profil" in response_post.text and response_post.status_code == 200:
            print("Login successful!")

        return response_post

    def _make_form_post_request(self, url: str, form_data: dict, params: dict = None) -> requests.models.Response:
        try:
            with self.session as session:
                response = session.post(url=url, data=form_data, cookies=session.cookies, params=params)
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
            response_get = session.get(f"{self.urls.get('products_url')}/create", params=params)
        response_get.raise_for_status()

        csrf_token = parse_csrf_token(response_get.content)

        form_data = {
            "_token": csrf_token,
            "type": "configurable",
            "attribute_family_id": "1",
            "sku": product_sku,
            "super_attributes[color][]": ["22", "32", "33"],  # Multiple values for super_attributes[color][]
            "super_attributes[size][]": ["54", "55", "56"],  # Multiple values for super_attributes[size][]

        }

        response_post = self._make_form_post_request(f"{self.urls.get('products_url')}/create",
                                     params=params,
                                     form_data=form_data)

        if "Edytuj Produkt" in response_post.text and response_post.status_code == 200:
            print("Product variations created successfully")

        return response

    def get_profile_page(self):
        with self.session as session:
            response = session.get("https://storisma.pl/customer/account/profile")
            print(response.content)


storisma = Storisma(STORISMA_EMAIL, STORISMA_PASSWORD)
response = storisma.login()
print(response.url.split('/')[-1])
# storisma.create_product_variations("532123")

product_for = {
    '_token': ...,
    '_method': 'PUT',
    'userType': 'vendor',
    'locale': 'pl',
    'channel': 'default',
    'sku': ...,
    'name': ...,
    'url_key': ...,
    'tax_category_id': '1',
    'new': "1",
    'visible_individually': '0',
    'status': ...,
    'brand': '',
    # SHIPPING TIME
    # (44) 1-2 business days
    # (45) 2-5 business days
    # (46) 7 business days
    # (47) over 7 business days
    'custom_shipping_time_3': "44",  # (44) 1-2 business days
    'short_description': ...,
    'description': ...,
    'meta_title': ...,
    'meta_keywords': ...,
    'meta_description': ...,
    'price': '',
    'weight': '',
    # Images
    # For every image
    'images[image_5]': '',  # File
    'categories[]': [],
    # Variations, for every product variants[ variant + 1 ]
    'variants[12709][vendor_id]': ...,  # parse input variants[12709][vendor_id]
    'variants[12709][name]': ...,
    'variants[12709][color]': ...,
    'variants[12709][size]': ...,
    'variants[12709][inventories][1]': ...,
    'variants[12709][price]': ...,
    'variants[12709][weight]': ...,
    'variants[12709][status]': ...,
}