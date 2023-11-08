# Import necessary libraries
import json
import websocket
import logging
from kafka import KafkaProducer
import os
import traceback
from datetime import datetime

# Set up logging with INFO level and a specific format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load API key 
API_KEY = os.getenv("Stock_API_Key")

# Function to create a Kafka producer with specified configurations
def create_kafka_producer():
    return KafkaProducer(
        # Specify the Kafka bootstrap servers (brokers)
        bootstrap_servers=['kafka1:19092', 'kafka2:19093', 'kafka3:19094'],
        # Use a lambda function to serialize the message values to JSON
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

# Create a Kafka producer instance
producer = create_kafka_producer()

# Function to handle incoming messages from the websocket
def on_message(ws, message):
    # Log the received message
    logging.info(f"Received: {message}")
    # Parse the message from JSON
    msg_data = json.loads(message)
    
    # Check if the message contains trade data
    if "data" in msg_data:
        # Process each trade in the message data
        for trade in msg_data["data"]:
            # Convert timestamp from milliseconds to seconds and format as ISO 8601
            timestamp = datetime.utcfromtimestamp(int(trade['t']) / 1000).isoformat()
            # Prepare the key and data to send to Kafka
            key_to_send = trade['s']
            data_to_send = {
                'symbol': trade['s'],
                'last_price': trade['p'],
                'volume': float(trade['v']),
                'timestamp': timestamp
            }
            try:
                # Encode the key to bytes
                key_to_send_bytes = key_to_send.encode('utf-8')
                # Send the data to the 'stock_data' Kafka topic
                producer.send('staging', key=key_to_send_bytes, value=data_to_send)
                # Log the sent data
                logging.info(f"Sent data to Kafka with key {key_to_send} and value {data_to_send}")
            except Exception as e:
                # Log any exceptions that occur while sending to Kafka
                logging.error(f"Error sending to Kafka: {e}")
                logging.error(traceback.format_exc())

# Function to handle errors from the websocket
def on_error(ws, error):
    logging.error(error)

# Function to handle websocket close events
def on_close(ws, close_status_code, close_msg):
    logging.info("WebSocket closed")

# Function to handle websocket open events
def on_open(ws):
    # List of symbols to subscribe to
    symbols = ['AAPL', 'AMZN', 'BINANCE:BTCUSDT', 'IC MARKETS:1']
    # Send a subscription request for each symbol
    for symbol in symbols:
        ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))

# Entry point of the script
if __name__ == "__main__":
    # Enable websocket tracing
    websocket.enableTrace(True)
    # Create a WebSocketApp instance with specified callbacks and API key
    ws = websocket.WebSocketApp(
        f"wss://ws.finnhub.io?token={API_KEY}",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    # Set the on_open callback
    ws.on_open = on_open
    # Start the websocket event loop
    ws.run_forever()
