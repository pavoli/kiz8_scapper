from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def print_hello():
    print("Hello World")


with DAG(
    dag_id='hello_world',
    start_date=datetime(2025, 5, 8),
    schedule_interval='@daily',
    catchup=False,
    tags=['example'],
) as dag:

    task_print_hello = PythonOperator(
        task_id='print_hello_task',
        python_callable=print_hello,
    )
