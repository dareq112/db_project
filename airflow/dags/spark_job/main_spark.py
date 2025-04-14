import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, FloatType
from pyspark.sql.functions import col, year, lpad, concat_ws, to_timestamp, to_date, format_string, substring, length
import pyspark.sql.functions as F

GCS_BUCKET_NAME = os.getenv('GCP_GCS_BUCKET')
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

#Creating basic spark session
spark = SparkSession.builder \
    .appName("Transform the data from GCS and save to BigQuery") \
    .config("spark.hadoop.fs.gs.project.id", f"{GCP_PROJECT_ID}") \
    .config("spark.hadoop.fs.gs.bucket", f"{GCS_BUCKET_NAME}") \
    .getOrCreate()

#Preparing schema for staging data
staging_schema = StructType([
    StructField("Year", IntegerType(), True),
    StructField("Month", IntegerType(), True),
    StructField("DayOfMonth", IntegerType(), True),
    StructField("DayOfWeek", IntegerType(), True),
    StructField("DepTime", StringType(), True),
    StructField("CRSDepTime", StringType(), True),
    StructField("ArrTime", StringType(), True),
    StructField("CRSArrTime", StringType(), True),
    StructField("UniqueCarrier", StringType(), True),
    StructField("FlightNum", IntegerType(), True),
    StructField("TailNum", FloatType(), True),
    StructField("ActualElapsedTime", FloatType(), True),
    StructField("CRSElapsedTime", IntegerType(), True),
    StructField("AirTime", StringType(), True),
    StructField("ArrDelay", FloatType(), True),
    StructField("DepDelay", FloatType(), True),
    StructField("Origin", StringType(), True),
    StructField("Dest", StringType(), True),
    StructField("Distance", FloatType(), True),
])

#Preparing schema for seed data (carriers table to join)
carriers_schema = StructType([
    StructField("CarrierCode", StringType(), True),
    StructField("CarrierDescription", StringType(), True)
])

#Loading the data from GCS bucket staging folder
df_staging = spark.read.csv(f'gs://{GCS_BUCKET_NAME}/staging/*.csv', schema=staging_schema, header=True)

#Loading the data from GCS bucket seeds folder carriers file
df_seeds = spark.read.csv(f'gs://{GCS_BUCKET_NAME}/seeds/carriers.csv', schema=carriers_schema, header=True)

df_transformed = df_staging \
    .withColumn("FlightDate", to_date(format_string("%04d-%02d-%02d", col("Year"), col("Month"), col("DayOfMonth")))) \
    .withColumn("DepTimePadded", lpad(col("DepTime"), 4, "0")) \
    .withColumn("DepTimeFormatted",
                   concat_ws(":",
                             substring(col("DepTimePadded"), 1, 2),
                             substring(col("DepTimePadded"), 3, 2)
                   )) \
    .withColumn("ArrTimePadded", lpad(col("ArrTime"), 4, "0")) \
    .withColumn("ArrTimeFormatted",
                   concat_ws(":",
                             substring(col("ArrTimePadded"), 1, 2),
                             substring(col("ArrTimePadded"), 3, 2)
                   )) \
    .drop('ArrTimePadded', 'DepTimePadded')

#Join carriers table to our transformed table
df_joined = df_transformed.join(df_seeds, df_transformed["UniqueCarrier"] == df_seeds["CarrierCode"], how="inner")

df_joined.show(truncate=False)

# Writing the final result to BigQuery
# Using partition on year column and clustering on origin (origin airport)
df_joined.write.format("bigquery") \
    .option("table", f"{GCP_PROJECT_ID}.db_project_dataset.flights_data") \
    .option("temporaryGcsBucket", f"gs://{GCS_BUCKET_NAME}/temp/") \
    .option("partitionField", "FlightDate") \
    .option("clusteringFields", "Origin") \
    .mode("overwrite") \
    .save()
    