import sys
import datetime as dt
import os
import shutil
import time
import boto3

from pathlib import Path

from airflow import DAG, settings
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable, Connection 
from airflow.configuration import conf
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

from utilities.preprocessors import reformat_date
from operators.create_s3_bucket import create_s3_bucket
from operators.pull_forex_data import pull_forex_data
from operators.test_pull_forex_data import test_pull_forex_data
from operators.transform_forex_data import transform_forex_data
from operators.move_raw_forex import move_raw_forex

from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import (
    LocalFilesystemToS3Operator,
)
from airflow.providers.amazon.aws.transfers.sql_to_s3 import SqlToS3Operator


# go to this site if you want to use cron instead of datetime to set schedule_interval
# https://crontab.guru/#00_12_*_*_Sun



def get_env_vars(ti):
    """
    push api key to xcom so that pull_forex_data can access
    this xcom
    """
    api_key = conf.get('secrets', 'polygon_api_key')

    ti.xcom_push(key="api_key", value=api_key)

# get airflow folder
AIRFLOW_HOME = conf.get('core', 'dags_folder')

# base dir would be /opt/***/ or /opt/airflow
BASE_DIR = Path(AIRFLOW_HOME).resolve().parent

# data dir once joined with base dir would be /opt/airflow/include/data/
DATA_DIR = os.path.join(BASE_DIR, 'include/data')

# bucket name
BUCKET_NAME = "usd-php-ml-pipeline-bucket"

default_args = {
    'owner': 'mikhail',
    'retries': 3,
    'retry_delay': dt.timedelta(minutes=2)
}

with DAG(
    dag_id="forex_ml_pipeline",
    default_args=default_args,
    description="pull forex of usd to php data from last january 1 2024 up to january 2025 in intervals of 4 hours",
    start_date=dt.datetime(2024, 1, 1, 12),

    # runs every sunday at 12:00 
    schedule_interval="00 12 * * Sun",
    catchup=False
) as dag:
    
    get_env_vars_task = PythonOperator(
        task_id="get_env_vars",
        python_callable=get_env_vars
    )

    create_s3_bucket_task = PythonOperator(
        task_id='create_s3_bucket',
        python_callable=create_s3_bucket,
        op_kwargs={
            'region': 'us-east-2',
            'bucket_name': BUCKET_NAME,
        }
    )
    
    pull_forex_data_task = PythonOperator(
        task_id='pull_forex_data',
        # python_callable=test_pull_forex_data,
        python_callable=pull_forex_data,
        op_kwargs={
            "start_date": "january 1 2022",
            "end_date": "january 1 2024",
            "forex_ticker": "C:USDPHP",
            "multiplier": 4,
            "timespan": "hour",
            "formatter": reformat_date,
            "bucket_name": BUCKET_NAME,
            "save_path": DATA_DIR
        }
    )

    move_raw_forex_task = PythonOperator(
        task_id='move_raw_forex',
        python_callable=move_raw_forex,
        op_kwargs={
            'region': 'us-east-2',
            'bucket_name': BUCKET_NAME,
            'filepath': "{{ti.xcom_pull(key='file_path', task_ids='pull_forex_data')}}",
            'destination': "raw/{{ti.xcom_pull(key='file_name', task_ids='pull_forex_data')}}",    
        }
    )
    
    transform_forex_data_task = SparkSubmitOperator(
        task_id='transform_forex_data',
        conn_id='my_spark_conn',
        application='./dags/operators/transform_forex_data.py',

        # pass argument vector to spark submit job operator since
        # it is a file that runs like a script
        application_args=["{{ti.xcom_pull(key='s3_raw_uri', task_ids='move_raw_forex')}}"],
        # application_args=["{{ti.xcom_pull(key='file_path', task_ids='pull_forex_data')}}"],
        verbose=True
    )
    
    [get_env_vars_task, create_s3_bucket_task] >> pull_forex_data_task >> move_raw_forex_task >> transform_forex_data_task