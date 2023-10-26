import json
import websocket
import logging
from kafka import KafkaProducer
import os
import traceback
# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load your API key (adjust as necessary)
API_KEY =  "ck45smhr01qus81pq6egck45smhr01qus81pq6f0" #os.getenv("Stock_API_Key")

# Create Kafka producer
def create_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=['127.0.0.1:9092', '127.0.0.1:9093', '127.0.0.1:9094'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

producer = create_kafka_producer()

# Handle incoming messages from the websocket
def on_message(ws, message):
    logging.info(f"Received: {message}")
    msg_data = json.loads(message)
    
    if "data" in msg_data:
        for trade in msg_data["data"]:
            key_to_send = trade['s']
            data_to_send = {
                'symbol': trade['s'],
                'last_price': trade['p'],
                'volume': trade['v'],
                'timestamp': trade['t']
            }
            try:
                
                key_to_send_bytes = key_to_send.encode('utf-8')
                producer.send('stock_data', key=key_to_send_bytes, value=data_to_send)
                logging.info(f"Sent data to Kafka with key {key_to_send} and value {data_to_send}")
            except Exception as e:
                logging.error(f"Error sending to Kafka: {e}")
                logging.error(traceback.format_exc())

def on_error(ws, error):
    logging.error(error)

def on_close(ws, close_status_code, close_msg):
    logging.info("WebSocket closed")

def on_open(ws):
    symbols = ['AAPL', 'AMZN', 'BINANCE:BTCUSDT', 'IC MARKETS:1']
    for symbol in symbols:
        ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        f"wss://ws.finnhub.io?token={API_KEY}",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()



















'''''

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
API_KEY = os.getenv("Stock_API_Key")

# Create Kafka producer using Kafka-Python library
def create_kafka_producer():
    """
    Creates the Kafka producer object
    """
    return KafkaProducer(bootstrap_servers=['127.0.0.1:9092', '127.0.0.1:9093', '127.0.0.1:9094'],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

producer = create_kafka_producer()

# Enable WebSocket trace logs (for debugging)
websocket.enableTrace(True)

# Function to handle incoming messages from the websocket
def on_message(ws, message):
    logging.info(f"Received: {message}")
    message_data = json.loads(message)
    if "data" in message_data:
        for trade in message_data["data"]:
            try:
                producer.send('stock_data', key=str(trade["t"]), value=trade)
            except Exception as e:
                logging.error(f"Error sending to Kafka: {e}")

# WebSocket error handler
def on_error(ws, error):
    logging.error(error)

# WebSocket close handler
def on_close(ws):
    logging.info("WebSocket closed")

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

    
    '''''