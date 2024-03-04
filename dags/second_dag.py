from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'mykke',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

def greet(name, age):
    print(f'Hello world! I am calling from PythonOperator.',
          f'I am {name} and {age} years old.')

with DAG(
    dag_id='second_dag',
    default_args=default_args,
    description='This is our second dag with PythonOperator!',
    start_date=datetime(2024, 3, 3, 2),
    schedule_interval='@daily'
) as dag:
    
    start = PythonOperator(
        task_id='greet',
        python_callable=greet,
        op_kwargs={'name': 'Greet Oppo', 'age': 1}
    )

    start