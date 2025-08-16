import os
from flask import Flask
from werkzeug.serving import make_server
from .controllers.package_controller import PackageController, package_blueprint
from infrastructure.database.logstash_producer import db 
from application.package_service import PackageService

class WebServer:

    def __init__(self):
        self.__app = Flask(__name__)
        self.__package_service = PackageService(db)
        self.__package_controller = PackageController(self.__package_service)
        self.__setup_routes()

    def __setup_routes(self):
        package_blueprint.add_url_rule('/', view_func=self.__package_controller.render, methods=['GET'])
        package_blueprint.add_url_rule('/api/get_packages', view_func=self.__package_controller.get_packages, methods=['GET'])
        package_blueprint.add_url_rule('/api/new_model', view_func=self.__package_controller.post_model, methods=['POST'])
        self.__app.register_blueprint(package_blueprint, url_prefix='/', package_service=self.__package_service)

    def run(self):
        host = os.getenv("API_RUN_HOST", "0.0.0.0")
        port = int(os.getenv("API_RUN_PORT", 8000))
        self.__server = make_server(host, port, self.__app)
        self.__server.serve_forever()

    def stop(self):
        self.__server.shutdown()
