import logging
import requests

from interfaces.rest_client import RESTClient

class pfSenseClient(RESTClient):

    def __init__(self, base_url, client, token):
        self.__base_url = base_url
        self.__client = client
        self.__token = token

    def __handle_response(self, response):
        try:
            response.raise_for_status()

        # Handle HTTP errors
        except requests.exceptions.HTTPError as errh:
            logging.error("HTTP Error:", errh)

        # Handle connection errors
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting:", errc)

        # Handle timeouts
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error:", errt)

        # Handle other errors
        except requests.exceptions.RequestException as err:
            logging.error("Error:", err)

    def get(self, path='', params=None):
        url = f'{self.__base_url}/{path}'
        try:
            response = requests.get(url, headers={'Authorization': f'{self.__client} {self.__token}'}, params=params, verify=False)
            self.__handle_response(response)

            return response

        except requests.RequestException as e:
            logging.error(f"An error occurred during GET request: \n{str(e)}")

    def post(self, path='', data=None):
        url = f'{self.__base_url}/{path}'
        try:
            response = requests.post(url, headers={'Authorization': f'{self.__client} {self.__token}'}, json=data, verify=False)
            self.__handle_response(response)

            return response

        except requests.RequestException as e:
            logging.error(f"An error occurred during POST request: \n{str(e)}")