# Airflow

- Airflow is platform to manage complex workflows (see [Figure 1.00 of DAG components](#figure-100))
- Workflows are DAGs (directed acyclic graphs) and consists of Tasks.
- Tasks performs operators which consists of BashOperator, PythonOperator, CustomizedOperator, etc.
- Operators can leverage Hooks to conneect and perform actions on external systems

### Figure 1.00

![Figure 1.00](./images/00_basic.png)

# Execution and Task Lifecycle

- Once DAGs are scheduled and finally executed, tasks are orchestrated to execute one after another according to their dependencies but this doesn't mean DAGs are synchronous (see [Figure 1.00 how A triggers C and B asynchronously](#figure-100)) and can be categorized into three groups (scheduler stages, worker stages, and executor stages)
- The task lifecycle are scheduled to go through 11 different stages (see [Figure 1.01](#figure-101)):
  - Scheduler stages
    - **no_status** - scheduler created an empty task instance
    - **scheduled** - scheduler created a task instance to execute and can encounter statuses such as _skipped_, _removed_, or _upstream_failed_
      - **upstream_failed** - current task's upstream failed and cannot run (see [Figure 1.0 if A fails then B encounters upstream fail](#figure-101))
  - Executor stages
    - **queued** - scheduler sent task to executor to run and wait for when a worker is available (worker is when the computation resource is not occuppied)
  - Worker stages
    - **running** - removes from queue and runs after a worker is assigned, which can encounter _success_, _failed_ or _shutdown_
      - **up_for_retry** - if a task fails or shutdown, it will retry the entire lifestyle

### Figure 1.01

![Figure 1.01](./images/01_task_lifecycle.png)

# User of Airflow

- Typically, data engineers manages Airflow to maintain the following:
  - configurations in airflow.cfg
  - authoring and maintaining DAGs
  - navigating through airflow UI hosted in webserver (typically Docker) to manage DAGs, schedulers, executors, and workers which are all connected to some DB such as postgres, MySQL, etc.

# Airflow nuances

- **XComs** - data sharing and passing values between tasks via taskinstance (or `ti`). HOWEVER, the max XCom size is tiny and only 48kb
- **TaskflowAPI** - using XComs to data share between tasks can be verbose but with Taskflow API, this XCom process is simplifed as TaskflowAPI provides decorators to easily define data sharing and task dependencies
- **schedule_interval** - predefined intervals such as @once, @daily, @weekly, etc. are just predefined cron expressions but this parameter can have both cron or timedelta as args
- **backfill** vs. **catchup** - while both serves the same purpose—to execute tasks for past periods—they differ in that:
  - **catchup** is the automatic approach and only requires us to set `catchup=True` directly in dag definition (see [second_dag_taskflowapi.py](./dags/second_dag_taskflowapi.py))
  - **backfill** is the manual approach and requires the following steps:
    1. `docker ps` to retrieve CONTAINER_ID of airflow_docker-airflow-scheduler-1
    1. `docker exec -it CONTAINER_ID bash`
    1. `airflow dags backfill s START_DATE e END_DATE`
- **DB Connection** - in general, it's recommended in Airflow to delete rows before inserting them into db (see [third_dag_postgres_conn.py](./dags/third_dag_postgres_conn.py)) to avoid primary key constraint and row duplication
- **Airflow Sensors** - a special type of operator which waits for something to occur to trigger task when exact time is unknown (see [To install S3 Sensor](#to-install-s3-sensor)) and is similar to polling but has two ways to do this: poke (the default and used for polling within seconds, requiring worker basically forever) or reschedule (used for polling within minutes but only requires worker when it is polling)

# Running Airflow in Docker

### To set-up

1. `docker --version`
1. `docker-compose --version`
1. curls for [airflow docker yaml](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
1. `mkdir -p ./dags ./logs ./plugins ./config`
1. `docker-compose up airflow-init`
1. `docker-compose up -d`
1. `docker ps` to see running containers

### To launch airflow and its container

1. `docker-compose up airflow-init`
1. `docker-compose up -d`

### To shutdown airflow and its container

1. `docker-compose down -v`

### To connect to Postgres

1. add `ports` 5432:5432 under `services / postgres` in [docker-compose.yaml](docker-compose.yaml)
1. download dbeaver or db management equivalent
1. create a new database conn with PostgresQL with the following and test conn accordingly
   - `Host` - localhost
   - `Username`
   - `Password`
1. create a db as needed in PostgresQL
1. create Airflow conn to Postgres with the following
   - `Host` - host.docker.internal
   - `Database` - name of db created from prev step
   - `Login`, `Password` - from step 3
   - `Port` - from step 1
1. run postgres operator like [third_dag_postgres_conn.py](./dags/third_dag_postgres_conn.py)!

### To install py dependencies

We can install dependencies in two ways; by extending or customizing. Choosing between the two approaches is typical build vs buy conundrum (customize is lightweight and especially useful for optimization but takes time and is complex to build, etc.). Extending is most common and the steps are as follow (customization is similar but requires us to build our own airflow version by forking the original repo):

1. add dependencies in [requirements.txt](./requirements.txt)
1. add Dockerfile in [Dockerfile](./Dockerfile) to instruct docker to extend airflow with dependencies
1. `docker build . --tag extending-airflow:latest` to build an image with name "extending-airflow" using Dockerfile in root directory with version latest
1. update `airflow-common/image/` from `-apache/airflow:2.8.2` to `extending-airflow:latest` from previous step in [docker-compose.yaml](./docker-compose.yaml)
1. import dependencies accordignly like in [second_dag.py](./dags/second_dag.py)
1. `docker-compose up -d --no-deps --build airflow-webserver airflow-scheduler` to rebuild and relaunch the webserver and scheduler

### To install s3 sensor

1. setup S3 service (AWS S3, MinIO)
   - run Rootful commands to create docker image for S3 [MinIO Docker S3 Quick Start](https://min.io/docs/minio/container/index.html)
   - once completed, addresses and URLs for S3 API (used for creating AWS conn) and MinIO Console (actual UI for buckets!) are provided for login with ports (used for creating AWS conn)
1. follow steps in [to install py dependencies](#to-install-py-dependencies) to extend airflow with dependencies
1. `docker-ps` to retrieve airflow_docker-airflow-scheduler-1 contain ID
1. `docker exec -it CONTAINER_ID bash` to access container
1. `pip list | grep amazon` to retrieve Amazon provider version
1. access [Airflow's Amazon provider package](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/index.html) with the correct version that matches our local airflow installation
1. access [Amazon provider package's Python reference](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/index.html) and look for S3 Sensors
1. access [AWS S3 Sensor documentation](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/sensors/s3/index.html) to retrieve its class/module directory
1. set-up s3 conn and use the Sensor operator like [second_dag.py](./dags/second_dag.py)! Conn requires:
   - `aws_access_key_id` - S3 service account name
   - `aws_secret_access_key` - S3 service account password
   - `host` - "http://host.docker.internal:{PORT}/"
