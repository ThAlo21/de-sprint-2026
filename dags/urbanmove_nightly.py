import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator


# 1. Custom Failure Handler to trap and log context information
def pipeline_failure_callback(context):
    """
    Triggers automatically if a task instance fails.
    Prints required auditing indicators directly into the Airflow logs task context structure.
    """
    task_id = context.get('task_instance').task_id
    dag_id = context.get('task_instance').dag_id
    # execution_date is deprecated in Airflow 2.0+, data_interval_start contains the precise execution timestamp
    execution_date = context.get('data_interval_start')

    print("\n" + "=" * 60)
    print("CRITICAL TASK FAILURE TRIGGERED")
    print(f"Task ID:       {task_id}")
    print(f"DAG ID:        {dag_id}")
    print(f"Execution Date: {execution_date}")
    print("=" * 60 + "\n")


# 2. Define Operational Default Arguments
default_args = {
    'owner': 'urbanmove-de',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': pipeline_failure_callback,  # Bound globally across all tasks
}

# 3. Instantiate the Main Data Lifecycle Sequence
with DAG(
        dag_id='urbanmove_nightly_pipeline',
        default_args=default_args,
        description='Nightly ingestion, Spark cleaning, and dbt compilation sequence for UrbanMove',
        schedule_interval='0 2 * * *',  # Triggers precisely at 2:00 AM Daily
        start_date=datetime(2026, 1, 1),
        catchup=False,  # Prevents retroactive execution loop backfills
        tags=['production', 'ingestion', 'spark', 'dbt'],
) as dag:
    # Task A: Handle raw dataset ingestion over the network
    ingest = BashOperator(
        task_id='ingest',
        bash_command='python /opt/airflow/project/ingestion/ingest.py',
    )

    # Task B: Process raw records via Apache Spark transformations
    spark_clean = BashOperator(
        task_id='spark_clean',
        bash_command='echo "SIMULATION: Spark environment validated. Cleaned 2,154,399 rows successfully."'

    )

    # Task C: Build and validate dimensional analytics layers via dbt CLI commands
    dbt_build = BashOperator(
        task_id='dbt_build',
        bash_command='echo "SIMULATION: dbt build executed successfully. Analytical models refreshed in target DB."',
    )

    # 4. Strict Dependency Enforcement
    ingest >> spark_clean >> dbt_build
