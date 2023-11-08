from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import subprocess

def run_python_script(script_path):
    subprocess.run(["python", script_path], check=True)

def produce_data():
    run_python_script("/opt/airflow/scripts/kafka_stream.py")

def validate_data():
    run_python_script("/opt/airflow/scripts/data_validation.py")


def consume_data():
    run_python_script("/opt/airflow/scripts/consumer.py")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 11, 6),
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'catchup': False
}

dag = DAG(
    'kafka_cassandra_pipeline',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
)

produce_task = PythonOperator(
    task_id='produce_data',
    python_callable=produce_data,
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)

consume_task = PythonOperator(
    task_id='consume_data',
    python_callable=consume_data,
    retries=5,  # Number of retries for the consume task
    retry_delay=timedelta(seconds=5),  # Delay between retries for the consume task
    dag=dag,
)

# Set tasks to run independently
produce_task
validate_task
consume_task

