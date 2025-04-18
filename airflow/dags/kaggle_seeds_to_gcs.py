from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from kaggle.api.kaggle_api_extended import KaggleApi
from google.cloud import storage
import os

# Using Kaggle API to download .csv files (seeds) and saving to GCS
KAGGLE_DATASET = f'{os.getenv("KAGGLE_USERNAME")}/data-fight-usa-dataset'
LOCAL_DIR = '/tmp/kaggle_downloads'
GCS_BUCKET = os.getenv('GCP_GCS_BUCKET')
GCS_FOLDER = 'seeds'

# Google Cloud Storage client
client = storage.Client()

def download_seeds_from_kaggle(**kwargs):
    seed_files = ['carriers.csv', 'airports.csv', 'plane-data.csv']
    os.makedirs(LOCAL_DIR, exist_ok=True) 

    os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
    os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')

    api = KaggleApi() 
    api.authenticate()

    downloaded_files = []
    for file_name in seed_files:
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
        
        downloaded_files.append(os.path.join(LOCAL_DIR, file_name))

    return downloaded_files

def upload_gcs_seeds_file(**kwargs):
    files_to_upload = kwargs['ti'].xcom_pull(task_ids="download_seeds_from_kaggle")
    for file in files_to_upload:
        destination_filename = f"{GCS_FOLDER}/{os.path.basename(file)}"
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(destination_filename)
        blob.upload_from_filename(file, timeout=300, retry=None)
        print(f"Uploaded {file} to {GCS_BUCKET}/{destination_filename}")


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'kaggle_seeds_to_gcs',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False
) as dag:

    download_seeds_from_kaggle = PythonOperator(
        task_id="download_seeds_from_kaggle",
        python_callable=download_seeds_from_kaggle,
    )

    upload_seeds_to_gcs = PythonOperator(
        task_id="upload_seeds_to_gcs",
        python_callable=upload_gcs_seeds_file,
    )

    download_seeds_from_kaggle >> upload_seeds_to_gcs