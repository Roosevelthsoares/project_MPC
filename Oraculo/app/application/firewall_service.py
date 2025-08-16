import json
import logging

from interfaces.rest_client import RESTClient

class FirewallService:

    def __init__(self, pfsense_client: RESTClient):
        self.__pfsense_client = pfsense_client

    def __create_blocking_rule(self, ip):
        try:
            with open('app/data/rules/block.json') as f:
                rule = json.load(f)
                rule['src'] = ip

            return rule 

        except Exception as e:
            logging.error(f'Error accessing rule file: {e}')

    def block_source_ip(self, ip):
        logging.info(f'Creating blocking rule for source IP: {ip}')
        rule = self.__create_blocking_rule(ip)
        self.__pfsense_client.post(data=rule)
