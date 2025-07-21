from abc import ABC, abstractmethod

class RESTClient(ABC):

    @abstractmethod
    def get(self, path='', params=None):
        pass

    @abstractmethod
    def post(self, path='', data=None):
        pass