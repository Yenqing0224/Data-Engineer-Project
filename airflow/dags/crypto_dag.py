from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.extract_data import fetch_data
from src.load_data import upload_to_s3


default_args = {
    'owner': 'yqqq',
    'depends_on_past': False,
    'start_date': datetime(2026, 6, 1),
    'retries': 2,                       
    'retry_delay': timedelta(minutes=5),
}


def upload_wrapper(**kwargs):
    ti = kwargs['ti']
    
    data = ti.xcom_pull(task_ids='fetch_from_CoinGecko')
    
    upload_to_s3(data=data)


# DAG pipeline
with DAG(
    dag_id='cryptocurrency_pipeline', 
    default_args=default_args,
    description='Fetch Data from CoinGecko and Load to AWS S3',
    schedule='0 2 * * *',     
    catchup=False,
) as dag:
    
    task_extract_data = PythonOperator(
        task_id='fetch_from_CoinGecko',
        python_callable=fetch_data,
    )

    task_load_data = PythonOperator(
        task_id='upload_data_to_S3',
        python_callable=upload_wrapper,
    )

    task_extract_data >> task_load_data