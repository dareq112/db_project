import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'run_dbt',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,          
) as dag:

    def run_dbt_command(command: str, task_id: str):
        return BashOperator(
            task_id=task_id,
            bash_command=f'cd /opt/airflow/dbt && {command}',
        )

    run_dbt_deps = run_dbt_command('dbt deps', 'run_dbt_deps')

    run_dbt_seed = run_dbt_command('dbt seed', 'run_dbt_seed')

    run_dbt_all_models = run_dbt_command('dbt run', 'run_dbt_all_models')

    run_dbt_deps >> run_dbt_seed >> run_dbt_all_models