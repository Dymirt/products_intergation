from pprint import pprint

import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

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


def parse_product_variations(content):
    try:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        variations = soup.find_all('input', {'type': 'hidden'})
        print(variations)

        return variations
    except requests.exceptions.RequestException as e:
        print(f"Error fetching variants: {e}")
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

    def _make_form_post_request(self, url: str, form_data: dict, params: dict = None) -> requests.models.Response:
        try:
            with self.session as session:
                response = session.post(url=url, data=form_data, cookies=session.cookies, params=params)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            print("Form submitted successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Error submitting form: {e}")
        return response

    def create_product_with_variation(self, product_sku, super_attributes: dict):
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
        }
        form_data.update(super_attributes)

        response_post = self._make_form_post_request(f"{self.urls.get('products_url')}/create",
                                     params=params,
                                     form_data=form_data)

        return response_post

    def populate_product_data(self, storisma_product):

        with self.session as session:
            response_get = session.get(
                url=f"{self.base_url}/marketplace/account/catalog/products/edit/{storisma_product.product_id}"
            )
        response_get.raise_for_status()

        storisma_categories = []
        for wordpress_category in storisma_product.wordpress_product.categories.all():
            for storisma_category in wordpress_category.storisma_categories.all():
                storisma_categories.append(str(storisma_category.category_id))

        product_form = {
            # Hidden inputs
            '_token': parse_csrf_token(response_get.content),
            '_method': 'PUT',
            'userType': 'vendor',
            'locale': 'pl',
            'channel': 'default',
            'new': "1",

            'sku': str(storisma_product.product_id),
            'name': storisma_product.wordpress_product.name,
            'url_key': storisma_product.wordpress_product.slug,
            'tax_category_id': '1',
            'visible_individually': '0',
            'status': '1',
            'brand': '',
            # SHIPPING TIME
            # (44) 1-2 business days
            # (45) 2-5 business days
            # (46) 7 business days
            # (47) over 7 business days
            'custom_shipping_time_3': "44",  # (44) 1-2 business days
            'short_description': storisma_product.wordpress_product.short_description, #TODO clean HTML
            'description': storisma_product.wordpress_product.short_description, #TODO clean HTML
            'meta_title': '',
            'meta_keywords': '',
            'meta_description': '',
            'price': '',
            'weight': '',

            # Images
            # For every image
            'images[image_1]': '',  # File
            'categories[]': storisma_categories,
        }

        for product_variation in storisma_product.variations.all():
            product_form[f'variants[{product_variation.variation_id}][sku]'] = product_variation.variation_id
            product_form[f'variants[{product_variation.variation_id}][vendor_id]'] = '88'
            #TODO product_form[f'variants[{product_variation.variation_id}][name]'] = "Name"
            #TODO product_form[f'variants[{product_variation.variation_id}][color]'] = "color"
            #TODO product_form[f'variants[{product_variation.variation_id}][size]'] = "size"
            product_form[f'variants[{product_variation.variation_id}][inventories][1]'] = str(product_variation.stock_quantity)
            product_form[f'variants[{product_variation.variation_id}][price]'] = str(product_variation.price)
            product_form[f'variants[{product_variation.variation_id}][weight]'] = "0"
            product_form[f'variants[{product_variation.variation_id}][status]'] = "1"

        pprint(product_form)


#storisma = Storisma(STORISMA_EMAIL, STORISMA_PASSWORD)
#response = storisma.login()
#print(response.url.split('/')[-1])
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