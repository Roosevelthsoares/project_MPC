import logging
import threading
import signal
import sys

from infrastructure.rest.app import WebServer
from infrastructure.database.logstash_producer import db 
from domain.entities.predictor import Predictor
from infrastructure.adapters.message_broker import MessageBroker
from infrastructure.adapters.pfsense_client import pfSenseClient
from application.messenger_service import MessengerService
from application.firewall_service import FirewallService
from application.package_service import PackageService
from application.classification_service import ClassificationService
from config import URL_FIREWALL, FIREWALL_CLIENT_ID, FIREWALL_TOKEN_ID
from domain.entities.loggers.terminal import apply_colored_formatter


def start_flask_app():
    global flask_app
    flask_app = WebServer()
    flask_thread = threading.Thread(target=flask_app.run)
    flask_thread.start()
    return flask_app, flask_thread

def stop_application():
    logging.warning("Stopping application...") # INSERIDO  
    if flask_app: # INSERIDO
        flask_app.stop()
    sys.exit(0)

def initialize_services():
    predictor = Predictor().build()

    message_broker = MessageBroker()
    pfSense_client = pfSenseClient(URL_FIREWALL, FIREWALL_CLIENT_ID, FIREWALL_TOKEN_ID)
    classification_service = ClassificationService(predictor)
    firewall_service = FirewallService(pfSense_client)
    package_service = PackageService(db)
    messenger_service = MessengerService(message_broker, classification_service, firewall_service, package_service)
    return messenger_service

def main():
    messenger_service = initialize_services()
    messenger_service.consume_message('model-queue')
    
if __name__ == '__main__':
    try:
        # Color and format the logs
        apply_colored_formatter()
        
        # Create flask instance and a thread running the web server
        flask_app, flask_thread = start_flask_app()

        # Register a signal handler for CTRL+C
        signal.signal(signal.SIGINT, stop_application)

        # Run your existing main function (communication with broker) in the main thread
        main()

        # Stop the application when the communication with the broker ends
        stop_application()

    except Exception as e:
        logging.error(str(e.with_traceback()))
        stop_application()
        
