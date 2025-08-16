import json
from pathlib import Path
import socket
from interfaces.repositories.package_repository import PackageRepository

class InMemoryDatabase(PackageRepository):
    
    def __init__(self):
        self.data = []

    def get_all(self):
        return self.data

    def create(self, package_data):
        self.data.append(package_data)

db = InMemoryDatabase()