from airflow import DAG
from airflow.decorators import task, dag
from airflow.utils.dates import days_ago
from kafka import KafkaProducer
from confluent_kafka import Consumer, KafkaException, KafkaError 
from cassandra.cluster import Cluster
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import logging
import time
from dateutil import parser

@dag(schedule_interval='@daily', start_date=days_ago(1), catchup=False)
def data_pipeline():

    @task
    def run_kafka_stream():
        kafka_stream.main()
        return "Kafka Stream Completed"

    @task
    def run_consumer():
        # Your Consumer.main() code here, converted to a function
        ...
        return "Consumer Completed"

    @task
    def run_visualization():
        # Your visual.py code here, converted to a function
        ...
        return "Visualization Completed"

    @task
    def run_integrity_check():
        # Your data integrity check code
        ...
        return "Integrity Check Completed"

    @task
    def run_quality_check():
        # Your data quality check code
        ...
        return "Quality Check Completed"

    kafka_result = run_kafka_stream()
    consumer_result = run_consumer()
    visual_result = run_visualization()
    integrity_check_result = run_integrity_check()
    quality_check_result = run_quality_check()

data_pipeline_dag = data_pipeline()
