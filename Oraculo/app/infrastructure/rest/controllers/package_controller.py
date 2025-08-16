from flask import Blueprint, render_template
from application.package_service import PackageService

package_blueprint = Blueprint('package', __name__)

class PackageController:

    def __init__(self, package_service: PackageService):
        self.__package_service = package_service

    def render(self):
        packages = self.__package_service.get_packages()
        return render_template("index.html", packages=packages)
    
    def get_packages(self):
        packages = self.__package_service.get_packages()
        return packages
    
    def post_model(self):
        pass
        