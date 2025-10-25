"""
Model Evaluation Module

This module handles comprehensive model evaluation with metrics computation
and visualization.

Learning Objectives:
- Compute multiple evaluation metrics
- Generate confusion matrices
- Create classification reports
- Visualize model performance
- Log results to MLflow

TODO: Complete all sections marked with TODO
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Tuple
import logging
from pathlib import Path
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluates models on test set with comprehensive metrics.

    This class computes multiple metrics, generates visualizations,
    and logs everything to MLflow for tracking.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary
        device (torch.device): Device for inference (CPU/GPU)
        class_names (List[str]): List of class names
    """

    def __init__(
        self,
        config: Dict[str, Any],
        class_names: List[str]
    ) -> None:
        """
        Initialize ModelEvaluator.

        Args:
            config: Configuration dictionary
            class_names: List of class names for visualization

        TODO:
        1. Store configuration
        2. Determine device (GPU if available)
        3. Store class names
        4. Create output directory for plots
        5. Log initialization
        """
        self.config = config
        self.class_names = class_names

        # TODO: Set device
        # Hint: self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = None

        # TODO: Create plots directory
        self.plots_dir = Path(config.get('plots_dir', 'plots'))
        # self.plots_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"ModelEvaluator initialized with {len(class_names)} classes")

    def predict(
        self,
        model: nn.Module,
        test_loader: DataLoader
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate predictions on test set.

        Args:
            model: Trained PyTorch model
            test_loader: Test data loader

        Returns:
            Tuple of (true_labels, predicted_labels) as numpy arrays

        TODO:
        1. Set model to evaluation mode
        2. Move model to device
        3. Iterate through test data
        4. Generate predictions (no gradients needed)
        5. Collect true and predicted labels
        6. Convert to numpy arrays
        7. Return both arrays
        """
        logger.info("Generating predictions on test set...")

        # TODO: Set model to eval mode and move to device
        # model.eval()
        # model = model.to(self.device)

        y_true = []
        y_pred = []

        # TODO: Disable gradient computation
        # with torch.no_grad():
        for inputs, targets in test_loader:
            # TODO: Move data to device
            # inputs, targets = inputs.to(self.device), targets.to(self.device)

            # TODO: Forward pass
            # outputs = model(inputs)

            # TODO: Get predictions
            # _, predicted = outputs.max(1)

            # TODO: Collect labels
            # y_true.extend(targets.cpu().numpy())
            # y_pred.extend(predicted.cpu().numpy())
            pass

        # TODO: Convert to numpy arrays
        y_true = np.array(y_true) if y_true else np.array([])
        y_pred = np.array(y_pred) if y_pred else np.array([])

        logger.info(f"Generated predictions for {len(y_true)} samples")

        return y_true, y_pred

    def compute_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Compute comprehensive evaluation metrics.

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Dictionary of metric name -> value

        TODO:
        1. Compute overall accuracy
        2. Compute macro-averaged precision, recall, F1
        3. Compute per-class precision, recall, F1
        4. Organize into dictionary
        5. Log metrics summary
        6. Return metrics dictionary

        Metrics to compute:
        - test_accuracy
        - test_precision (macro)
        - test_recall (macro)
        - test_f1 (macro)
        - per_class_precision (list)
        - per_class_recall (list)
        - per_class_f1 (list)
        """
        logger.info("Computing evaluation metrics...")

        metrics = {}

        # TODO: Compute overall metrics
        # metrics['test_accuracy'] = accuracy_score(y_true, y_pred)
        # metrics['test_precision'] = precision_score(y_true, y_pred, average='macro')
        # metrics['test_recall'] = recall_score(y_true, y_pred, average='macro')
        # metrics['test_f1'] = f1_score(y_true, y_pred, average='macro')

        # TODO: Compute per-class metrics
        # per_class_precision = precision_score(y_true, y_pred, average=None)
        # per_class_recall = recall_score(y_true, y_pred, average=None)
        # per_class_f1 = f1_score(y_true, y_pred, average=None)

        # TODO: Store per-class metrics
        # for i, class_name in enumerate(self.class_names):
        #     metrics[f'{class_name}_precision'] = per_class_precision[i]
        #     metrics[f'{class_name}_recall'] = per_class_recall[i]
        #     metrics[f'{class_name}_f1'] = per_class_f1[i]

        # TODO: Log summary
        logger.info(f"Test Accuracy: {metrics.get('test_accuracy', 0):.4f}")
        logger.info(f"Test F1 Score: {metrics.get('test_f1', 0):.4f}")

        return metrics

    def generate_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> np.ndarray:
        """
        Generate confusion matrix.

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Confusion matrix as numpy array

        TODO:
        1. Compute confusion matrix
        2. Log matrix dimensions
        3. Return matrix
        """
        logger.info("Generating confusion matrix...")

        # TODO: Compute confusion matrix
        # cm = confusion_matrix(y_true, y_pred)

        # TODO: Log
        # logger.info(f"Confusion matrix shape: {cm.shape}")

        return None  # Replace with cm

    def plot_confusion_matrix(
        self,
        cm: np.ndarray,
        save_path: Optional[Path] = None
    ) -> Path:
        """
        Plot confusion matrix as heatmap.

        Args:
            cm: Confusion matrix
            save_path: Optional path to save plot

        Returns:
            Path to saved plot

        TODO:
        1. Create figure
        2. Plot heatmap with seaborn
        3. Add labels, title, colorbar
        4. Save figure
        5. Close figure
        6. Return path
        """
        logger.info("Plotting confusion matrix...")

        # TODO: Create figure
        # plt.figure(figsize=(10, 8))

        # TODO: Create heatmap
        # sns.heatmap(
        #     cm,
        #     annot=True,
        #     fmt='d',
        #     cmap='Blues',
        #     xticklabels=self.class_names,
        #     yticklabels=self.class_names
        # )

        # TODO: Add labels
        # plt.title('Confusion Matrix')
        # plt.ylabel('True Label')
        # plt.xlabel('Predicted Label')

        # TODO: Save figure
        if save_path is None:
            save_path = self.plots_dir / 'confusion_matrix.png'

        # plt.tight_layout()
        # plt.savefig(save_path, dpi=300, bbox_inches='tight')
        # plt.close()

        logger.info(f"Saved confusion matrix plot to {save_path}")

        return save_path

    def generate_classification_report(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        save_path: Optional[Path] = None
    ) -> str:
        """
        Generate detailed classification report.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            save_path: Optional path to save report

        Returns:
            Classification report as string

        TODO:
        1. Generate classification report with sklearn
        2. Save to file if path provided
        3. Log report
        4. Return report string
        """
        logger.info("Generating classification report...")

        # TODO: Generate report
        # report = classification_report(
        #     y_true,
        #     y_pred,
        #     target_names=self.class_names,
        #     digits=4
        # )

        # TODO: Save to file
        # if save_path:
        #     save_path = Path(save_path)
        #     save_path.parent.mkdir(parents=True, exist_ok=True)
        #     with open(save_path, 'w') as f:
        #         f.write(report)

        # TODO: Log report
        # logger.info(f"\nClassification Report:\n{report}")

        return ""  # Replace with report

    def save_metrics(
        self,
        metrics: Dict[str, float],
        save_path: Path
    ) -> None:
        """
        Save metrics to JSON file.

        Args:
            metrics: Dictionary of metrics
            save_path: Path to save JSON file

        TODO:
        1. Create parent directories
        2. Save metrics as JSON
        3. Log save location
        """
        logger.info("Saving metrics to file...")

        # TODO: Create directories
        # save_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: Save as JSON
        # with open(save_path, 'w') as f:
        #     json.dump(metrics, f, indent=2)

        logger.info(f"Saved metrics to {save_path}")

    def evaluate(
        self,
        model: nn.Module,
        test_loader: DataLoader,
        mlflow_tracker: Optional[Any] = None
    ) -> Dict[str, float]:
        """
        Run complete evaluation pipeline.

        Args:
            model: Trained model to evaluate
            test_loader: Test data loader
            mlflow_tracker: Optional MLflow tracker for logging

        Returns:
            Dictionary of all computed metrics

        TODO:
        1. Generate predictions
        2. Compute metrics
        3. Generate confusion matrix
        4. Plot confusion matrix
        5. Generate classification report
        6. Save all artifacts
        7. Log to MLflow if tracker provided
        8. Return metrics

        This is the main entry point that runs all evaluation steps.
        """
        logger.info("Starting comprehensive model evaluation...")

        # TODO: Step 1 - Generate predictions
        # y_true, y_pred = self.predict(model, test_loader)

        # TODO: Step 2 - Compute metrics
        # metrics = self.compute_metrics(y_true, y_pred)

        # TODO: Step 3 - Generate confusion matrix
        # cm = self.generate_confusion_matrix(y_true, y_pred)

        # TODO: Step 4 - Plot confusion matrix
        # cm_plot_path = self.plot_confusion_matrix(cm)

        # TODO: Step 5 - Generate classification report
        # report_path = self.plots_dir / 'classification_report.txt'
        # report = self.generate_classification_report(y_true, y_pred, report_path)

        # TODO: Step 6 - Save metrics
        # metrics_path = self.plots_dir / 'test_metrics.json'
        # self.save_metrics(metrics, metrics_path)

        # TODO: Step 7 - Log to MLflow if available
        # if mlflow_tracker:
        #     mlflow_tracker.log_metrics(metrics)
        #     mlflow_tracker.log_artifact(str(cm_plot_path))
        #     mlflow_tracker.log_artifact(str(report_path))
        #     mlflow_tracker.log_artifact(str(metrics_path))

        logger.info("Evaluation complete!")

        return {}  # Replace with metrics


# Example usage
if __name__ == "__main__":
    """
    Example usage of ModelEvaluator.

    TODO:
    1. Load a trained model
    2. Create test data loader
    3. Initialize evaluator
    4. Run evaluation
    5. View results
    """

    # Configuration
    config = {
        'plots_dir': 'evaluation_plots'
    }

    # Class names for the dataset
    class_names = ['cat', 'dog', 'bird', 'fish']

    # TODO: Initialize evaluator
    # evaluator = ModelEvaluator(config, class_names)

    # TODO: Load model (placeholder)
    # model = torch.load('path/to/model.pth')

    # TODO: Create test loader (placeholder)
    # test_loader = ...

    # TODO: Run evaluation
    # metrics = evaluator.evaluate(model, test_loader)

    # TODO: Print results
    # print("\nEvaluation Metrics:")
    # for key, value in metrics.items():
    #     print(f"{key}: {value:.4f}")

    print("ModelEvaluator module loaded. Implement the TODOs to complete functionality.")
