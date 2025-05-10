from datetime import datetime, timedelta
from textwrap import dedent

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.python import PythonOperator

from src.utils.config import JSON_DIR
from src.extract_data import parse_yeahub
from src.utils.work_json import (
    parse_json_postgres_question,
    parse_json_postgres_answer,
)
from src.utils.work_pg import init_db, insert_many_rows
from src.utils.work_pinecone import run_pinecone_upsert


DAG_NAME = "process_YeaHub"
DESCRIPTION = "Parse site `YeaHub`, save data into *.html, *.json, then into PostgreSQL & Pinecone"

ARGS = {
    "owner": "pavel.olifer",
    "start_date": datetime(2025, 5, 8),
    "retries": 3,
    "retry_delay": timedelta(minutes=15),
}

table_list = {
    'questions': [
        ['id', 'title', 'created_at'],
        parse_json_postgres_question
    ],
    'answers': [
        ['question_id', 'body_md'],
        parse_json_postgres_answer
    ],
}

with DAG(
    dag_id=DAG_NAME,
    description=DESCRIPTION,
    default_args=ARGS,
    schedule_interval='0 10 * * 1-5',
    catchup=False,
    max_active_runs=1,
    tags=['YeaHub', 'Pinecone', 'PostgreSQL'],
) as dag:
    
    create_db = PythonOperator(
        task_id='create_db',
        python_callable=init_db,
    )

    parse_html_and_save_data = PythonOperator(
        task_id='parse_html_and_save_data',
        python_callable=parse_yeahub,
    )

    parse_json_and_save_Postgres = []
    for table_name, (columns, row_func) in table_list.items():
        rows = row_func(file_dir=JSON_DIR)
        task = PythonOperator(
            task_id=f'parse_json_and_save_PG_{table_name}',
            python_callable=insert_many_rows,
            op_kwargs={
                'table_name': table_name,
                'columns': columns,
                'rows': rows,
            },
        )
        parse_json_and_save_Postgres.append(task)
    
    parse_json_and_save_Pinecone = PythonOperator(
        task_id='parse_json_and_save_Pinecone',
        python_callable=run_pinecone_upsert,
        op_kwargs={
            'file_dir': JSON_DIR,
        },
    )

    chain(
        create_db,
        parse_html_and_save_data,
        *parse_json_and_save_Postgres,
        parse_json_and_save_Pinecone,
    )

    dag.doc_md = dedent(f"""
        ### DAG: {dag.dag_id}
        ---

        Developer: {dag.owner}\n
        Date: {dag.start_date}\n
        Schedule: {dag.timetable.description}\n

        ---
        ### Parse website `YeaHub`\n

        1. Create DB in Postgres
        2. Parse HTML-pages
        3. Store (questions + answers) in HTML
        3. Parse JSON
           - Store in Postgres
           - Store in Pinecone
    """)