import base64
import http
import mimetypes
from pprint import pprint
import http.client
import http.cookiejar
import urllib.parse
import requests
from PIL import Image

import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import io
import json

import secrets

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


def resize_immage(file_path: str) -> None:
    max_dimension = 1900
    target_file_size_kb = 1500
    quality = 100
    with Image.open(file_path) as im:
        print(im.format, im.size, im.mode, os.stat(file_path).st_size / (1024 * 1024))
        w, h = im.size
        # Check if either dimension is larger than max_dimension
        if w > max_dimension or h > max_dimension:
            # Calculate the scaling factor
            scale_factor = max_dimension / max(w, h)
            new_width = int(w * scale_factor)
            new_height = int(h * scale_factor)
            # Resize the image
            im = im.resize((new_width, new_height))

        im.save(file_path, format="JPEG", quality=quality, optimize=True)
        # Check if the file size is below the target size
        while os.stat(file_path).st_size / 1024 > target_file_size_kb:
            quality -= 1
            im.save(file_path, format="JPEG", quality=quality, optimize=True)

        print(im.format, im.size, im.mode, os.stat(file_path).st_size / (1024 * 1024), quality)


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
        self.login()

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

    def _make_form_post_request(self, url: str, form_data, params: dict = None,
                                headers: dict = None) -> requests.models.Response:
        try:
            with self.session as session:
                if headers:
                    session.headers.update(headers)
                response = session.post(
                    url=url,
                    data=form_data,
                    cookies=session.cookies,
                    params=params, )
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

        # Define the payload with the form data
        payload = {
            '_token': parse_csrf_token(response_get.content),
            '_method': 'PUT',
            'userType': 'vendor',
            'locale': 'pl',
            'channel': 'default',
            'sku': int(storisma_product.product_id),
            'name': storisma_product.wordpress_product.name,
            'url_key': storisma_product.wordpress_product.slug,
            'tax_category_id': '',
            'new': '1',
            'visible_individually': '0',
            'status': '1',
            'color': '1',
            'custom_shipping_time_3': '44',
            'short_description': storisma_product.wordpress_product.short_description,
            'description': storisma_product.wordpress_product.short_description,
            'meta_title': '',
            'meta_keywords': '',
            'meta_description': '',
            'categories[]': storisma_categories,
        }

        # Send a GET request to download the image
        i = 1
        files = dict()
        for image in storisma_product.wordpress_product.images:
            image_response = requests.get(image)
            if image_response.status_code == 200:
                # Prepare the image file for upload
                image_filename = image.split('/')[-1]

                # Open the local file in binary write mode and write the image data
                with open(f"./wp-images/{image_filename}", 'wb') as file:
                    file.write(image_response.content)

                resize_immage(f"./wp-images/{image_filename}")
                files[f'images[image_{i}]'] = (image_filename, open(f"./wp-images/{image_filename}", 'rb'), 'image/jpeg')
                i += 1

        for product_variation in storisma_product.variations.all():
            payload[f'variants[{product_variation.variation_id}][sku]'] = str(product_variation.variation_id)
            payload[f'variants[{product_variation.variation_id}][vendor_id]'] = '88'

            payload[f'variants[{product_variation.variation_id}][name]'] = storisma_product.wordpress_product.name
            attributes = product_variation.attributes.all()
            for attribute in attributes:
                payload[f'variants[{product_variation.variation_id}][{attribute.attribute}]'] = int(attribute.term.term_id)
                payload[f'variants[{product_variation.variation_id}][name]'] += f' {attribute.term}'
            payload[f'variants[{product_variation.variation_id}][inventories][1]'] = int(product_variation.stock_quantity)
            payload[f'variants[{product_variation.variation_id}][price]'] = int(product_variation.price)
            payload[f'variants[{product_variation.variation_id}][weight]'] = 0
            payload[f'variants[{product_variation.variation_id}][status]'] = 1

        try:
            with self.session as session:
                response = session.post(
                    url=f"{self.base_url}/marketplace/account/catalog/products/edit/{storisma_product.product_id}",
                    data=payload,
                    cookies=session.cookies,
                    files=files
                )

            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            print("Form submitted successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Error submitting form: {e}")


        # Check the response
        if response.status_code == 200:
            print("Request was successful")
            #print(response.text)  # If you expect a response from the server
        else:
            print("Request failed")
            #print(response.text)  # Print the response content for debugging