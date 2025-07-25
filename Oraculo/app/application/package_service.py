from datetime import datetime
from interfaces.repositories.package_repository import PackageRepository

class PackageService:
    
    def __init__(self, repository: PackageRepository):
        self.__db = repository

    def get_packages(self):
        return self.__db.get_all()
    
    def create_package(self, ip: str, attack_type: str, confidence: float=0): # remove default arg later
        package = {
            "ip": ip,
            "attack_type": attack_type,
            "confidence": confidence, # float
            "timestamp": datetime.now().isoformat()
        }
        self.__db.create(package)