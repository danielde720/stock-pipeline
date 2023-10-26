import logging
from confluent_kafka import Consumer, KafkaError
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import json  # Added for safer data parsing

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cassandra Configuration

cluster = Cluster(contact_points=['172.19.0.7'], port=9042, protocol_version=4)

session = cluster.connect('stock_keyspace')

# Kafka Configuration
conf = {
    'bootstrap.servers': '127.0.0.1:9092,127.0.0.1:9093,127.0.0.1:9094',  # Assuming Kafka brokers are on host machine
    'group.id': 'stock_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['stock_data'])

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logger.info('Reached end of partition %d' % (msg.partition()))
            else:
                logger.error('Error while consuming message: %s' % (msg.error().str()))
        else:
            # Proper message received
            data = msg.value().decode('utf-8')
            stock_data = json.loads(data)  # Safely parse the data using json.loads
            logger.info('Received message: %s' % stock_data)

            # Insert into Cassandra
            session.execute(
                """
                INSERT INTO stock_data (symbol, timestamp, last_price, volume)
                VALUES (%s, %s, %s, %s)
                """,
                (stock_data['symbol'], stock_data['timestamp'], stock_data['last_price'], stock_data['volume'])
            )

except KeyboardInterrupt:
    pass

finally:
    consumer.close()
    session.shutdown()
    cluster.shutdown()
