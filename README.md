# Data Engineering Zoomcamp Final Project

## Problem Description

This project focuses on analyzing a subset of the **airline on-time performance dataset** from **1987 to 1992**, covering detailed flight arrival and departure information for all commercial flights within the USA during this period. The data is derived from the **RITA (Research and Innovative Technology Administration)**, providing insights into airline operations, delays, cancellations, and more.

The dataset spans **5 years** of operations, containing millions of records, and is highly valuable for understanding early trends and factors that influenced flight performance in the late 1980s and early 1990s.

### Key Insights:
- Flight operations
- Delays and cancellations
- Factors influencing flight performance
- Trends in airline industry performance across the years

![Map Image](img/flights_map.png)

---

## Tools & Technologies Used

For this project, I leveraged the following tools:

- **Google Cloud Platform (GCP)**: Primary cloud provider for hosting services, offering a range of managed solutions.
  
- **Google Cloud Storage (GCS)**: Utilized as the data lake storage within GCP.

- **Google Cloud DataProc**: Running Spark Cluster

- **BigQuery**: Applied as the data warehouse solution for large-scale data analysis.

- **Terraform**: Used as the Infrastructure-as-Code (IaC) tool to automate and provision cloud resources.

- **Airflow**: Orchestration tool for managing and scheduling the end-to-end data pipeline.

- **Spark**: Leveraged for distributed data processing and transformations at scale.

- **DBT (Data Build Tool)**: Implemented for transforming data within the data warehouse, focusing on analytics engineering, modularity, and version control.

- **Looker Studio**: Utilized for creating interactive, dynamic, and customizable data visualizations and reports.

---

## Project Workflow

This combination of tools enabled efficient data management, transformation, and visualization, all within an automated and scalable pipeline. The goal was to analyze flight data, identify trends, and generate meaningful insights that can inform understanding of flight performance during the 1987-1992 period.

---

## Project Setup and Code Reproduction

To run the project code, several steps and configurations are required.

### 1. Google Cloud Platform (GCP)

Make sure the following prerequisites are completed:

- Have an active account on **Google Cloud Platform (GCP)**.
- Create a **Service Account**.
- Assign the following roles to the service account:
  - `Storage Admin`
  - `BigQuery Admin`
  - `Storage Object Admin`  
  *(Alternatively, you can assign the `Owner` role to grant all necessary permissions.)*
- Enable the following APIs in your GCP project:
  - **Cloud Logging API**  
  - **Cloud Monitoring API**  
  - **Cloud Dataproc Control API**  
  - **Cloud Dataproc API**  
  - **BigQuery API**  
  - **Compute Engine API**  
  - **Cloud Dataplex API**  
  - **Cloud Storage API**
- Download the **JSON key** for your service account. This key is required to authenticate the tools used in this project with GCP.
- Save the JSON key in the following directories:
  - In the `terraform/` directory as: `gcs-key.json`
  - In the `airflow/config/` directory as: `gcs-key.json`

---

### 2. Terraform Setup

To provision the necessary infrastructure on GCP, Terraform must be installed and configured.

#### Step 1: Install Terraform

Download and install Terraform from the official website:  
👉 [https://www.terraform.io/downloads](https://www.terraform.io/downloads)

Follow the installation instructions for your operating system.

---

#### Step 2: Configure `terraform.tfvars`

Navigate to the `terraform/` directory in the project.  
Edit the `terraform.tfvars` file with your specific configuration values, including:

```hcl
project_id       = "<your-gcp-project-id>"
region           = "<your-region>"
credentials_file = "gcs-key.json"
bucket_name      = "<your-bucket-name>"
dataset_id       = "<your-dataset-id>"
cluster_name     = "<your-cluster-name>"
```

Run the following commands from inside the terraform/ directory:
```bash
terraform init
terraform plan
terraform apply
```

### 3. Downloading the Dataset

The dataset used in this project is publicly available on the Harvard Dataverse platform:

🔗 [Airline On-Time Performance Dataset (1987–1992)](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/HG7NV7)

However, **direct download links are not available** via API or scripts. Therefore, the data for the years **1987 to 1992 must be downloaded manually** from the website.

#### Instructions:

1. Visit the dataset page:  
   [https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/HG7NV7](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/HG7NV7)

2. Download the `.csv` files for the following years:
   - 1987
   - 1988
   - 1989
   - 1990
   - 1991
   - 1992

3. After downloading, upload all the files to the **`raw/` folder** in your **GCS bucket**, which was created using Terraform.

   You can do this manually using the GCP Console or via the `gsutil` CLI. For example:

   ```bash
    gsutil cp <path-to-local-csv-file> gs://<your-bucket-name>/raw/
   ```

### 4. Airflow Setup

Before running Airflow, make sure to configure the appropriate environment variables in the `docker-compose.yaml` file. These variables are necessary for authenticating with GCP and enabling Airflow to communicate with Google Cloud services.

#### Required Environment Variables

Inside your `docker-compose.yaml`, set the following:

```yaml
environment:
  - GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/config/gcp-key.json
  - AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT=google-cloud://?key_path=%2Fopt%2Fairflow%2Fconfig%2Fgcp-key.json&project=<your-project-id>
  - GCP_PROJECT_ID=<your-project-id>
  - GCP_GCS_BUCKET=<your-gcs-bucket-name>
```

Replace <your-project-id> and <your-gcs-bucket-name> with your actual project and bucket names. Do not use quotation marks in the YAML if your values are plain strings.

Build the Airflow Docker Image
Once the environment variables are set, build the Airflow image using:
    ```bash
    docker-compose build
    ```
Run Airflow
To start the Airflow services, run:
```bash
docker-compose up
```
This will launch the Airflow webserver, scheduler, and any other defined services. You should be able to access the Airflow UI at http://localhost:8080.

### Airflow & DBT Workflow

Once the infrastructure is deployed and raw data is uploaded to GCS, the data pipeline is orchestrated using **Airflow** with multiple DAGs handling each stage of the process.

#### 1. `first_stage` DAG

The first step in the pipeline is to trigger the `first_stage` DAG. This DAG performs the following tasks:

- Reads raw CSV files from the `raw/` folder in the GCS bucket.
- Applies basic cleaning and transformation.
- Writes the cleaned data into the `staging/` folder within the same GCS bucket.

This staging area serves as the intermediate zone before advanced processing and analytics.

---

#### 2. `spark_job` DAG

Once the data is staged, the `spark_job` DAG should be triggered. It performs the core transformation using a Spark job running on a Dataproc cluster.

Key steps:

- Uploads the `main_spark.py` script into the `code/` folder in the GCS bucket.
- Submits this script to the **Dataproc cluster**, which executes the following logic:
  - Defines a schema using `StructType` to enforce data types.
  - Renames and casts columns to appropriate types.
  - Joins flight data with the `carriers` reference table for enriched context.
  - Writes the final, transformed table into **BigQuery**.

The resulting BigQuery table is:

- **Partitioned** by the year of the flight (`Year` column).
- **Clustered** by the `Origin` column, which represents the departure airport.

This setup ensures efficient storage and faster querying performance.



The execution of DBT models is handled automatically by Airflow through the DAG:  
**run_dbt_model.py**

This DAG is triggered **as the final step** in the pipeline after:

1. Data has been staged by the first_stage DAG.
2. Spark processing has been completed by the spark_job DAG.

The DAG runs the DBT CLI inside the container and builds models in the correct order based on their dependencies, ensuring that the final analytics tables in the marts/ layer are ready for consumption.

### Looker Studio

Once the data has been processed and stored in BigQuery, you can create interactive visualizations using **Looker Studio**.

#### Steps to Create a Dashboard:

1. **Navigate to Looker Studio**:
   Go to [Looker Studio](https://lookerstudio.google.com/) and sign in with your Google account.

2. **Create a New Data Source**:
   - Click on the **Create** button.
   - Select **Data Source** from the dropdown menu.

3. **Connect to BigQuery**:
   - In the data source configuration, choose **BigQuery** as the connection type.
   - Select the appropriate **BigQuery project** and **dataset**.
   - Choose the relevant tables that you want to use for your reports.

4. **Build the Dashboard**:
   - After connecting to your BigQuery tables, use the **Chart** options to create various visualizations (e.g., bar charts, line charts, tables, etc.).
   - Drag the relevant data fields from the right-hand panel into your charts. You may need to add the following additional fields:
     - **Year**: YEAR(flight_date) — to extract the year of the flight from the flight_date field.
     - **Month**: MONTH(flight_date) — to extract the month of the flight from the flight_date field.

![Map Image](img/flights_map.png)





