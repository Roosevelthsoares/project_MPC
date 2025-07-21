from abc import ABC, abstractmethod

class Messenger(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def publish_message(self, queue_name, message):
        pass
    
    @abstractmethod
    def receive_message(self, queue_name, callback):
        pass

    @abstractmethod
    def close_connection(self):
        pass
        