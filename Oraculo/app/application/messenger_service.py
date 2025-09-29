import logging
from typing import Any
from application.classification_service import ClassificationService
from application.firewall_service import FirewallService
from application.package_service import PackageService
from interfaces.messenger import Messenger

class MessengerService:

    def __init__(self, messenger: Messenger, classification_service: ClassificationService, firewall_service: FirewallService, package_service: PackageService):
        self.__messenger = messenger
        self.__classification_service = classification_service
        self.__firewall_service = firewall_service
        self.__package_service = package_service

    def __handle_message(self, ch, method, properties, body: bytes):
        try:
    
            message: dict[str, Any] = body.decode('utf-8')
            ip, id, input_data = self.__classification_service.pre_processing(message)
            prediction = self.__classification_service.classification(input_data, id)
            max_score_label = prediction[0][0]
            max_score_confidence = prediction[0][1]
            if(max_score_label != "Benign"): 
                # self.__firewall_service.block_source_ip(ip)
                self.__package_service.create_package(ip, id, max_score_label, max_score_confidence)

        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")

    def consume_message(self, queue_name):
        self.__messenger.receive_message(queue_name, self.__handle_message)
