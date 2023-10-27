# Import necessary libraries from the Confluent Kafka and Cassandra packages
from confluent_kafka import Consumer, KafkaException,  KafkaError 
from cassandra.cluster import Cluster
import json
import logging
from cassandra.policies import DCAwareRoundRobinPolicy

# Set up logging with INFO level and a specific format
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def create_kafka_consumer():
    try:
        # Configuration dictionary for the Kafka consumer
        conf = {
            'bootstrap.servers': '127.0.0.1:9092,127.0.0.1:9093,127.0.0.1:9094',
            'group.id': 'stock_data_group',
            'auto.offset.reset': 'earliest',
        }
        logging.info('Creating Kafka consumer...')
        # Create and return a Kafka Consumer instance with the specified configuration
        return Consumer(conf)
    except Exception as e:
        logging.error(f'Failed to create Kafka consumer: {e}')
        raise

def create_cassandra_session():
    try:
        # Set up a load balancing policy for connecting to Cassandra
        load_balancing_policy = DCAwareRoundRobinPolicy(local_dc='datacenter1')
        # Create and return a Cassandra Cluster instance, specifying the host, port, and load balancing policy
        cluster = Cluster(['127.0.0.1'], port=9042, load_balancing_policy=load_balancing_policy, protocol_version=4 )
        logging.info('Connecting to Cassandra...')
        session = cluster.connect()
        logging.info('Connected to Cassandra.')
        return session
    except Exception as e:
        logging.error(f'Failed to connect to Cassandra: {e}')
        raise

def on_message(msg, session):
    if msg.error():
        # Handle Kafka message errors
        if msg.error().code() == KafkaError._PARTITION_EOF:
            logging.info(f"Consumer reached end of {msg.topic()}:{msg.partition()} at offset {msg.offset()}")
        else:
            logging.error(f'Kafka error: {msg.error()}')
            raise KafkaException(msg.error())
    else:
        try:
            # Parse the Kafka message value from JSON
            stock_data = json.loads(msg.value().decode('utf-8'))
            # Log the data types of the stock_data fields
            logging.info(f'Types - symbol: {type(stock_data["symbol"])}, last_price: {type(stock_data["last_price"])}, volume: {type(stock_data["volume"])}, timestamp: {type(stock_data["timestamp"])}')
            # Cassandra query to insert stock data into the database
            insert_query = """
            INSERT INTO stock_data.updated_stock (symbol, last_price, volume, timestamp)
            VALUES (%s, %s, CAST(%s AS float), %s)
            """
            # Log and execute the Cassandra query
            logging.info(f'Executing query: {insert_query % (stock_data["symbol"], stock_data["last_price"], stock_data["volume"], stock_data["timestamp"])}')  # Log the query being executed
            session.execute(insert_query, (stock_data['symbol'], stock_data['last_price'], float(stock_data['volume']), stock_data['timestamp']))
            logging.info(f'Inserted stock data for {stock_data["symbol"]}')
        except Exception as e:
            logging.error(f'Failed to process message: {e}', exc_info=True)

def main():
    # Create Kafka consumer and Cassandra session
    consumer = create_kafka_consumer()
    cassandra_session = create_cassandra_session()
    # Subscribe to the Kafka topic 'stock_data'
    logging.info('Subscribing to topic: stock_data')
    consumer.subscribe(['stock_data'])
    
    try:
        # Continuously poll for messages from Kafka, and process each message using on_message
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            on_message(msg, cassandra_session)
    except KeyboardInterrupt:
        logging.info('Interrupted by user')
    except Exception as e:
        logging.error(f'Error: {e}')
    finally:
        # Close the Kafka consumer and Cassandra session when done
        logging.info('Closing consumer and Cassandra session...')
        consumer.close()
        cassandra_session.cluster.shutdown()
        logging.info('Consumer and Cassandra session closed.')

# Entry point of the script
if __name__ == "__main__":
    main()