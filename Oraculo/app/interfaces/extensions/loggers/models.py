from abc import ABC, abstractmethod


class ModelLoggingExtension(ABC):
    
    @abstractmethod
    def save(self, **kwargs):
        pass
    
    @abstractmethod
    def load(self, **kwargs):
        pass