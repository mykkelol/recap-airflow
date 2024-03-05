from dags_config import Config as config
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

def get_name(ti):
    import sklearn
    import matplotlib

    modules = [sklearn, matplotlib]
    dependencies = ', '.join([f'{m.__name__} {m.__version__}' for m in modules])

    ti.xcom_push(key='first_name', value='Tendies')
    ti.xcom_push(key='last_name', value='Wang')
    ti.xcom_push(key='dependencies', value=dependencies)

def get_age(ti):
    ti.xcom_push(key='age', value=1)

def greet(my_dict, ti):
    first_name = ti.xcom_pull(task_ids='get_name', key='first_name')
    last_name = ti.xcom_pull(task_ids='get_name', key='last_name')
    dependencies = ti.xcom_pull(task_ids='get_name', key='dependencies')
    age = ti.xcom_pull(task_ids='get_age', key='age')

    print(my_dict)
    print(f'Hello world! I am calling from PythonOperator.',
          f'I am {first_name} {last_name} and {age} years old.',
          f'I extended airflow with {dependencies}')

with DAG(
    dag_id='second_dag',
    default_args=config.DEFAULT_ARGS,
    description='This is our second dag with PythonOperator!',
    start_date=datetime(2024, 3, 3, 2),
    schedule_interval='@daily'
) as dag:
    
    start = S3KeySensor(
        task_id='minio_s3_sensor',
        bucket_name='airflow',
        bucket_key='data.csv',
        aws_conn_id=config.S3_CONN_ID,
        mode='poke',
        poke_interval=5,
        timeout=30
    )
    
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

    start >> [name, age] >> finish