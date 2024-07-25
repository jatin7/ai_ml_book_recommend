from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 24),
    'email': ['alert@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'run_py_dag',
    default_args=default_args,
    description='A DAG to run python scripts using BashOperator',
    schedule_interval=timedelta(days=1),
)

# Define the tasks using BashOperator
t1 = BashOperator(
    task_id='getSeattleLibrary',
    bash_command='python scripts/getSeattleLibrary.py',
    dag=dag,
)

t2 = BashOperator(
    task_id='inventory_preprocessing',
    bash_command='python scripts/inventory_preprocessing.py',
    dag=dag,
)

t3 = BashOperator(
    task_id='audio_processing',
    bash_command='python scripts/audio_processing.py',
    dag=dag,
)

t4 = BashOperator(
    task_id='audio_linkgeneration',
    bash_command='python scripts/audio_linkgeneration.py',
    dag=dag,
)

# Define the order of execution of tasks
t1 >> t2 >> t3 >> t4
