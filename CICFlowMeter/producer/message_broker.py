import pika
import time
import json

class MessageBroker:
    def __init__(self, host='rabbitmq', queue='model-queue'):
        self.queue = queue
        max_retries = 10
        for attempt in range(max_retries):
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)
                print("[INFO] Conexão com RabbitMQ estabelecida.")
                return
            except pika.exceptions.AMQPConnectionError as e:
                print(f"[WARN] Tentativa {attempt + 1}/{max_retries} falhou: RabbitMQ não está pronto. Aguardando 3s...")
                time.sleep(3)
        raise ConnectionError("[ERRO] Não foi possível conectar ao RabbitMQ após várias tentativas.")

    def publish_message(self, message):
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2  # persistente
                )
            )
            print("[DEBUG] Publicando mensagem no RabbitMQ:", message)
        except pika.exceptions.AMQPError as e:
            print(f"[ERROR] Falha ao publicar mensagem: {e}")

    def close(self):
        self.connection.close()
