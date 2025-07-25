import os

from dotenv import load_dotenv
from urllib3 import disable_warnings

load_dotenv()
disable_warnings()

CLIENT_ID    = os.getenv('CLIENT_ID')
TOKEN_ID     = os.getenv('TOKEN_ID')
URL_FIREWALL = os.getenv('URL_FIREWALL')