from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
import sys

sys.path.insert(0, '/opt/airflow/plugins')
from etl_utils import ETLUtils

# Configuração padrão do DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}

dag = DAG(
    'banvic_etl',
    default_args=default_args,
    description='Pipeline ETL BanVic',
    schedule_interval='35 4 * * *',  # Diário às 04:35
    catchup=False,
    tags=['etl', 'banvic'],
)

# Funções das tarefas

def extract_csv_task(**context):
    etl = ETLUtils()
    return etl.extract_csv_data(context['ds'])


def extract_sql_task(**context):
    etl = ETLUtils()
    return etl.extract_sql_data(context['ds'])


def load_csv_task(**context):
    etl = ETLUtils()
    csv_file = context['task_instance'].xcom_pull(task_ids='extract_csv_data')
    if not csv_file:
        csv_file = f"/opt/airflow/data/{context['ds']}/csv/transacoes.csv"
    return etl.load_csv_to_warehouse(csv_file)


def load_sql_task(**context):
    etl = ETLUtils()
    sql_files = context['task_instance'].xcom_pull(task_ids='extract_sql_data')
    if not sql_files:
        base_dir = f"/opt/airflow/data/{context['ds']}/sql"
        tables = ['agencias', 'clientes', 'colaboradores', 'colaborador_agencia', 'contas', 'propostas_credito']
        sql_files = {table: f"{base_dir}/{table}.csv" for table in tables}
    return etl.load_sql_to_warehouse(sql_files)


def validate_task(**context):
    etl = ETLUtils()
    if not etl.validate_data_quality():
        raise ValueError("Validation failed")
    return "OK"

# Definição de tarefas
start_task = EmptyOperator(task_id='start_etl', dag=dag)

# Extrações paralelas
extract_csv = PythonOperator(
    task_id='extract_csv_data',
    python_callable=extract_csv_task,
    dag=dag,
)

extract_sql = PythonOperator(
    task_id='extract_sql_data',
    python_callable=extract_sql_task,
    dag=dag,
)

# Sincronização
sync_tasks = EmptyOperator(task_id='sync_extractions', dag=dag)

# Carregamentos paralelos
load_csv = PythonOperator(
    task_id='load_csv_data',
    python_callable=load_csv_task,
    dag=dag,
)

load_sql = PythonOperator(
    task_id='load_sql_data',
    python_callable=load_sql_task,
    dag=dag,
)

# Validação
validate = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_task,
    dag=dag,
)

# Fluxo: extrações paralelas -> sincronização -> carregamentos paralelos -> validação
start_task >> [extract_csv, extract_sql] >> sync_tasks >> [load_csv, load_sql] >> validate
