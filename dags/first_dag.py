from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'mykke',
    'retries': 5,
    'owner': timedelta(minutes=2),
}

with DAG(
    dag_id='first_dag',
    default_args=default_args,
    description='First dag since 2021',
    start_time=datetime(2024, 3, 3, 2),
    schedule_interval='@daily',
) as dag:
    pass