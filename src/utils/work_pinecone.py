import os
from typing import Any, Dict, Generator, List, Optional

from dotenv import load_dotenv
from pinecone import Pinecone

# from src.utils.config import JSON_DIR
from src.utils.logger import setup_logger
from src.utils.work_json import parse_json_pinecone


MAX_BATCH_SIZE=50

class PineconeClient:
    """
    Wrapper class for Pinecone operations: index creation and data upsert.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        """
        Initialize Pinecone client with configuration.

        Args:
            api_key (Optional[str]): Pinecone API key.
            index_name (Optional[str]): Pinecone index name.
            namespace (Optional[str]): Pinecone namespace.
        """
        load_dotenv()

        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME")
        self.namespace = namespace or os.getenv("PINECONE_NAMESPACE")

        if not all([self.api_key, self.index_name, self.namespace]):
            raise ValueError("API-key, INDEX name, and NAMESPACE must be provided")

        self.logger = setup_logger(level=10)
        self.pc = Pinecone(api_key=self.api_key)

    def create_index(self) -> None:
        """
        Create Pinecone index if it does not exist.
        """
        if not self.pc.has_index(self.index_name):
            self.pc.create_index_for_model(
                name=self.index_name,
                cloud="aws",
                region="us-east-1",
                embed={
                    "model": "llama-text-embed-v2",
                    "field_map": {"text": "title"},
                }
            )
            self.dense_index = self.pc.Index(self.index_name)
            self.logger.debug(f"Index `{self.index_name}` created.")
        else:
            self.logger.debug(f"Index `{self.index_name}` already exists.")

    def batch_records(
            self,
            records: List[Dict[str, Any]], 
            max_batch_size: int = MAX_BATCH_SIZE,
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Divide records on batch based on max_batch_size
        """
        for i in range(0, len(records), max_batch_size):
            yield records[i:i + max_batch_size]

    def upsert_data(self, file_dir: str) -> None:
        """
        Parse JSON data and upsert into Pinecone index.

        Args:
            file_dir (str): Directory path containing JSON files.
        """
        try:
            records = parse_json_pinecone(file_dir)
            self.logger.debug(f"Parsed {len(records)} records from JSON.")

            for i, batch in enumerate(self.batch_records(records)):
                self.dense_index.upsert_records(self.namespace, batch)
                self.logger.debug(f"Upserted batch {i + 1} with {len(batch)} records.")

            self.logger.info("All data upserted into Pinecone successfully.")
        except Exception as e:
            self.logger.error(f"An error occurred during upsert: {e}")
            raise


def run_pinecone_upsert(file_dir: str) -> None:
    client = PineconeClient()
    client.create_index()
    client.upsert_data(file_dir)


if __name__ == "__main__":
    # run_pinecone_upsert(JSON_DIR)
    pass
