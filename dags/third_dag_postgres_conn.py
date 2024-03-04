from dags_config import Config as config
from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(dag_id='third_dag_with_postgres_conn',
    default_args=config.DEFAULT_ARGS,
    description='This is our third dag with PostgresOperator to connect to a db and specifically Postgres!',
    start_date=datetime(2024, 2, 25, 2),
    schedule_interval='0 4 * * Mon,Wed,Fri',
    catchup=False) as dag:

    create_table = PostgresOperator(
        task_id='create_postgres_table',
        postgres_conn_id=config.POSTGRES_CONN_ID,
        sql="""
            CREATE TABLE IF NOT EXISTS dag_runs (
                dt date,
                dag_id character varying,
                primary key (dt, dag_id)
            );
        """ 
    )
    
    # ds and dag_id are airflow's template variable for dag run's date
    add_dag_run = PostgresOperator(
        task_id='insert_dag_to_table',
        postgres_conn_id=config.POSTGRES_CONN_ID,
        sql="""
            INSERT INTO dag_runs (dt, dag_id) VALUES (
                '{{ ds }}',
                '{{ dag.dag_id }}'
            );
        """ 
    )
    
    validate_unique_dag_run = PostgresOperator(
        task_id='delete_dag_from_table',
        postgres_conn_id=config.POSTGRES_CONN_ID,
        sql="""
            DELETE FROM dag_runs WHERE dt = '{{ ds }}' and dag_id = '{{ dag.dag_id }}'
        """ 
    )

    create_table >> validate_unique_dag_run >> add_dag_run