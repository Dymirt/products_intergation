from PIL import Image
import requests
from bs4 import BeautifulSoup
import os

import logging

# Get an instance of the logger
logger = logging.getLogger(__name__)

def my_view():
    # Your view code here
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')


class Storisma:
    def __init__(self, email, password):
        self.base_url = "https://storisma.pl"
        self.session = requests.Session()
        self.email = email
        self.password = password
        self.urls = {
            "products_url": f"{self.base_url}/marketplace/account/catalog/products",
            "login_url": f"{self.base_url}/customer/login",
            "profile": f"{self.base_url}/customer/account/profile"
        }

    def establish_session(self) -> None:
        if not self.valid_session():
            logger.warning("Invalid session, reconnecting...")
            self.login()

    def valid_session(self) -> bool:
        with self.session as session:
            response = session.get(self.urls.get("profile"))
        return "Profil" in response.text and response.status_code == 200

    def login(self):
        with self.session as session:
            response_get = session.get(self.urls.get("login_url"))

        form_data = {
            "_token": parse_csrf_token(response_get.content),
            "email": self.email,
            "password": self.password,
            "zero": parse_zero_token(response_get.content),
        }

        response_post = self._make_form_post_request(
            url=self.urls.get("login_url"), form_data=form_data
        )
        if "Profil" in response_post.text and response_post.status_code == 200:
            print("Login successful!")
        else:
            print("Some ")

    def _make_form_post_request(
        self, url: str, form_data: dict, params: dict = None, files: dict = None
    ) -> requests.models.Response:
        try:
            with self.session as session:
                response = session.post(
                    url=url,
                    data=form_data,
                    cookies=session.cookies,
                    params=params,
                    files=files,
                )
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            print("Form submitted successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Error submitting form: {e}")
        return response

    def create_product_with_variation(self, product_sku, super_attributes: dict):
        self.establish_session()

        # GET request to get csrf token for post request
        params = {"family": "1", "sku": str(product_sku)}
        with self.session as session:
            response_get = session.get(
                f"{self.urls.get('products_url')}/create", params=params
            )
        response_get.raise_for_status()

        # Making post request
        form_data = {
            "_token": parse_csrf_token(response_get.content),
            "type": "configurable",
            "attribute_family_id": "1",
            "sku": product_sku,
        }
        form_data.update(super_attributes)

        response_post = self._make_form_post_request(
            url=f"{self.urls.get('products_url')}/create",
            params=params,
            form_data=form_data,
        )

        return response_post

    def populate_product_data(self, storisma_product):
        self.establish_session()

        with self.session as session:
            response_get = session.get(
                url=f"{self.base_url}/marketplace/account/catalog/products/edit/{storisma_product.product_id}"
            )
        response_get.raise_for_status()

        # Define the payload with the form data
        payload = {
            "_token": parse_csrf_token(response_get.content),
            "_method": "PUT",
            "userType": "vendor",
            "locale": "pl",
            "channel": "default",
            "sku": int(storisma_product.product_id),
            "name": storisma_product.wordpress_product.name,
            "url_key": storisma_product.wordpress_product.slug,
            "tax_category_id": "",
            "new": "1",
            "visible_individually": "0",
            "status": "1",
            "color": "1",  # TODO product colour
            "custom_shipping_time_3": "44",
            "short_description": storisma_product.wordpress_product.short_description,
            "description": storisma_product.wordpress_product.short_description,
            "meta_title": "",
            "meta_keywords": "",
            "meta_description": "",
            "categories[]": get_related_categories_id(storisma_product),
        }

        for variation in storisma_product.variations.all():
            payload[f"variants[{variation.variation_id}][sku]"] = str(variation.variation_id)
            payload[f"variants[{variation.variation_id}][vendor_id]"] = "88"
            payload[f"variants[{variation.variation_id}][name]"] = storisma_product.wordpress_product.name
            payload[f"variants[{variation.variation_id}][inventories][1]"] = int(variation.stock_quantity)
            payload[f"variants[{variation.variation_id}][price]"] = int(variation.price)
            payload[f"variants[{variation.variation_id}][weight]"] = 0
            payload[f"variants[{variation.variation_id}][status]"] = 1

            # Populate variation attributes (colour, size)
            attributes = variation.attributes.all()
            for attribute in attributes:
                payload[f"variants[{variation.variation_id}][{attribute.attribute}]"] = int(attribute.term.term_id)
                payload[f"variants[{variation.variation_id}][name]"] += f" {attribute.term}"

            self._make_form_post_request(
                url=f"{self.base_url}/marketplace/account/catalog/products/edit/{storisma_product.product_id}",
                form_data=payload,
                files=get_product_images(storisma_product),
            )


def parse_csrf_token(content):
    try:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")

        # Find the input element with name="_token" and get its value
        csrf_token = soup.find("input", {"name": "_token"})["value"]
        return csrf_token
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CSRF token: {e}")
        return None


def parse_zero_token(content):
    try:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")

        # Find the input element with name="_token" and get its value
        csrf_token = soup.find("input", {"name": "zero"})["value"]
        return csrf_token
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CSRF token: {e}")
        return None


def resize_immage(file_path: str) -> None:
    max_dimension = 1900
    target_file_size_kb = 1500
    quality = 100

    with Image.open(file_path) as im:
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


def get_product_images(storisma_product):
    # Send a GET request to download the image
    i = 1
    files = dict()
    for image in storisma_product.wordpress_product.images:
        image_response = requests.get(image)
        if image_response.status_code == 200:
            # Prepare the image file for upload
            image_filename = image.split("/")[-1]

            # Open the local file in binary write mode and write the image data
            with open(f"./wp-images/{image_filename}", "wb") as file:
                file.write(image_response.content)

            resize_immage(f"./wp-images/{image_filename}")
            files[f"images[image_{i}]"] = (
                image_filename,
                open(f"./wp-images/{image_filename}", "rb"),
                "image/jpeg",
            )
            i += 1
    return files


def get_related_categories_id(storisma_product):
    storisma_categories = []
    for wordpress_category in storisma_product.wordpress_product.categories.all():
        for storisma_category in wordpress_category.storisma_categories.all():
            storisma_categories.append(str(storisma_category.category_id))
    return storisma_categories
