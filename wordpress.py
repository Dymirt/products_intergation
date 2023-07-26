import os
from pprint import pprint
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()
WP_CONSUMER_KEY = os.getenv("WP_CONSUMER_KEY")
WP_CONSUMER_SECRET = os.getenv("WP_CONSUMER_SECRET")
WP_URL = os.getenv("WP_URL")


class WordpressAPI:
    def __init__(self, url, consumer_key, consumer_secret):
        self.url = url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.session = requests.Session()
        self.__authenticate_session()
        self.products_url = f"{self.url}/products"

        self.products_variable_publish_payload = {
            'status': 'publish',
            'type': "variable"
        }

    def __authenticate_session(self) -> None:
        self.session.auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret)

    def _make_api_call(self, url: str, params: dict = None) -> requests.models.Response:
        try:
            with self.session as session:
                response = session.get(url, params=params)
                response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
                return response
        except requests.exceptions.RequestException as e:
            print(f"Error making API call: {e}")

    def get_products_variable_publish(self):
        return self._make_api_call(self.products_url, params=self.products_variable_publish_payload).json()

    def get_products_variable_publish_count(self) -> int:
        response = self._make_api_call(self.products_url, params=self.products_variable_publish_payload)
        return int(response.headers.get('X-WP-Total'))


if __name__ == "__main__":
    wp = WordpressAPI(WP_URL, WP_CONSUMER_KEY, WP_CONSUMER_SECRET)
    pprint(wp.get_products_variable_publish()[0])