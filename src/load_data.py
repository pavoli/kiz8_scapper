from src.utils.work_pg import insert_many_rows
from src.utils.work_json import (
    parse_json_postgres_question,
    parse_json_postgres_answer,
)


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

for table_name, columns in table_list.items():

    insert_many_rows(
        table_name=table_name,
        columns=columns[0],
        rows=columns[1](filename='data/json/response.json')
    )