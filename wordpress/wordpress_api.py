from pprint import pprint

import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

WP_CONSUMER_KEY = os.getenv("WP_CONSUMER_KEY")
WP_CONSUMER_SECRET = os.getenv("WP_CONSUMER_SECRET")
WP_URL = os.getenv("WP_URL")


class WordpressAPI:
    def __init__(self, url, consumer_key, consumer_secret):
        self.url = url
        self.session = WordpressAuthenticate(consumer_key, consumer_secret).authenticate_session()
        self.products_url = f"{self.url}/products"
        self.products = WordpressProducts(self.url, self.session)
        self.categories = WordpressCategory(self.url, self.session)
        self.attributes = WordpressAttributes(self.url, self.session)


class WordpressAuthenticate:
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def authenticate_session(self) -> requests.Session:
        session = requests.Session()
        session.auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        return session


class WordpressBase:
    def __init__(self, session: requests.Session):
        self.session = session
        self.url = ...

    def make_api_call(self, url: str, params: dict = None) -> requests.models.Response:
        try:
            with self.session as session:
                response = session.get(url, params=params)
                response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
                return response
        except requests.exceptions.RequestException as e:
            print(f"Error making API call: {e}")


class WordpressDetails(WordpressBase):
    def __init__(self, url, session: requests.Session, item_id):
        super().__init__(session)
        self.item_id = item_id
        self.url = f"{url}/{self.item_id}"
        self.details = self.make_api_call(self.url).json()


class WordpressResource(WordpressBase):
    def __init__(self, session: requests.Session):
        super().__init__(session)
        self.session = session
        self.default_payload = ...

    def all(self, payload: dict = None) -> list:
        if payload is None:
            payload = self.default_payload

        all_items = []

        response = self.make_api_call(self.url, params=payload)
        all_items.extend(response.json())

        total_pages = int(response.headers.get('X-WP-TotalPages'))
        if total_pages > 1:
            for page in range(2, total_pages + 1):
                payload['page'] = str(page)
                response = self.make_api_call(self.url, params=payload)
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

    def get(self, product_id):
        return WordpressProduct(
            url=self.url,
            product_id=product_id,
            session=self.session
        )


class WordpressProduct(WordpressDetails):
    def __init__(self, url, session, product_id):
        super().__init__(url=url, session=session, item_id=product_id)

    @property
    def variations(self):
        return WordpressProductVariations(
            url=self.url,
            session=self.session
        )


class WordpressProductVariations(WordpressResource):
    def __init__(self, url, session):
        super().__init__(session)
        self.url = f"{url}/variations"
        self.default_payload = {'status': 'publish'}


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


wp = WordpressAPI(WP_URL, WP_CONSUMER_KEY, WP_CONSUMER_SECRET)


