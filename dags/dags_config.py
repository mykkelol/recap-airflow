from datetime import timedelta

class Config:

    DEFAULT_ARGS = {
        'owner': 'mykke',
        'retries': 5,
        'retry_delay': timedelta(minutes=2)
    }

    POSTGRES_CONFIG = {
        "host": "host.docker.internal",
        "port": "5432",
        "db": 0
    }

    POSTGRES_CONN_ID = "postgres_localhost"
    
    S3_CONFIG = {
        "host": "host.docker.internal",
        "port": "5432",
        "db": 0
    }

    S3_CONN_ID = "minio_conn"
