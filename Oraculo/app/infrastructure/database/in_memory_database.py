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

import socket
import json
from pathlib import Path

class PersistentLogstashProducer(PackageRepository):
    def __init__(self, file_path='logs.jsonl', logstash_host='logstash', logstash_port=5044):
        self.file_path = Path(file_path)
        self.logstash_host = logstash_host
        self.logstash_port = logstash_port
        self.file_path.touch(exist_ok=True)

    def get_all(self):
        with self.file_path.open('r', encoding='utf-8') as f:
            return [json.loads(line.strip()) for line in f if line.strip()]

    def create(self, package_data):
        # Append to disk
        with self.file_path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(package_data) + '\n')

        # Send to Logstash
        message = json.dumps(package_data)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.logstash_host, self.logstash_port))
                sock.sendall(message.encode('utf-8'))
            print(f"[x] Logged and pushed to Logstash: {message}")
        except Exception as e:
            print(f"[!] Failed to send to Logstash at {self.logstash_host}:{self.logstash_port} — {e}")

    def close(self):
        pass




db = PersistentLogstashProducer()