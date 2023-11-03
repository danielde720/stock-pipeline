from kafka import KafkaConsumer, KafkaProducer
import json
import logging
from datetime import datetime, timedelta

# Set up logging with INFO level and a specific format
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Expected schema
EXPECTED_SCHEMA = {
    'symbol': str,
    'last_price': float,
    'volume': float,
    'timestamp': str 
}

# Symbols to monitor
SYMBOLS_TO_MONITOR = {'AAPL', 'AMZN', 'BINANCE:BTCUSDT', 'IC MARKETS:1'}

# Dictionary to keep track of the last time a symbol was received
last_received = {symbol: None for symbol in SYMBOLS_TO_MONITOR}

def create_kafka_consumer():
    try:
        # Configuration dictionary for the Kafka consumer
        conf = {
            'bootstrap_servers': 'kafka1:19092,kafka2:19093,kafka3:19094',
            'group_id': 'data_validation_group',
            'auto_offset_reset': 'earliest',
        }
        logging.info('Creating Kafka consumer...')
        # Create and return a Kafka Consumer instance with the specified configuration
        return KafkaConsumer('staging', bootstrap_servers=conf['bootstrap_servers'], group_id=conf['group_id'], auto_offset_reset=conf['auto_offset_reset'])
    except Exception as e:
        logging.error(f'Failed to create Kafka consumer: {e}')
        raise


def create_kafka_producer():
    try:
        logging.info('Creating Kafka producer...')
        return KafkaProducer(
            # Specify the Kafka bootstrap servers (brokers)
            bootstrap_servers=['kafka1:19092', 'kafka2:19093', 'kafka3:19094'],
            # Use a lambda function to serialize the message values to JSON
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception as e:
        logging.error(f'Failed to create Kafka producer: {e}')
        raise

def validate_data(record):
    # Check if all required fields are present and have the correct data type
    for field, dtype in EXPECTED_SCHEMA.items():
        if field not in record:
            logging.warning(f'Missing field: {field}')
            return False
        if not isinstance(record[field], dtype):
            logging.warning(f'Incorrect data type for field: {field}')
            return False
    # Check for null values
    for field, value in record.items():
        if value is None:
            logging.warning(f'Null value for field: {field}')
            return False
        
     # Check for realistic values
    if record['last_price'] < 0:
        logging.warning(f'Negative value for last_price: {record["last_price"]}')
        return False
        
    if record['volume'] < 0:
        logging.warning(f'Negative value for volume: {record["volume"]}')
        return False
    return True

def monitor_symbols():
    now = datetime.utcnow()
    for symbol, last_time in last_received.items():
        if last_time is None or (now - last_time) > timedelta(hours=4):
            logging.warning(f"No data received for symbol {symbol} in the last 4 hours")
            

def main():
    consumer = create_kafka_consumer()
    producer = create_kafka_producer()

    try:
        for message in consumer:
            record = json.loads(message.value)
            symbol = record.get('symbol')
            if symbol in SYMBOLS_TO_MONITOR:
                last_received[symbol] = datetime.utcnow()

            if validate_data(record):
                producer.send('stock_data', value=record)
                logging.info(f"Sent valid record to stock_data topic: {record}")
            else:
                producer.send('bad_stock_data', value=record)
                logging.warning(f"Sent invalid record to bad_stock_data topic: {record}")

            # Monitoring check
            monitor_symbols()
    except Exception as e:
        logging.error(f'Error: {e}', exc_info=True)
    finally:
        # Close the consumer and producer
        consumer.close()
        producer.close()

if __name__ == "__main__":
    main()
