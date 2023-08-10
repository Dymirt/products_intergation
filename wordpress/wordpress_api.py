from pprint import pprint

import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

WP_CONSUMER_KEY = os.getenv("WP_CONSUMER_KEY")
WP_CONSUMER_SECRET = os.getenv("WP_CONSUMER_SECRET")
WP_URL = os.getenv("WP_URL")


class WordpressAuthenticate:
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def authenticate_session(self) -> requests.Session:
        session = requests.Session()
        session.auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        return session


class WordpressResource:
    def __init__(self, session: requests.Session):
        self.session = session
        self.url = ...
        self.default_payload = ...

    def _make_api_call(self, url: str, params: dict = None) -> requests.models.Response:
        try:
            with self.session as session:
                response = session.get(url, params=params)
                response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
                return response
        except requests.exceptions.RequestException as e:
            print(f"Error making API call: {e}")

    def all(self, payload: dict = None) -> list:
        if payload is None:
            payload = self.default_payload

        all_items = []

        response = self._make_api_call(self.url, params=payload)
        all_items.extend(response.json())

        total_pages = int(response.headers.get('X-WP-TotalPages'))
        if total_pages > 1:
            for page in range(2, total_pages + 1):
                payload['page'] = str(page)
                response = self._make_api_call(self.url, params=payload)
                all_items.extend(response.json())
        return all_items


class WordpressProducts(WordpressResource):
    def __init__(self, url, session):
        super().__init__(session)
        self.url = f"{url}/products"
        self.default_payload = {
            'status': 'publish',
            'type': "variable",
            'stock_status': 'instock',
        }

    def get_variations(self, product_id):
        return WordpressProductVariation(
            url=self.url,
            product_id=product_id,
            session=self.session
        )


class WordpressCategory(WordpressResource):
    def __init__(self, url, session):
        super().__init__(session)
        self.url = f"{url}/products/categories"
        self.default_payload = {}


class WordpressAttributes(WordpressResource):
    def __init__(self, url, session):
        super().__init__(session)
        self.url = f"{url}/products/attributes"
        self.default_payload = {}

    def terms(self, attribute_id):
        return WordpressTerms(
            url=self.url,
            attribute_id=attribute_id,
            session=self.session
        )


class WordpressTerms(WordpressResource):
    def __init__(self, url, attribute_id, session):
        super().__init__(session)
        self.url = f"{url}/{attribute_id}/terms"
        self.default_payload = {}


class WordpressProductVariation(WordpressResource):
    def __init__(self, url, product_id, session):
        super().__init__(session)
        self.url = f"{url}/{product_id}/variations"
        self.default_payload = {}


class WordpressAPI:
    def __init__(self, url, consumer_key, consumer_secret):
        self.session = WordpressAuthenticate(consumer_key, consumer_secret).authenticate_session()
        self.products_url = f"{url}/products"
        self.products = WordpressProducts(url, self.session)
        self.categories = WordpressCategory(url, self.session)
        self.attributes = WordpressAttributes(url, self.session)


if __name__ == "__main__":
    wp = WordpressAPI(WP_URL, WP_CONSUMER_KEY, WP_CONSUMER_SECRET)

    all_products = wp.products.all()
    print("Products count", len(all_products))
    print("First product id", all_products[0].get('id'))

    all_categories = wp.categories.all()
    print("Categories count", len(all_categories))
    print("First category id", all_categories[0].get('id'))

    all_attributes = wp.attributes.all()
    print("Attributes count", len(all_attributes))
    print("First attribute id", all_attributes[0].get('id'))

    all_product_variations = wp.products.get_variations(66596).all()
    print("Variations count", len(all_product_variations))
    print("First variation id", all_product_variations[0].get('id'))



