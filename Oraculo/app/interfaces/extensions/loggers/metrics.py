from abc import ABC, abstractmethod


class MetricLoggingExtension(ABC):
    @abstractmethod
    def new_experiment(self, experiment_name: str):
        pass
    
    @abstractmethod
    def log(self, **kwargs):
        pass