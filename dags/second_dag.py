from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'mykke',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

def get_name(ti):
    ti.xcom_push(key='first_name', value='Tendies')
    ti.xcom_push(key='last_name', value='Wang')

def get_age(ti):
    ti.xcom_push(key='age', value=1)

def greet(my_dict, ti):
    first_name = ti.xcom_pull(task_ids='get_name', key='first_name')
    last_name = ti.xcom_pull(task_ids='get_name', key='last_name')
    age = ti.xcom_pull(task_ids='get_age', key='age')
    print(my_dict)
    print(f'Hello world! I am calling from PythonOperator.',
          f'I am {first_name} {last_name} and {age} years old.')

with DAG(
    dag_id='second_dag',
    default_args=default_args,
    description='This is our second dag with PythonOperator!',
    start_date=datetime(2024, 3, 3, 2),
    schedule_interval='@daily'
) as dag:
    
    name = PythonOperator(
        task_id='get_name',
        python_callable=get_name,
    )

    age = PythonOperator(
        task_id='get_age',
        python_callable=get_age,
    )

    finish = PythonOperator(
        task_id='greet',
        python_callable=greet,
        op_kwargs={'my_dict': {'a': 6, 'b': .2}}
    )

    [name, age] >> finish
    finish