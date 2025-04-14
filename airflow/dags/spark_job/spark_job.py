import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.utils.dates import days_ago

GCS_BUCKET_NAME = os.getenv('GCP_GCS_BUCKET')
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')


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
        "reference": {"project_id": f"{GCP_PROJECT_ID}"},
        "placement": {"cluster_name": "db-project-dataproc-cluster"},
        "pyspark_job": {
            "main_python_file_uri": f"gs://{GCS_BUCKET_NAME}/code/main_spark.py"
        },
    }

    submit_job = DataprocSubmitJobOperator(
        task_id = "submit_spark_job",
        job = spark_job,
        region = "europe-central2",
        project_id ={GCP_PROJECT_ID}
    )

    upload_spark_to_gcs >> submit_job
