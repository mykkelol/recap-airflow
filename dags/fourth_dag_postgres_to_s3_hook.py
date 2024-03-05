import csv
import logging
from tempfile import NamedTemporaryFile
from dags_config import Config as config
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

# ds_nodash and next_ds_nodash are airflow macros for dates of when dags executed and when it executes next, respectively
def postgres_to_s3(ds_nodash, next_ds_nodash):
    # step1: query data from postgresql db and save locally as csv
    postgres_hook = PostgresHook(postgres_conn_id=config.POSTGRES_CONN_ID)
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM orders WHERE date >= %s', (ds_nodash,))
    # I work too late so below doesn't work xd
    # cursor.execute('SELECT * FROM orders WHERE date >= %s AND date < %s', (ds_nodash, next_ds_nodash))
    
    with NamedTemporaryFile(mode='w', suffix=f'{ds_nodash}') as f:
    # below writes files locally and can be obnoxious, we can use pickle or NamedTemporaryFile
    # with open(f'dags/orders_{ds_nodash}.csv', 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow((i[0] for i in cursor.description))
        csv_writer.writerows((cursor))
        f.flush()
        cursor.close()
        conn.close()
        logging.info(f'Saved orders data through NamedTemporaryFile in dags/orders_{ds_nodash}.csv\n'
             f'for execution on {ds_nodash},\n'
             f'next is {next_ds_nodash}')
    
    # step2: upload csv to s3
        s3_hook = S3Hook(aws_conn_id=config.S3_CONN_ID)
        s3_hook.load_file(
            filename=f.name,
            key=f'orders_{ds_nodash}.csv',
            bucket_name='airflow',
            replace=True #replaces the file if exists in the bucket
        )
        logging.info("Orders file %s has been pushed to S3!", f.name)


with DAG(dag_id='fourth_dag_hook_postgres_to_s3',
    default_args=config.DEFAULT_ARGS,
    description='This is our fouth dag to hook PostgresQL to S3 as csv!',
    start_date=datetime(2024, 2, 25, 2),
    schedule_interval='@daily',
    catchup=False) as dag:

    start = PythonOperator(
        task_id='postgres_to_s3',
        python_callable=postgres_to_s3
    )

    start