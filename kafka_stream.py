import json
import websocket
from dotenv import load_dotenv
import os
from kafka import KafkaProducer

load_dotenv()
API_KEY = os.getenv("Stock_API_Key")

# Create Kafka producer using Kafka-Python library
def create_kafka_producer():
    """
    Creates the Kafka producer object
    """
    return KafkaProducer(bootstrap_servers=['localhost:9092', 'localhost:9093', 'localhost:9094'],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

producer = create_kafka_producer()

# Enable WebSocket trace logs (for debugging)
websocket.enableTrace(True)


# Function to handle incoming messages from the websocket
def on_message(ws, message):
    print("Received:", message)
    message_data = json.loads(message)
    if "data" in message_data:
        for trade in message_data["data"]:
            try:
                producer.send('stock_data', key=str(trade["t"]), value=trade)
            except Exception as e:
                print("Error sending to Kafka:", e)


# WebSocket error handler
def on_error(ws, error):
    print(error)

# WebSocket close handler
def on_close(ws):
    print("### closed ###")

# WebSocket open handler
def on_open(ws):
    ws.send(json.dumps({"type": "subscribe", "symbol": "AAPL"}))
    ws.send(json.dumps({"type": "subscribe", "symbol": "AMZN"}))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={API_KEY}",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
