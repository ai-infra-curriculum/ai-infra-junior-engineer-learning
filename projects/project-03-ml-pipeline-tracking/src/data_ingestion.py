"""
Data Ingestion Module

This module handles ingesting data from multiple sources (CSV, APIs, databases)
and saving raw data to the pipeline.

Learning Objectives:
- Implement multi-source data ingestion
- Handle different data formats
- Implement error handling and retries
- Log ingestion metadata

TODO: Complete all sections marked with TODO
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataIngestion:
    """
    Handles data ingestion from multiple sources.

    This class provides methods to load data from CSV files, REST APIs,
    and databases, with proper error handling and logging.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary
        raw_data_path (Path): Path to raw data directory
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize DataIngestion with configuration.

        Args:
            config: Configuration dictionary containing:
                - raw_data_path: Path to store raw data
                - retry_attempts: Number of retry attempts for API calls
                - retry_delay: Delay between retries in seconds

        TODO:
        1. Extract configuration parameters
        2. Create raw_data_path directory if it doesn't exist
        3. Initialize retry settings (default: 3 attempts, 5 second delay)
        4. Log initialization
        """
        self.config = config
        # TODO: Extract raw_data_path from config
        self.raw_data_path = None  # Replace with actual path

        # TODO: Create directory if it doesn't exist
        # Hint: Use Path.mkdir(parents=True, exist_ok=True)

        # TODO: Initialize retry settings from config or use defaults
        self.retry_attempts = 3
        self.retry_delay = 5

        # TODO: Log successful initialization
        logger.info("DataIngestion initialized")

    def ingest_from_csv(self, file_path: str) -> pd.DataFrame:
        """
        Ingest data from a CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            DataFrame containing the loaded data

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            pd.errors.ParserError: If the CSV file is malformed

        TODO:
        1. Log the ingestion attempt with file path
        2. Attempt to read CSV file using pandas
        3. Handle potential errors (FileNotFoundError, ParserError)
        4. Log success with record count
        5. Return the DataFrame

        Example:
            >>> ingestion = DataIngestion(config)
            >>> df = ingestion.ingest_from_csv('data/raw/dataset.csv')
            >>> print(len(df))
            50000
        """
        logger.info(f"Attempting to ingest data from CSV: {file_path}")

        try:
            # TODO: Read CSV file using pd.read_csv()
            df = None  # Replace with actual code

            # TODO: Log success with record count
            # Hint: logger.info(f"Successfully loaded {len(df)} records from CSV")

            return df

        except FileNotFoundError as e:
            # TODO: Log error and re-raise
            logger.error(f"CSV file not found: {file_path}")
            raise

        except pd.errors.ParserError as e:
            # TODO: Log error and re-raise
            logger.error(f"Failed to parse CSV file: {file_path}")
            raise

        except Exception as e:
            # TODO: Log unexpected error and re-raise
            logger.error(f"Unexpected error ingesting CSV: {str(e)}")
            raise

    def ingest_from_api(
        self,
        api_url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Ingest data from a REST API with retry logic.

        Args:
            api_url: URL of the API endpoint
            params: Optional query parameters
            headers: Optional HTTP headers

        Returns:
            DataFrame containing the API response data

        Raises:
            requests.exceptions.RequestException: If all retry attempts fail
            ValueError: If response is not valid JSON

        TODO:
        1. Implement retry logic (max retry_attempts)
        2. Make GET request to API
        3. Handle HTTP errors (4xx, 5xx)
        4. Parse JSON response
        5. Convert to DataFrame
        6. Return the DataFrame

        Retry Logic:
        - Retry on network errors and 5xx server errors
        - Don't retry on 4xx client errors
        - Use exponential backoff (delay * attempt_number)

        Example:
            >>> ingestion = DataIngestion(config)
            >>> df = ingestion.ingest_from_api('https://api.example.com/data')
            >>> print(df.columns)
            Index(['id', 'name', 'value'], dtype='object')
        """
        logger.info(f"Attempting to ingest data from API: {api_url}")

        # TODO: Implement retry loop
        for attempt in range(self.retry_attempts):
            try:
                # TODO: Make GET request
                # Hint: response = requests.get(api_url, params=params, headers=headers, timeout=30)

                # TODO: Raise exception for HTTP errors
                # Hint: response.raise_for_status()

                # TODO: Parse JSON response
                # Hint: data = response.json()

                # TODO: Convert to DataFrame
                # Hint: df = pd.DataFrame(data)

                # TODO: Log success
                # logger.info(f"Successfully fetched {len(df)} records from API")

                # TODO: Return DataFrame
                return None  # Replace with actual DataFrame

            except requests.exceptions.HTTPError as e:
                # TODO: Check if error is 4xx (client error) - don't retry
                # Hint: if 400 <= e.response.status_code < 500:

                # TODO: For 5xx errors, retry with backoff
                logger.warning(f"API request failed (attempt {attempt + 1}/{self.retry_attempts}): {e}")

                if attempt < self.retry_attempts - 1:
                    # TODO: Calculate backoff delay
                    backoff_delay = self.retry_delay * (attempt + 1)
                    logger.info(f"Retrying in {backoff_delay} seconds...")
                    time.sleep(backoff_delay)
                else:
                    # TODO: Log final failure and re-raise
                    logger.error(f"All retry attempts failed for API: {api_url}")
                    raise

            except requests.exceptions.RequestException as e:
                # TODO: Handle network errors with retry
                logger.warning(f"Network error (attempt {attempt + 1}/{self.retry_attempts}): {e}")

                if attempt < self.retry_attempts - 1:
                    backoff_delay = self.retry_delay * (attempt + 1)
                    time.sleep(backoff_delay)
                else:
                    logger.error(f"All retry attempts failed for API: {api_url}")
                    raise

            except ValueError as e:
                # TODO: Handle JSON parsing errors
                logger.error(f"Failed to parse API response as JSON: {e}")
                raise

    def ingest_from_database(
        self,
        connection_string: str,
        query: str
    ) -> pd.DataFrame:
        """
        Ingest data from a database using SQL query.

        Args:
            connection_string: Database connection string
                Format: 'postgresql://user:password@host:port/database'
            query: SQL query to execute

        Returns:
            DataFrame containing query results

        Raises:
            sqlalchemy.exc.OperationalError: If connection fails
            sqlalchemy.exc.ProgrammingError: If query is invalid

        TODO:
        1. Log the ingestion attempt (sanitize connection string!)
        2. Execute SQL query using pandas
        3. Handle connection errors
        4. Handle query errors
        5. Log success with record count
        6. Return DataFrame

        Security Note:
        - Never log passwords or sensitive credentials
        - Sanitize connection string before logging

        Example:
            >>> ingestion = DataIngestion(config)
            >>> conn_str = 'postgresql://user:pass@localhost:5432/mydb'
            >>> query = 'SELECT * FROM images WHERE split = "train"'
            >>> df = ingestion.ingest_from_database(conn_str, query)
            >>> print(len(df))
            35000
        """
        # TODO: Sanitize connection string for logging
        # Hint: Replace password with '***' before logging
        sanitized_conn = self._sanitize_connection_string(connection_string)
        logger.info(f"Attempting to ingest data from database: {sanitized_conn}")

        try:
            # TODO: Execute query using pd.read_sql()
            # Hint: df = pd.read_sql(query, connection_string)
            df = None  # Replace with actual code

            # TODO: Log success with record count
            logger.info(f"Successfully queried {len(df)} records from database")

            return df

        except Exception as e:
            # TODO: Log error with sanitized connection string
            logger.error(f"Failed to query database {sanitized_conn}: {str(e)}")
            raise

    def save_raw_data(
        self,
        df: pd.DataFrame,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save raw data to disk with metadata.

        Args:
            df: DataFrame to save
            filename: Name of the file (e.g., 'dataset.csv')
            metadata: Optional metadata to save alongside data

        Returns:
            Path to the saved file

        TODO:
        1. Create full output path (raw_data_path / filename)
        2. Save DataFrame to CSV
        3. Create metadata dictionary if not provided
        4. Save metadata as JSON (same name with .meta.json extension)
        5. Log success
        6. Return Path object

        Metadata should include:
        - filename
        - record_count
        - column_count
        - columns (list)
        - saved_at (timestamp)
        - file_size (bytes)

        Example:
            >>> ingestion = DataIngestion(config)
            >>> df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
            >>> path = ingestion.save_raw_data(df, 'test.csv')
            >>> print(path.exists())
            True
        """
        # TODO: Create full output path
        output_path = None  # Replace with: self.raw_data_path / filename

        # TODO: Save DataFrame to CSV
        # Hint: df.to_csv(output_path, index=False)

        # TODO: Create metadata if not provided
        if metadata is None:
            metadata = {
                # TODO: Fill in metadata fields
                "filename": filename,
                "record_count": 0,  # Replace with len(df)
                "column_count": 0,  # Replace with len(df.columns)
                "columns": [],  # Replace with list(df.columns)
                "saved_at": None,  # Replace with datetime.now().isoformat()
                "file_size_bytes": 0  # Replace with output_path.stat().st_size
            }

        # TODO: Save metadata as JSON
        # Hint: Use json.dump() or write to .meta.json file

        # TODO: Log success
        logger.info(f"Saved raw data to {output_path} ({len(df)} records)")

        return output_path

    def get_ingestion_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Retrieve metadata for a previously saved raw data file.

        Args:
            file_path: Path to the raw data file

        Returns:
            Dictionary containing metadata

        TODO:
        1. Construct metadata file path (.meta.json)
        2. Load and parse JSON metadata
        3. Return metadata dictionary
        4. Handle case where metadata file doesn't exist

        Example:
            >>> ingestion = DataIngestion(config)
            >>> metadata = ingestion.get_ingestion_metadata(Path('data/raw/dataset.csv'))
            >>> print(metadata['record_count'])
            50000
        """
        # TODO: Construct metadata file path
        metadata_path = None  # Replace with actual path

        # TODO: Load and return metadata
        # Hint: Use json.load()

        return {}  # Replace with actual metadata

    def _sanitize_connection_string(self, conn_str: str) -> str:
        """
        Sanitize database connection string for safe logging.

        Args:
            conn_str: Database connection string

        Returns:
            Sanitized connection string with password replaced

        TODO:
        1. Use regex to find password in connection string
        2. Replace password with '***'
        3. Return sanitized string

        Example:
            >>> conn = 'postgresql://user:password@localhost:5432/db'
            >>> sanitized = self._sanitize_connection_string(conn)
            >>> print(sanitized)
            'postgresql://user:***@localhost:5432/db'
        """
        import re

        # TODO: Implement sanitization
        # Hint: Use regex pattern to match password
        # Pattern: r':([^@]+)@' captures the password between ':' and '@'

        return conn_str  # Replace with sanitized string


# Example usage and testing
if __name__ == "__main__":
    """
    Example usage of DataIngestion class.

    TODO:
    1. Create a sample configuration
    2. Initialize DataIngestion
    3. Test CSV ingestion
    4. Test API ingestion (use a public API)
    5. Test save_raw_data

    Try these public APIs for testing:
    - JSONPlaceholder: https://jsonplaceholder.typicode.com/users
    - Open Brewery DB: https://api.openbrewerydb.org/breweries
    - REST Countries: https://restcountries.com/v3.1/all
    """

    # Sample configuration
    config = {
        'raw_data_path': 'data/raw',
        'retry_attempts': 3,
        'retry_delay': 5
    }

    # TODO: Initialize DataIngestion
    # ingestion = DataIngestion(config)

    # TODO: Test CSV ingestion
    # Create a sample CSV file first for testing

    # TODO: Test API ingestion
    # Example: df = ingestion.ingest_from_api('https://jsonplaceholder.typicode.com/users')

    # TODO: Test save_raw_data
    # Example: path = ingestion.save_raw_data(df, 'api_data.csv')

    print("DataIngestion module loaded. Implement the TODOs to complete functionality.")
