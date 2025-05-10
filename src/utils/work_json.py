import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.utils.config import QUESTION_URL
from src.utils.logger import setup_logger

from src.utils.config import JSON_DIR


JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
logger = setup_logger(level=10)


def get_all_json_files(directory: str = JSON_DIR) -> List[str]:
    """
    Returns a list of all .json file paths in the specified directory and its subdirectories.

    :param directory: Path to the directory to search for files.
    :return: List of absolute paths to .json files.
    """

    base_path = Path(directory).resolve()
    cwd = Path.cwd()

    return [
        str(p.resolve().relative_to(cwd))
        for p in base_path.rglob('*.json')
        if p.is_file()
    ]


def read_json_file(filename: str) -> Optional[JSONType]:
    """Reads a JSON file and returns the parsed data.

    Args:
        filename (str): Path to the JSON file.

    Returns:
        Optional[JSONType]: Parsed JSON data if successful, None otherwise.
    """

    logger.debug(f"read file -> {filename}")

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: File '{filename}' not found.")
    except json.JSONDecodeError as e:
        logger.error(f"Error: Failed to decode JSON from file '{filename}': {e}")
    except PermissionError:
        logger.error(f"Error: Permission denied when accessing file '{filename}'.")
    except Exception as e:
        logger.error(f"Unexpected error reading file '{filename}': {e}")
    return None


def read_json_file_all(filename: str) -> List[Dict]:
    """Function to read file in JSON format.

    Args:
        filename (str): relative path to the file
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = []
    count = 1
    for item in data['data']:
        parsed = {
            'id': item.get('id'),
            'title': item.get('title'),
            'keywords': item.get('keywords'),
            'shortAnswer': item.get('shortAnswer'),
            # 'shortAnswer': shortAnswer,
            # 'longAnswer': item.get('longAnswer'),
            # 'longAnswer': longAnswer,
            # 'status': item.get('status'),
            # 'rate': item.get('rate'),
            # 'complexity': item.get('complexity'),
            'createdAt': item.get('createdAt'),
        }
        results.append(parsed)
        if count == 10:
            break

    for r in results:
        print(r)
        logger.debug(r)


def parse_json_pinecone(file_dir: str) -> List[Dict]:
    """
    Parse a JSON string and return the corresponding Python object.

    Args:
        file_dir (str): PAth to JSON folder to parse.

    Returns:
        Any: Python object parsed from the JSON string.

    Raises:
        json.JSONDecodeError: If the input string is not valid JSON.
    """

    json_list = get_all_json_files(file_dir)

    if not json_list:
        logger.error(f"list of FILES is empty.")
        return

    try:
        results = []
        for filename in json_list:
            data = read_json_file(filename)

            if data is None:
                logger.error(f"file {filename} is empty.")
                return

            for item in data['data']:
                parsed = {
                    '_id': str(item.get('id')),
                    'title': item.get('title'),
                    'tags': item.get('keywords'),
                    'url': QUESTION_URL.format(item.get('id')),
                }
                results.append(parsed)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed: {e}")
        raise
    return results


def parse_json_postgres_question(file_dir: str) -> List[Tuple]:
    """
    Parse a JSON string and return the corresponding Python object.
    Parse DATA for table `QUESTIONS`

    Args:
        file_dir (str): PAth to JSON folder to parse.

    Returns:
        Any: Python object parsed from the JSON string.

    Raises:
        json.JSONDecodeError: If the input string is not valid JSON.
    """

    json_list = get_all_json_files(file_dir)

    if not json_list:
        logger.error(f"list of FILES is empty.")
        return

    try:
        results = []
        for filename in json_list:
            data = read_json_file(filename)

            if data is None:
                logger.error(f"file {filename} is empty.")
                return

            for item in data['data']:
                parsed = {
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'tags': item.get('keywords'),
                    'createdAt': item.get('createdAt'),
                }
                results.append(tuple(parsed.values()))
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed: {e}")
        raise
    return results


def parse_json_postgres_answer(file_dir: str) -> List[Tuple]:
    """
    Parse a JSON string and return the corresponding Python object.
    Parse DATA for table `ANSWERS`

    Args:
        file_dir (str): PAth to JSON folder to parse.

    Returns:
        Any: Python object parsed from the JSON string.

    Raises:
        json.JSONDecodeError: If the input string is not valid JSON.
    """

    json_list = get_all_json_files(file_dir)

    if not json_list:
        logger.error(f"list of FILES is empty.")
        return

    try:
        results = []
        for filename in json_list:
            data = read_json_file(filename)

            if data is None:
                logger.error(f"file {filename} is empty.")
                return

            for item in data['data']:
                parsed = {
                    'id': item.get('id'),
                    'shortAnswer': item.get('shortAnswer'),
                    
                }
                results.append(tuple(parsed.values()))
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed: {e}")
        raise
    return results

if __name__ == '__main__':
    # print(get_all_json_files())
    # print(parse_json_postgres_question(JSON_DIR))
    # print(parse_json_postgres_answer(JSON_DIR))
    pass