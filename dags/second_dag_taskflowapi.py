from dags_config import Config as config
from datetime import datetime
from airflow.decorators import dag, task

@dag(dag_id='second_dag_taskflowapi',
    default_args=config.DEFAULT_ARGS,
    description='This is our second dag with PythonOperator using TaskflowAPI!',
    start_date=datetime(2024, 3, 3, 2),
    schedule_interval='@daily')
def hi_world_data_pipeline():

    @task
    def get_name(multiple_outputs=True):
        return {
            'first_name': 'Tendies',
            'last_name': 'Wang'
        }

    @task
    def get_age():
        return 1

    @task
    def greet(name_dict, age):
        first_name = name_dict['first_name']
        last_name = name_dict['last_name']
        print(f'Hello world! I am calling from PythonOperator.',
            f'I am {first_name} {last_name} and {age} years old.')

    name_dict=get_name()
    age=get_age()
    greet(name_dict, age)

greet_dag = hi_world_data_pipeline()
    