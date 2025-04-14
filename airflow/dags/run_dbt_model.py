import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Define your default arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

# Set up the Airflow DAG
with DAG(
    'dbt_airflow',
    default_args=default_args,
    schedule_interval=None, 
    catchup=False,
) as dag:

    run_dbt_staging = BashOperator(
        task_id='run_dbt_staging',
        bash_command='cd /opt/airflow/dbt && dbt deps && dbt run --models stg_flights',
    )

    run_dbt_seed = BashOperator(
        task_id='run_dbt_seed',
        bash_command='cd /opt/airflow/dbt && dbt seed'
    )

    run_dbt_core = BashOperator(
        task_id='run_dbt_core',
        bash_command='cd /opt/airflow/dbt && dbt run --models core_flights'
    )

    run_dbt_mart1 = BashOperator(
        task_id='run_dbt_mart1',
        bash_command='cd /opt/airflow/dbt && dbt run --models fact_departures_by_airport_year'
    )

    run_dbt_mart2 = BashOperator(
        task_id='run_dbt_mart2',
        bash_command='cd /opt/airflow/dbt && dbt run --models fact_delays_by_flight_num'
    )

    run_dbt_staging >> run_dbt_seed >> run_dbt_core >> run_dbt_mart1 >> run_dbt_mart2