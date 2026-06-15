from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os
import pendulum


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.extract_data import fetch_data
from src.load_data import upload_to_s3, upload_to_snowflake

# Local TimeZone
local_tz = pendulum.timezone("Asia/Singapore")


default_args = {
    'owner': 'yqqq',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2026, 6, 1, tz=local_tz),
    'retries': 2,                       
    'retry_delay': timedelta(minutes=5),
}


def extract_load_to_s3_wrapper():
    symbols = ["bitcoin", "ethereum", "solana"]
    s3_key_dict = {}
    for symbol in symbols:
        raw_prices = fetch_data(symbol=symbol, limit=200)
        s3_key = upload_to_s3(raw_prices, symbol=symbol)
        if s3_key:
            s3_key_dict[symbol] = s3_key

    return s3_key_dict


def load_to_snowflake_wrapper(**kwargs):
    ti = kwargs['ti']
    # Pull s3 key
    s3_key_dict = ti.xcom_pull(task_ids='extract_and_upload_to_s3')
    
    for symbol, s3_key in s3_key_dict.items():
        upload_to_snowflake(s3_key, symbol=symbol)


# DAG pipeline
with DAG(
    dag_id='cryptocurrency_pipeline', 
    default_args=default_args,
    description='Fetch Data from CoinGecko and Load to AWS S3',
    schedule='0 2 * * *',     
    catchup=False,
) as dag:
    
    task_extract_and_load_s3 = PythonOperator(
        task_id='extract_and_upload_to_s3',
        python_callable=extract_load_to_s3_wrapper,
    )

    task_load_snowflake = PythonOperator(
        task_id='load_s3_to_snowflake',
        python_callable=load_to_snowflake_wrapper,
    )

    task_dbt_transform = BashOperator(
        task_id='dbt_run_transformations',
        bash_command='cd /opt/airflow/dbt_transform && dbt clean && dbt run --profiles-dir . && dbt test --profiles-dir .'
    )

    task_extract_and_load_s3 >> task_load_snowflake >> task_dbt_transform