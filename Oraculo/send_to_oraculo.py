import gc
import pika
import pandas as pd
import json
import time
from sklearn.preprocessing import StandardScaler

# === Configuration ===
RABBITMQ_HOST = 'rabbitmq'        # Change if needed
RABBITMQ_PORT = 5672
QUEUE_NAME = 'fluxos'
DATA_PATH = 'app/data/models/calibrate/CICIDS2018_preprocessed_test.parquet'
NUM_SAMPLES = 5
MOCK_IP = "192.168.1.123"
ATTACK_LABEL = "SSH-Bruteforce"  # Change this to test different attack classes

# === Load and preprocess data ===
df = pd.read_parquet(DATA_PATH)

# Basic cleaning
if 'Timestamp' in df.columns:
    df = df.drop(columns=['Timestamp'])
if 'label' in df.columns:
    df = df.rename(columns={'label': 'Label'})
df = df[df['Label'] != 'Label']  # Remove invalid rows

# Filter only attack class samples
df_attack = df[df['Label'] == ATTACK_LABEL]

if df_attack.empty:
    raise ValueError(f"No samples found with label '{ATTACK_LABEL}'")

# Remove label column and fit scaler
X = df_attack.drop(columns=['Label'])
cols = X.columns.tolist()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Create scaled DataFrame
df_scaled = pd.DataFrame(X_scaled, columns=cols)

# === Connect to RabbitMQ ===
credentials = pika.PlainCredentials('guest', 'guest')
params = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    credentials=credentials
)

connection = pika.BlockingConnection(params)
channel = connection.channel()

# Queue must match durability config with consumer
channel.queue_declare(queue=QUEUE_NAME, durable=False)

# === Send messages ===
print(f"Sending {NUM_SAMPLES} attack samples to queue '{QUEUE_NAME}'...")

for i in range(NUM_SAMPLES):
    sample = df_scaled.sample(n=1, random_state=i).iloc[0].to_dict()
    message = {"ip": MOCK_IP, **sample}

    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(message),  # Proper JSON
        properties=pika.BasicProperties(delivery_mode=2)
    )

    print(f"[{i + 1}] Sent attack sample with IP {MOCK_IP}")
    time.sleep(0.5)

connection.close()
print("Done.")
