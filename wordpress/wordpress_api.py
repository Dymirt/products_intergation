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

    @property
    def name(self):
        return self.details.get('name')


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
        for variation_id in self.details.get('variations'):
            yield WordpressVariation(
                url=self.url + '/variations',
                variation_id=variation_id,
                session=self.session
            )


class WordpressProductVariations(WordpressResource):
    def __init__(self, url, session):
        super().__init__(session)
        self.url = f"{url}/variations"
        self.default_payload = {}


class WordpressVariation(WordpressDetails):
    def __init__(self, url, session, variation_id):
        super().__init__(url, session, variation_id)

    @property
    def attributes(self):
        for attribute in self.details.get('attributes'):
            yield [attribute.get('id'), attribute.get('option')]


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

    def get(self, attribute_id):
        return WordpressAttribute(
            url=self.url,
            attribute_id=attribute_id,
            session=self.session
        )


class WordpressAttribute(WordpressDetails):
    def __init__(self, url, session, attribute_id):
        super().__init__(url=url, session=session, item_id=attribute_id)


class WordpressTerms(WordpressResource):
    def __init__(self, url, attribute_id, session):
        super().__init__(session)
        self.url = f"{url}/{attribute_id}/terms"
        self.default_payload = {}

    def get(self, term_id):
        return WordpressTerm(
            url=self.url,
            term_id=term_id,
            session=self.session
        )

class WordpressTerm(WordpressDetails):
    def __init__(self, url, session, term_id):
        super().__init__(url=url, session=session, item_id=term_id)

    #TODO term in product is value not id

class WordpressProductVariation(WordpressResource):
    def __init__(self, url, product_id, session):
        super().__init__(session)
        self.url = f"{url}/{product_id}/variations"
        self.default_payload = {}


if __name__ == "__main__":
    wp = WordpressAPI(WP_URL, WP_CONSUMER_KEY, WP_CONSUMER_SECRET)

    """
    all_products = wp.products.all()
    print("Products count", len(all_products))

    first_product_id = all_products[0].get('id')
    print("First product id", first_product_id)
    """

    first_product = wp.products.get(66596)
    print("Product name", first_product.name)

    for variation in first_product.variations:
        for attribute, term in variation.attributes:
            print(f"{wp.attributes.get(attribute).name} - {wp.attributes.terms(attribute).get(term).name}")

    """
    all_categories = wp.categories.all()
    first_category_id = all_categories[0].get('id')
    print("Categories count", len(all_categories))
    print("First category id", first_category_id)
    #print("Category name", wp.categories.get_by_id(first_category_id).get('name'))

    all_attributes = wp.attributes.all()
    first_attribute_id = all_attributes[0].get('id')
    print("Attributes count", len(all_attributes))
    print("First attribute id", first_attribute_id)
    #print("Attribute name", wp.attributes.get_by_id(first_attribute_id).get('name'))

    all_product_variations = wp.products.variations(66596).all()
    first_product_variation_id = all_product_variations[0].get('id')
    print("Variations count", len(all_product_variations))
    print("First variation id", first_product_variation_id)
    #print("Variation name", wp.products.variations(66596).get_by_id(first_product_variation_id).get('name'))



    """


