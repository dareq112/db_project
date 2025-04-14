import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.utils.dates import days_ago

GCS_BUCKET_NAME = os.getenv('GCP_GCS_BUCKET')

default_args = {
    "start_date": days_ago(1)
}

def upload_to_gcs():
    gcs_hook = GCSHook()
    gcs_hook.upload(
        bucket_name=GCS_BUCKET_NAME,
        object_name="code/main_spark.py",
        filename="/opt/airflow/dags/spark_job/main_spark.py"
    )

with DAG(
    "spark_csv_to_bigquery",
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:
    
    upload_spark_to_gcs = PythonOperator(
        task_id="upload_spark_to_gcs",
        python_callable=upload_to_gcs
    )
    
    spark_job = {
        "reference": {"project_id": "db-project-456518"},
        "placement": {"cluster_name": "db-project-dataproc-cluster"},
        "pyspark_job": {
            "main_python_file_uri": "gs://db_project_data_bucket/code/main_spark.py"
        },
    }

    submit_job = DataprocSubmitJobOperator(
        task_id = "submit_spark_job",
        job = spark_job,
        region = "europe-central2",
        project_id = "db-project-456518"
    )

    upload_spark_to_gcs >> submit_job
