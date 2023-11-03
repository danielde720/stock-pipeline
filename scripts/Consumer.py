# Import necessary libraries from the Confluent Kafka and Cassandra packages
from confluent_kafka import Consumer, KafkaException,  KafkaError 
from cassandra.cluster import Cluster
import json
import logging
from cassandra.policies import DCAwareRoundRobinPolicy
import time
from dateutil import parser

# Set up logging with INFO level and a specific format
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def create_kafka_consumer():
    try:
        # Configuration dictionary for the Kafka consumer
        conf = {
            'bootstrap.servers': 'kafka1:19092,kafka2:19093,kafka3:19094',
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
        #auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
        cluster = Cluster(['cassandra'], port=9042, load_balancing_policy=load_balancing_policy, protocol_version=4 )
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
            # Convert the string formatted timestamp to a datetime object
            dt = parser.parse(stock_data['timestamp'])
            # Convert the datetime object to a UNIX timestamp in milliseconds
            timestamp_ms = int(time.mktime(dt.timetuple()) * 1000 + dt.microsecond / 1000)
            # Prepare the Cassandra query
            insert_query = """
            INSERT INTO stock_data.stock (symbol, last_price, volume, timestamp)
            VALUES (%s, %s, CAST(%s AS float), %s)
            """
            # Execute the Cassandra query
            session.execute(insert_query, (stock_data['symbol'], stock_data['last_price'], float(stock_data['volume']), timestamp_ms))
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