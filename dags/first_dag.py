from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'mykke',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}


with DAG(
    dag_id='first_dag',
    default_args=default_args,
    description='This is our first dag that we write',
    start_date=datetime(2024, 3, 3, 2),
    schedule_interval='@daily'
) as dag:
    task1 = BashOperator(
        task_id='first_task',
        bash_command="echo hello world first dag since 2021"
    )

    task2 = BashOperator(
        task_id='second_task',
        bash_command="echo hey task1, I am task2 and was successfully executed"
    )
    
    task3 = BashOperator(
        task_id='third_task',
        bash_command="echo hey task1, I am task3 and was also successfully executed async to task2"
    )
    
    task4 = BashOperator(
        task_id='fourth_task',
        bash_command="echo hey task2, I am task4 and will execute with task5"
    )
    
    task5 = BashOperator(
        task_id='fifth_task',
        bash_command="echo hey task2, we are task4 and task5 and we went after you!"
    )

    task1 >> [task2, task3]
    task2 >> [task4, task5]