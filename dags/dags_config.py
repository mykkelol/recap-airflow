from datetime import timedelta

class Config:

    DEFAULT_ARGS = {
        'owner': 'mykke',
        'retries': 5,
        'retry_delay': timedelta(minutes=2)
    }