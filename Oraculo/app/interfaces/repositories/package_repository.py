from abc import ABC, abstractmethod

class PackageRepository(ABC):

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def create(self, package_data):
        pass