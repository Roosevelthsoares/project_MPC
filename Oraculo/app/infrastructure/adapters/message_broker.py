import logging
import os
import pika
import time

from interfaces.messenger import Messenger

class MessageBroker(Messenger):
    
    def __init__(self, server='rabbitmq', port=5672, user=None, password=None, virtual_host='/', max_retries=3, retry_delay=5):
        user = user or os.getenv("RABBITMQ_DEFAULT_USER", "guest")
        password = password or os.getenv("RABBITMQ_DEFAULT_PASSWORD", "guest")
        
        self.__server = server
        self.__port = port
        self.__user = user
        self.__password = password
        self.__virtual_host = virtual_host
        self.__max_retries = max_retries
        self.__retry_delay = retry_delay
        self.__connection = None
        self.__channel = None
        
    def connect(self):
        # Connect to RMQ 
        logging.info(f'Connecting to {self.__server}')
        retries = 0
        while retries < self.__max_retries:
            try:
                credentials = pika.PlainCredentials(self.__user, self.__password)
                params = pika.ConnectionParameters(host=self.__server, port=self.__port, virtual_host=self.__virtual_host, credentials=credentials)
                self.__connection = pika.BlockingConnection(params)
                self.__channel = self.__connection.channel()
                return

            # Do not recover on channel errors
            except pika.exceptions.AMQPChannelError as err:
                logging.error('Channel error: {}, stopping...'.format(err))
                break

            # Recover on connection errors
            except pika.exceptions.AMQPConnectionError:
                logging.warning("Connection was closed, retrying...")
                retries += 1
                time.sleep(self.__retry_delay)

        raise Exception("Max retries reached. Unable to connect to RabbitMQ.")

    def publish_message(self, queue_name, message):
        try:
            self.connect()
            self.__channel.queue_declare(queue=queue_name, durable=True) 
            self.__channel.basic_publish(exchange='', routing_key=queue_name, body=message)
            logging.debug(f"Sent '{message[:100]}...'")
            self.__retry_delay = 5  # Reset retry delay on success

        except pika.exceptions.AMQPError as e:
            logging.error(f"Error publishing message: {str(e)}")

        finally:
            self.close_connection()
        
    def receive_message(self, queue_name, callback):
        while True:
            try:
                self.connect()
                self.__channel.queue_declare(queue=queue_name, durable=True)
                self.__channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
                logging.info('Waiting for messages. To exit press CTRL+C')
                self.__channel.start_consuming()

            except KeyboardInterrupt:
                if self.__channel:
                    self.__channel.stop_consuming()
                break

            except (pika.exceptions.AMQPError, pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as e:
                logging.error(f"Error receiving message: {str(e)}")
                time.sleep(self.__retry_delay)
                continue

            finally:
                self.close_connection()

    def close_connection(self):
        if self.__connection and self.__connection.is_open:
            self.__connection.close()
            logging.info("Connection closed.")
        