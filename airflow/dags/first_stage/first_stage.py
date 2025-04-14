from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from google.cloud import storage
import pandas as pd
import os
import bz2

# Retrieve the environment variables
GCS_BUCKET_NAME = os.getenv('GCP_GCS_BUCKET')
GCS_DEST_FOLDER = 'staging'

# Google Cloud Storage client
client = storage.Client()

# Function to download file from GCS to local filesystem
def download_gcs_file(bucket_name, source_file_name, destination_file_name):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_file_name)
    print(f"Downloading {source_file_name} from bucket {bucket_name} to {destination_file_name}")
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {bucket_name}/{source_file_name} to {destination_file_name}")

# Function to upload a file from local filesystem to GCS
def upload_gcs_file(bucket_name, source_file_name, destination_file_name):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_file_name)
    blob.upload_from_filename(source_file_name, timeout=300, retry=None)
    print(f"Uploaded {destination_file_name} to {bucket_name}/{source_file_name}")

# Function to load data from GCS and process it
def gcs_source(execution_date):
    source_file_name = f"raw/{execution_date}.csv.bz2"
    destination_file_name = f"/tmp/{execution_date}.csv.bz2"
    extracted_csv_path = f"/tmp/{execution_date}.csv"

    print(f"Source File Path: {source_file_name}")
    print(f"Destination File Path: {destination_file_name}")

    download_gcs_file(GCS_BUCKET_NAME, source_file_name, destination_file_name)

    with bz2.open(destination_file_name, "rt") as file, open(extracted_csv_path, "w") as out_file:
        out_file.write(file.read())

    return extracted_csv_path

# Remove unnecessary columns and transform data
def transform_data(input_file_path):
    df = pd.read_csv(input_file_path)

    df.drop(columns=['TaxiIn', 'TaxiOut', 'Cancelled', 'CancellationCode', 'Diverted', 'CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay', 'LateAircraftDelay'], inplace=True)

    output_file_path = input_file_path.replace(".csv", "_transformed.csv")
    df.to_csv(output_file_path, index=False)
    print("Data saved to _transformed.csv")

    return output_file_path


# Write the processed data back to GCS
def gcs_destination(file_path, execution_date):
    destination_blob_name = f"{GCS_DEST_FOLDER}/{execution_date}.csv"
    upload_gcs_file(GCS_BUCKET_NAME, file_path, destination_blob_name)

# Define the Airflow DAG
with DAG(
    'gcs_dlt_data_pipeline',
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    },
    description="pipeline from GCS to GCS",
    schedule_interval='0 0 1 1 *',  # Once per year on January 1st
    start_date=datetime(1987, 1, 1),  # Start from January 1st, 1987
    end_date=datetime(1992, 1, 1),  # End on January 1st, 2008
    catchup=False,
) as dag:

    download_task = PythonOperator(
        task_id='download_file',
        python_callable=gcs_source,
        op_kwargs={'execution_date': '{{ execution_date.year }}'},
    )

    process_task = PythonOperator(
        task_id='process_data',
        python_callable=transform_data,
        op_args=['{{ ti.xcom_pull(task_ids="download_file") }}'],
        execution_timeout=timedelta(hours=1),
    )

    upload_task = PythonOperator(
        task_id='upload_file',
        python_callable=gcs_destination,
        op_kwargs={
            'file_path': '{{ ti.xcom_pull(task_ids="process_data") }}',
            'execution_date': '{{ execution_date.year }}'
        },
    )
    download_task >> process_task >> upload_task
