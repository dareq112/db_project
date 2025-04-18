import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
from pyspark.sql.functions import col, to_date, format_string, date_format
import pyspark.sql.functions as F

GCS_BUCKET_NAME = '' #Your bucket name Bucket must be hard-coded as script is run in DataProc cluster
GCP_PROJECT_ID = '' #Your project ID Project ID must be hard-coded as script is run in DataProc cluster

print(GCS_BUCKET_NAME, GCP_PROJECT_ID)
#Creating basic spark session
spark = SparkSession.builder \
    .appName("Transform the data from GCS and save to BigQuery") \
    .config("spark.hadoop.fs.gs.project.id", GCP_PROJECT_ID) \
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
df_staging = spark.read.csv(f'gs://{GCS_BUCKET_NAME}/raw/*.csv', schema=staging_schema, header=True)

#Loading the data from GCS bucket seeds folder carriers file
df_seeds = spark.read.csv(f'gs://{GCS_BUCKET_NAME}/seeds/carriers.csv', schema=carriers_schema, header=True)

df_transformed = df_staging \
    .withColumn("FlightDate", to_date(format_string("%04d-%02d-%02d", col("Year"), col("Month"), col("DayOfMonth")))) \
    .withColumn("DepTimeFormatted",
        F.when(
            F.length("DepTime") == 3,
            F.concat(F.lit("0"), F.substring("DepTime", 1, 1), F.lit(":"), F.substring("DepTime", 2, 2))
        ).when(
            F.length("DepTime") == 4,
            F.concat(F.substring("DepTime", 1, 2), F.lit(":"), F.substring("DepTime", 3, 2))
        )
    ) \
    .withColumn("ArrTimeFormatted",
        F.when(
            F.length("ArrTime") == 3,
            F.concat(F.lit("0"), F.substring("ArrTime", 1, 1), F.lit(":"), F.substring("ArrTime", 2, 2))
        ).when(
            F.length("ArrTime") == 4,
            F.concat(F.substring("ArrTime", 1, 2), F.lit(":"), F.substring("ArrTime", 3, 2))
        )
    ) \

#Join carriers table to our transformed table
df_joined = df_transformed.join(df_seeds, df_transformed["UniqueCarrier"] == df_seeds["CarrierCode"], how="inner")

df_joined.show(truncate=False)

df_joined = df_joined.withColumn("FlightMonth", date_format("FlightDate", "yyyy-MM"))

# Writing the final result to BigQuery
# Using partition on year column and clustering on origin (origin airport)
df_joined.write.format("bigquery") \
    .option("table", f"{GCP_PROJECT_ID}.db_project_dataset.flights_data") \
    .option("temporaryGcsBucket", f"gs://{GCS_BUCKET_NAME}/temp/") \
    .option("partitionField", "FlightMonth") \
    .option("clusteringFields", "Origin") \
    .mode("overwrite") \
    .save()
    