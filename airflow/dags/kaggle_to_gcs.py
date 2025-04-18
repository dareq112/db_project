from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from kaggle.api.kaggle_api_extended import KaggleApi
from google.cloud import storage
import os
import pandas as pd


KAGGLE_DATASET = f'{os.getenv('KAGGLE_USERNAME')}/data-fight-usa-dataset'
LOCAL_DIR = '/tmp/kaggle_downloads'
GCS_BUCKET = os.getenv('GCP_GCS_BUCKET')
GCS_FOLDER = 'raw'

client = storage.Client()

def download_csv_from_kaggle(execution_date, **kwargs):
    year = execution_date.year 
    file_name = f"{year}.csv"

    os.makedirs(LOCAL_DIR, exist_ok=True) 
 
    os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
    os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')

    api = KaggleApi() 
    api.authenticate()

    api.dataset_download_file(
        dataset=KAGGLE_DATASET,  
        file_name=file_name,     
        path=LOCAL_DIR,         
        force=True             
    )

    zip_path = os.path.join(LOCAL_DIR, file_name + '.zip')
    if os.path.exists(zip_path):
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(LOCAL_DIR)  
        os.remove(zip_path)

    return os.path.join(LOCAL_DIR, file_name)

def transform_csv(**kwargs):
    filepath = kwargs['ti'].xcom_pull(task_ids='download_csv_from_kaggle')
    df = pd.read_csv(filepath)

    df.drop(columns=['TaxiIn', 'TaxiOut', 'Cancelled', 'CancellationCode', 'Diverted', \
                     'CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay', 'LateAircraftDelay'], \
                     inplace=True)
    
    output_file_path = filepath.replace(".csv", "_transformed.csv")
    df.to_csv(output_file_path)

    print(output_file_path)
    return output_file_path

def upload_gcs_file(execution_date, **kwargs):
    input_filepath = kwargs['ti'].xcom_pull(task_ids="transform_csv")
    destination_filename = f"{GCS_FOLDER}/{execution_date.year}"
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(destination_filename)
    blob.upload_from_filename(input_filepath, timeout=300, retry=None)
    print(f"Uploaded {input_filepath} to {GCS_BUCKET}/{destination_filename}")


default_args = {
    'owner': 'airflow',
    'start_date': datetime(1987, 1, 1),
    'end_date': datetime(2007, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'kaggle_to_gcs',
    default_args=default_args,
    schedule_interval='@yearly',
    catchup=True
) as dag:

    download_from_kaggle = PythonOperator(
        task_id="download_csv_from_kaggle",
        python_callable=download_csv_from_kaggle,
        provide_context=True
    )

    transform_kaggle_csv = PythonOperator(
        task_id="transform_csv",
        python_callable=transform_csv,
        provide_context=True
    )

    upload_to_gcs = PythonOperator(
        task_id="upload_csv_to_gcs",
        python_callable=upload_gcs_file,
        provide_context=True
    )

    download_from_kaggle >> transform_kaggle_csv >> upload_to_gcs
