from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import kafka_stream
import Consumer

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

dag = DAG(
    'kafka_dag',
    default_args=default_args,
    description='A simple Kafka DAG',
    schedule_interval='@daily',
    start_date=days_ago(1),
)

def run_kafka_stream():
    kafka_stream.main()  # Assuming your script has a main() function

def run_consumer():
    Consumer.main()  # Assuming your script has a main() function

t1 = PythonOperator(
    task_id='kafka_stream',
    python_callable=run_kafka_stream,
    dag=dag,
)

t2 = PythonOperator(
    task_id='consumer',
    python_callable=run_consumer,
    dag=dag,
)

t1 >> t2  # Set task dependencies
