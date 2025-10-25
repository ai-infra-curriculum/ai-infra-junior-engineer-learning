"""
Data Preprocessing Module

This module handles cleaning and transforming raw data for model training.

Learning Objectives:
- Implement data cleaning (duplicates, missing values)
- Encode categorical variables
- Create train/validation/test splits
- Save preprocessing artifacts for reproducibility

TODO: Complete all sections marked with TODO
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
import joblib
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Handles data preprocessing for ML pipelines.

    This class provides methods to clean data, encode labels, create splits,
    and save preprocessing artifacts for reproducibility.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary
        label_encoder (LabelEncoder): Encoder for categorical labels
        scaler (StandardScaler): Scaler for numerical features
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize DataPreprocessor with configuration.

        Args:
            config: Configuration dictionary containing:
                - processed_data_path: Path to save processed data
                - artifacts_path: Path to save preprocessing artifacts
                - required_columns: List of required column names
                - test_size: Test set fraction (default: 0.2)
                - val_size: Validation set fraction (default: 0.1)
                - random_state: Random seed for reproducibility (default: 42)

        TODO:
        1. Extract configuration parameters
        2. Create output directories if they don't exist
        3. Initialize label encoder and scaler
        4. Log initialization
        """
        self.config = config

        # TODO: Extract paths from config
        self.processed_data_path = None  # Replace with Path(config.get('processed_data_path'))
        self.artifacts_path = None  # Replace with Path(config.get('artifacts_path'))

        # TODO: Create directories
        # Hint: Use .mkdir(parents=True, exist_ok=True)

        # TODO: Initialize encoders and scalers
        self.label_encoder = None  # Replace with LabelEncoder()
        self.scaler = None  # Replace with StandardScaler()

        # TODO: Extract configuration parameters with defaults
        self.required_columns = config.get('required_columns', [])
        self.test_size = 0.2  # TODO: Get from config
        self.val_size = 0.1   # TODO: Get from config
        self.random_state = 42  # TODO: Get from config

        logger.info("DataPreprocessor initialized")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean data by removing duplicates and handling missing values.

        Args:
            df: Raw DataFrame to clean

        Returns:
            Cleaned DataFrame

        TODO:
        1. Log initial data shape
        2. Remove exact duplicate rows
        3. Log number of duplicates removed
        4. Handle missing values in required columns (drop rows)
        5. Log number of rows with missing values removed
        6. Reset index
        7. Log final data shape
        8. Return cleaned DataFrame

        Cleaning Steps:
        - Remove exact duplicates (keep first occurrence)
        - Drop rows with missing values in required columns
        - Keep rows with missing values in optional columns
        - Reset index after dropping rows

        Example:
            >>> preprocessor = DataPreprocessor(config)
            >>> df_clean = preprocessor.clean_data(df_raw)
            >>> print(f"Cleaned: {len(df_raw)} -> {len(df_clean)} rows")
            Cleaned: 52000 -> 50000 rows
        """
        logger.info(f"Starting data cleaning. Initial shape: {df.shape}")

        # TODO: Store initial row count
        initial_rows = len(df)

        # TODO: Remove duplicates
        # Hint: df = df.drop_duplicates()
        # TODO: Calculate and log duplicates removed
        duplicates_removed = 0  # Replace with actual count

        logger.info(f"Removed {duplicates_removed} duplicate rows")

        # TODO: Handle missing values in required columns
        # Hint: df = df.dropna(subset=self.required_columns)
        # TODO: Calculate and log missing values removed
        missing_removed = 0  # Replace with actual count

        logger.info(f"Removed {missing_removed} rows with missing required values")

        # TODO: Reset index
        # Hint: df = df.reset_index(drop=True)

        logger.info(f"Data cleaning complete. Final shape: {df.shape}")

        return df

    def encode_labels(
        self,
        df: pd.DataFrame,
        label_column: str = 'label'
    ) -> pd.DataFrame:
        """
        Encode categorical labels to integers.

        Args:
            df: DataFrame with categorical labels
            label_column: Name of the label column

        Returns:
            DataFrame with encoded labels in new column

        TODO:
        1. Check if label_column exists
        2. Fit label encoder on unique labels
        3. Transform labels to integers
        4. Add encoded column (e.g., 'label_encoded')
        5. Save label encoder to artifacts directory
        6. Save label mapping (original -> encoded) as JSON
        7. Log encoding information
        8. Return DataFrame with new column

        The label encoder should be saved for use during inference.

        Example:
            >>> preprocessor = DataPreprocessor(config)
            >>> df = preprocessor.encode_labels(df, 'label')
            >>> print(df[['label', 'label_encoded']].head())
               label  label_encoded
            0    cat              0
            1    dog              1
            2   bird              2
        """
        logger.info(f"Encoding labels from column: {label_column}")

        # TODO: Check if column exists
        if label_column not in df.columns:
            raise ValueError(f"Column '{label_column}' not found in DataFrame")

        # TODO: Get unique labels before encoding
        unique_labels = None  # Replace with df[label_column].unique()

        # TODO: Fit and transform labels
        # Hint: encoded = self.label_encoder.fit_transform(df[label_column])

        # TODO: Add encoded column to DataFrame
        encoded_column_name = f"{label_column}_encoded"
        # df[encoded_column_name] = encoded

        # TODO: Save label encoder
        encoder_path = self.artifacts_path / 'label_encoder.pkl'
        # Hint: joblib.dump(self.label_encoder, encoder_path)

        # TODO: Create and save label mapping
        label_mapping = {}  # TODO: Create dict mapping original labels to encoded values
        # Hint: {label: encoded for label, encoded in zip(unique_labels, range(len(unique_labels)))}

        mapping_path = self.artifacts_path / 'label_mapping.json'
        # TODO: Save mapping as JSON

        logger.info(f"Encoded {len(unique_labels)} unique labels")
        logger.info(f"Saved label encoder to {encoder_path}")
        logger.info(f"Label mapping: {label_mapping}")

        return df

    def normalize_features(
        self,
        df: pd.DataFrame,
        feature_columns: List[str]
    ) -> pd.DataFrame:
        """
        Normalize numerical features using StandardScaler.

        Args:
            df: DataFrame with numerical features
            feature_columns: List of column names to normalize

        Returns:
            DataFrame with normalized features

        TODO:
        1. Validate that feature columns exist
        2. Fit scaler on feature columns
        3. Transform features
        4. Replace original columns with normalized values
        5. Save scaler to artifacts directory
        6. Log normalization statistics (mean, std)
        7. Return DataFrame

        Note: Only use this if your model requires normalized features.
        For image classification with pretrained models, this may not be needed.

        Example:
            >>> preprocessor = DataPreprocessor(config)
            >>> df = preprocessor.normalize_features(df, ['height', 'width'])
            >>> print(df[['height', 'width']].describe())
        """
        logger.info(f"Normalizing {len(feature_columns)} features")

        # TODO: Validate columns exist
        missing_cols = [col for col in feature_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found: {missing_cols}")

        # TODO: Fit and transform features
        # Hint: df[feature_columns] = self.scaler.fit_transform(df[feature_columns])

        # TODO: Save scaler
        scaler_path = self.artifacts_path / 'scaler.pkl'
        # Hint: joblib.dump(self.scaler, scaler_path)

        # TODO: Log statistics
        logger.info(f"Saved scaler to {scaler_path}")

        return df

    def create_train_test_split(
        self,
        df: pd.DataFrame,
        stratify_column: Optional[str] = 'label_encoded'
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Create train, validation, and test splits.

        Args:
            df: DataFrame to split
            stratify_column: Column to use for stratified splitting

        Returns:
            Tuple of (train_df, val_df, test_df)

        TODO:
        1. Validate stratify_column exists
        2. First split: separate test set from train+val
        3. Second split: separate train and validation sets
        4. Verify stratification worked (similar class distributions)
        5. Log split sizes and class distributions
        6. Return three DataFrames

        Splitting Strategy:
        - Use stratified splitting to preserve class balance
        - Default split: 70% train, 15% val, 15% test
        - Set random_state for reproducibility

        Example:
            >>> preprocessor = DataPreprocessor(config)
            >>> train, val, test = preprocessor.create_train_test_split(df)
            >>> print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
            Train: 35000, Val: 7500, Test: 7500
        """
        logger.info("Creating train/validation/test splits")

        # TODO: Validate stratify column
        if stratify_column and stratify_column not in df.columns:
            logger.warning(f"Stratify column '{stratify_column}' not found. Using random split.")
            stratify_column = None

        # TODO: Get stratify array if column exists
        stratify_array = None
        if stratify_column:
            stratify_array = df[stratify_column]

        # TODO: First split: train+val vs test
        # Hint: train_val, test = train_test_split(
        #     df,
        #     test_size=self.test_size,
        #     random_state=self.random_state,
        #     stratify=stratify_array
        # )

        # TODO: Calculate validation size relative to train+val
        # If total is 100%, test is 20%, then train+val is 80%
        # We want val to be 15% of total, so 15/80 = 0.1875 of train+val
        val_ratio = 0.0  # TODO: Calculate as self.val_size / (1 - self.test_size)

        # TODO: Second split: train vs val
        # Hint: train, val = train_test_split(
        #     train_val,
        #     test_size=val_ratio,
        #     random_state=self.random_state,
        #     stratify=train_val[stratify_column] if stratify_column else None
        # )

        # TODO: Log split sizes
        logger.info(f"Split sizes - Train: {0}, Val: {0}, Test: {0}")

        # TODO: Log class distributions if stratifying
        if stratify_column:
            # TODO: Calculate and log class distributions for each split
            pass

        # TODO: Return splits (uncomment when implemented)
        # return train, val, test
        return None, None, None  # Replace with actual splits

    def save_processed_data(
        self,
        train: pd.DataFrame,
        val: pd.DataFrame,
        test: pd.DataFrame
    ) -> Dict[str, Path]:
        """
        Save processed train, validation, and test sets.

        Args:
            train: Training DataFrame
            val: Validation DataFrame
            test: Test DataFrame

        Returns:
            Dictionary mapping split names to file paths

        TODO:
        1. Save each split to CSV in processed_data_path
        2. Create metadata for each split (record count, columns, etc.)
        3. Save metadata as JSON
        4. Log save locations
        5. Return paths dictionary

        Files to create:
        - train.csv, val.csv, test.csv
        - train.meta.json, val.meta.json, test.meta.json

        Example:
            >>> preprocessor = DataPreprocessor(config)
            >>> paths = preprocessor.save_processed_data(train, val, test)
            >>> print(paths['train'])
            PosixPath('data/processed/train.csv')
        """
        logger.info("Saving processed data splits")

        paths = {}

        # TODO: Save each split
        splits = {
            'train': train,
            'val': val,
            'test': test
        }

        for split_name, split_df in splits.items():
            # TODO: Create file path
            csv_path = None  # Replace with self.processed_data_path / f"{split_name}.csv"

            # TODO: Save to CSV
            # Hint: split_df.to_csv(csv_path, index=False)

            # TODO: Create metadata
            metadata = {
                # TODO: Fill in metadata
                "split": split_name,
                "record_count": 0,
                "columns": [],
                "shape": (0, 0),
                "created_at": None
            }

            # TODO: Save metadata
            meta_path = None  # Replace with path to .meta.json file

            # TODO: Add to paths dict
            # paths[split_name] = csv_path

            logger.info(f"Saved {split_name} split to {csv_path} ({len(split_df)} records)")

        return paths

    def run_pipeline(
        self,
        df: pd.DataFrame,
        label_column: str = 'label'
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Run the complete preprocessing pipeline.

        Args:
            df: Raw DataFrame
            label_column: Name of the label column

        Returns:
            Tuple of (train_df, val_df, test_df)

        TODO:
        1. Run data cleaning
        2. Run label encoding
        3. (Optional) Run feature normalization if needed
        4. Create train/val/test splits
        5. Save processed data
        6. Save preprocessing configuration
        7. Return splits

        This is the main entry point that runs all preprocessing steps.

        Example:
            >>> preprocessor = DataPreprocessor(config)
            >>> train, val, test = preprocessor.run_pipeline(raw_df)
            >>> print("Preprocessing complete!")
        """
        logger.info("Running complete preprocessing pipeline")

        # TODO: Step 1 - Clean data
        logger.info("Step 1/4: Cleaning data...")
        # df_clean = self.clean_data(df)

        # TODO: Step 2 - Encode labels
        logger.info("Step 2/4: Encoding labels...")
        # df_encoded = self.encode_labels(df_clean, label_column)

        # TODO: Step 3 - Create splits
        logger.info("Step 3/4: Creating train/val/test splits...")
        # train, val, test = self.create_train_test_split(df_encoded)

        # TODO: Step 4 - Save processed data
        logger.info("Step 4/4: Saving processed data...")
        # paths = self.save_processed_data(train, val, test)

        # TODO: Save preprocessing configuration
        self._save_preprocessing_config()

        logger.info("Preprocessing pipeline complete!")

        # TODO: Return splits (uncomment when implemented)
        # return train, val, test
        return None, None, None  # Replace with actual splits

    def _save_preprocessing_config(self) -> None:
        """
        Save preprocessing configuration for reproducibility.

        TODO:
        1. Create config dictionary with all preprocessing settings
        2. Save to JSON file in artifacts directory
        3. Log save location

        Config should include:
        - required_columns
        - test_size, val_size
        - random_state
        - label_column
        - feature_columns (if normalization used)
        """
        config_to_save = {
            # TODO: Fill in configuration
            "test_size": self.test_size,
            "val_size": self.val_size,
            "random_state": self.random_state,
            "required_columns": self.required_columns
        }

        config_path = self.artifacts_path / 'preprocessing_config.json'

        # TODO: Save configuration
        # Hint: with open(config_path, 'w') as f:
        #           json.dump(config_to_save, f, indent=2)

        logger.info(f"Saved preprocessing config to {config_path}")

    def load_preprocessing_artifacts(self) -> None:
        """
        Load previously saved preprocessing artifacts.

        TODO:
        1. Load label encoder from pickle
        2. Load scaler from pickle (if exists)
        3. Load preprocessing config from JSON
        4. Log loaded artifacts
        5. Set instance attributes

        Use this when you need to preprocess new data using the same
        transformations as the training data.

        Example:
            >>> preprocessor = DataPreprocessor(config)
            >>> preprocessor.load_preprocessing_artifacts()
            >>> # Now can use loaded encoder/scaler on new data
        """
        logger.info("Loading preprocessing artifacts")

        # TODO: Load label encoder
        encoder_path = self.artifacts_path / 'label_encoder.pkl'
        if encoder_path.exists():
            # self.label_encoder = joblib.load(encoder_path)
            logger.info(f"Loaded label encoder from {encoder_path}")

        # TODO: Load scaler if exists
        scaler_path = self.artifacts_path / 'scaler.pkl'
        if scaler_path.exists():
            # self.scaler = joblib.load(scaler_path)
            logger.info(f"Loaded scaler from {scaler_path}")

        # TODO: Load config
        config_path = self.artifacts_path / 'preprocessing_config.json'
        if config_path.exists():
            # with open(config_path, 'r') as f:
            #     config = json.load(f)
            logger.info(f"Loaded preprocessing config from {config_path}")


# Example usage and testing
if __name__ == "__main__":
    """
    Example usage of DataPreprocessor class.

    TODO:
    1. Create sample configuration
    2. Create sample DataFrame
    3. Initialize DataPreprocessor
    4. Run preprocessing pipeline
    5. Verify outputs

    Create a sample dataset with:
    - image_path column
    - label column (categorical)
    - Some duplicate rows
    - Some missing values
    """

    # Sample configuration
    config = {
        'processed_data_path': 'data/processed',
        'artifacts_path': 'artifacts',
        'required_columns': ['image_path', 'label'],
        'test_size': 0.2,
        'val_size': 0.1,
        'random_state': 42
    }

    # TODO: Create sample DataFrame for testing
    # Example:
    # sample_data = {
    #     'image_path': ['img1.jpg', 'img2.jpg', ...],
    #     'label': ['cat', 'dog', 'cat', ...],
    #     'extra_col': [1, 2, 3, ...]
    # }
    # df = pd.DataFrame(sample_data)

    # TODO: Initialize preprocessor
    # preprocessor = DataPreprocessor(config)

    # TODO: Run pipeline
    # train, val, test = preprocessor.run_pipeline(df)

    # TODO: Verify outputs
    # print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

    print("DataPreprocessor module loaded. Implement the TODOs to complete functionality.")
