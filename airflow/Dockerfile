FROM apache/airflow:2.10.5

# Set Airflow home directory
ENV AIRFLOW_HOME=/opt/airflow

# Switch to root user to install dependencies
USER root

# Install necessary system packages
RUN apt-get update -qq && apt-get install -y \
    vim \
    git \
    gcc \
    g++ \
    && apt-get clean

# Copy requirements file
COPY requirements.txt .

# Switch back to the Airflow user
USER airflow

# Install Python dependencies from requirements.txt and additional dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Set the default command to run Airflow's webserver
CMD ["bash", "-c", "airflow webserver"]