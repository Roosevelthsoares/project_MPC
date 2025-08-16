import os

from dotenv import load_dotenv
from urllib3 import disable_warnings

load_dotenv()
disable_warnings()

FIREWALL_CLIENT_ID    = os.getenv('FIREWALL_CLIENT_ID')
FIREWALL_TOKEN_ID     = os.getenv('FIREWALL_TOKEN_ID')
URL_FIREWALL = os.getenv('URL_FIREWALL')