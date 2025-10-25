"""
Model Training Module with MLflow Tracking

This module handles model training with comprehensive MLflow experiment tracking.

Learning Objectives:
- Implement PyTorch training loops
- Integrate MLflow for experiment tracking
- Log parameters, metrics, and artifacts
- Save and version models
- Implement early stopping

TODO: Complete all sections marked with TODO
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torchvision.models as models
import torchvision.transforms as transforms
from typing import Dict, Any, Tuple, Optional
import logging
from pathlib import Path
import time
import mlflow
import mlflow.pytorch
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLflowTracker:
    """
    Wrapper for MLflow tracking operations.

    This class provides a clean interface for all MLflow operations,
    making it easy to track experiments, log metrics, and register models.

    Attributes:
        tracking_uri (str): MLflow tracking server URI
        experiment_name (str): Name of the MLflow experiment
    """

    def __init__(self, tracking_uri: str, experiment_name: str) -> None:
        """
        Initialize MLflow tracker.

        Args:
            tracking_uri: URL of MLflow tracking server (e.g., 'http://localhost:5000')
            experiment_name: Name of the experiment

        TODO:
        1. Set MLflow tracking URI
        2. Set or create experiment
        3. Store experiment name
        4. Log initialization
        """
        # TODO: Set tracking URI
        # Hint: mlflow.set_tracking_uri(tracking_uri)

        # TODO: Set experiment (creates if doesn't exist)
        # Hint: mlflow.set_experiment(experiment_name)

        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri

        logger.info(f"Initialized MLflow tracker for experiment: {experiment_name}")

    def start_run(
        self,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> mlflow.ActiveRun:
        """
        Start an MLflow run.

        Args:
            run_name: Optional name for the run
            tags: Optional tags to attach to the run

        Returns:
            Active MLflow run object

        TODO:
        1. Start MLflow run with optional name and tags
        2. Log run start
        3. Return run object
        """
        # TODO: Start run
        # Hint: run = mlflow.start_run(run_name=run_name, tags=tags)

        # TODO: Log run ID
        # logger.info(f"Started MLflow run: {run.info.run_id}")

        # TODO: Return run
        return None  # Replace with actual run

    def log_params(self, params: Dict[str, Any]) -> None:
        """
        Log parameters to MLflow.

        Args:
            params: Dictionary of parameter name -> value pairs

        TODO:
        1. Log all parameters using mlflow.log_params()
        2. Log number of parameters logged
        """
        # TODO: Log parameters
        # Hint: mlflow.log_params(params)

        logger.info(f"Logged {len(params)} parameters to MLflow")

    def log_metrics(
        self,
        metrics: Dict[str, float],
        step: Optional[int] = None
    ) -> None:
        """
        Log metrics to MLflow.

        Args:
            metrics: Dictionary of metric name -> value pairs
            step: Optional step number (e.g., epoch number)

        TODO:
        1. Log all metrics using mlflow.log_metrics()
        2. Include step if provided
        """
        # TODO: Log metrics
        # Hint: mlflow.log_metrics(metrics, step=step)

        # Optional: Log individual metric log message
        if step is not None:
            logger.debug(f"Logged metrics at step {step}: {metrics}")

    def log_artifact(self, artifact_path: str) -> None:
        """
        Log an artifact file to MLflow.

        Args:
            artifact_path: Path to the artifact file

        TODO:
        1. Log artifact using mlflow.log_artifact()
        2. Log the artifact path
        """
        # TODO: Log artifact
        # Hint: mlflow.log_artifact(artifact_path)

        logger.info(f"Logged artifact: {artifact_path}")

    def log_model(
        self,
        model: nn.Module,
        artifact_path: str,
        **kwargs
    ) -> None:
        """
        Log a PyTorch model to MLflow.

        Args:
            model: PyTorch model to log
            artifact_path: Path within run to save model
            **kwargs: Additional arguments for mlflow.pytorch.log_model()

        TODO:
        1. Log model using mlflow.pytorch.log_model()
        2. Log success message
        """
        # TODO: Log model
        # Hint: mlflow.pytorch.log_model(model, artifact_path, **kwargs)

        logger.info(f"Logged model to {artifact_path}")

    def end_run(self) -> None:
        """
        End the current MLflow run.

        TODO:
        1. End MLflow run
        2. Log end message
        """
        # TODO: End run
        # Hint: mlflow.end_run()

        logger.info("Ended MLflow run")


class ModelTrainer:
    """
    Train image classification models with MLflow tracking.

    This class handles the complete training loop with validation,
    early stopping, and comprehensive MLflow logging.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary
        tracker (MLflowTracker): MLflow tracker instance
        device (torch.device): Device for training (CPU/GPU)
    """

    def __init__(
        self,
        config: Dict[str, Any],
        mlflow_tracker: MLflowTracker
    ) -> None:
        """
        Initialize ModelTrainer.

        Args:
            config: Configuration dictionary
            mlflow_tracker: Initialized MLflowTracker instance

        TODO:
        1. Store config and tracker
        2. Determine device (GPU if available, else CPU)
        3. Log device information
        """
        self.config = config
        self.tracker = mlflow_tracker

        # TODO: Set device
        # Hint: self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = None

        logger.info(f"ModelTrainer initialized. Using device: {self.device}")

    def create_model(
        self,
        num_classes: int,
        model_name: str = "resnet18"
    ) -> nn.Module:
        """
        Create a model architecture.

        Args:
            num_classes: Number of output classes
            model_name: Model architecture name ('resnet18', 'mobilenet_v2')

        Returns:
            PyTorch model

        TODO:
        1. Create model based on model_name
        2. Modify final layer for num_classes
        3. Move model to device
        4. Log model architecture
        5. Return model

        Supported models:
        - resnet18: Good baseline, 11M parameters
        - mobilenet_v2: Lightweight, 3.5M parameters
        """
        logger.info(f"Creating {model_name} model with {num_classes} classes")

        # TODO: Create model based on name
        if model_name == "resnet18":
            # TODO: Load pretrained ResNet18
            # Hint: model = models.resnet18(pretrained=True)
            # TODO: Get number of input features to final layer
            # Hint: num_features = model.fc.in_features
            # TODO: Replace final layer
            # Hint: model.fc = nn.Linear(num_features, num_classes)
            pass

        elif model_name == "mobilenet_v2":
            # TODO: Load pretrained MobileNetV2
            # Hint: model = models.mobilenet_v2(pretrained=True)
            # TODO: Get number of input features
            # Hint: num_features = model.classifier[1].in_features
            # TODO: Replace final layer
            # Hint: model.classifier[1] = nn.Linear(num_features, num_classes)
            pass

        else:
            raise ValueError(f"Unknown model: {model_name}")

        # TODO: Move model to device
        # Hint: model = model.to(self.device)

        # TODO: Log model info
        # total_params = sum(p.numel() for p in model.parameters())
        # logger.info(f"Created {model_name} with {total_params:,} parameters")

        return None  # Replace with actual model

    def train_epoch(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        criterion: nn.Module,
        optimizer: torch.optim.Optimizer
    ) -> Tuple[float, float]:
        """
        Train for one epoch.

        Args:
            model: PyTorch model
            train_loader: Training data loader
            criterion: Loss function
            optimizer: Optimizer

        Returns:
            Tuple of (average_loss, accuracy)

        TODO:
        1. Set model to training mode
        2. Initialize metrics (loss, correct predictions)
        3. Iterate through batches
        4. For each batch:
           - Move data to device
           - Forward pass
           - Compute loss
           - Backward pass
           - Update weights
           - Track metrics
        5. Calculate epoch statistics
        6. Return average loss and accuracy
        """
        # TODO: Set model to training mode
        # Hint: model.train()

        running_loss = 0.0
        correct = 0
        total = 0

        # TODO: Iterate through batches
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            # TODO: Move data to device
            # Hint: inputs, targets = inputs.to(self.device), targets.to(self.device)

            # TODO: Zero gradients
            # Hint: optimizer.zero_grad()

            # TODO: Forward pass
            # Hint: outputs = model(inputs)

            # TODO: Compute loss
            # Hint: loss = criterion(outputs, targets)

            # TODO: Backward pass
            # Hint: loss.backward()

            # TODO: Update weights
            # Hint: optimizer.step()

            # TODO: Track metrics
            # running_loss += loss.item()
            # _, predicted = outputs.max(1)
            # total += targets.size(0)
            # correct += predicted.eq(targets).sum().item()

            # Optional: Log progress every N batches
            if batch_idx % 10 == 0:
                logger.debug(f"Batch {batch_idx}/{len(train_loader)}, Loss: {0:.4f}")

        # TODO: Calculate epoch statistics
        epoch_loss = 0.0  # Replace with running_loss / len(train_loader)
        epoch_acc = 0.0   # Replace with 100.0 * correct / total

        return epoch_loss, epoch_acc

    def validate(
        self,
        model: nn.Module,
        val_loader: DataLoader,
        criterion: nn.Module
    ) -> Tuple[float, float]:
        """
        Validate the model.

        Args:
            model: PyTorch model
            val_loader: Validation data loader
            criterion: Loss function

        Returns:
            Tuple of (average_loss, accuracy)

        TODO:
        1. Set model to evaluation mode
        2. Disable gradient computation
        3. Iterate through batches
        4. For each batch:
           - Move data to device
           - Forward pass (no backward pass!)
           - Compute loss
           - Track metrics
        5. Calculate validation statistics
        6. Return average loss and accuracy
        """
        # TODO: Set model to evaluation mode
        # Hint: model.eval()

        val_loss = 0.0
        correct = 0
        total = 0

        # TODO: Disable gradient computation
        # Hint: with torch.no_grad():
        for inputs, targets in val_loader:
            # TODO: Move data to device
            # inputs, targets = inputs.to(self.device), targets.to(self.device)

            # TODO: Forward pass
            # outputs = model(inputs)

            # TODO: Compute loss
            # loss = criterion(outputs, targets)

            # TODO: Track metrics
            # val_loss += loss.item()
            # _, predicted = outputs.max(1)
            # total += targets.size(0)
            # correct += predicted.eq(targets).sum().item()
            pass

        # TODO: Calculate validation statistics
        avg_val_loss = 0.0  # Replace with val_loss / len(val_loader)
        val_acc = 0.0       # Replace with 100.0 * correct / total

        return avg_val_loss, val_acc

    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        num_classes: int,
        params: Dict[str, Any]
    ) -> Tuple[nn.Module, float]:
        """
        Complete training pipeline with MLflow tracking.

        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            num_classes: Number of output classes
            params: Training hyperparameters

        Returns:
            Tuple of (trained_model, best_validation_accuracy)

        TODO:
        1. Start MLflow run
        2. Log parameters
        3. Create model, criterion, optimizer
        4. Training loop:
           - Train epoch
           - Validate
           - Log metrics to MLflow
           - Save best model
           - Check early stopping
        5. Log final model and artifacts
        6. End MLflow run
        7. Return model and best accuracy

        Expected params:
        - model_name: str
        - num_epochs: int
        - batch_size: int
        - learning_rate: float
        - optimizer: str ('adam', 'sgd')
        - lr_step_size: int (for scheduler)
        - lr_gamma: float (for scheduler)
        - early_stopping_patience: int
        """
        logger.info("Starting training pipeline")

        # TODO: Start MLflow run
        run_name = f"train_{params['model_name']}_{int(time.time())}"
        tags = {
            "model_architecture": params['model_name'],
            "framework": "pytorch",
            "task": "image_classification"
        }
        # self.tracker.start_run(run_name=run_name, tags=tags)

        # TODO: Log all parameters
        # self.tracker.log_params(params)

        # TODO: Create model
        # model = self.create_model(num_classes, params['model_name'])

        # TODO: Define loss function
        # Hint: criterion = nn.CrossEntropyLoss()

        # TODO: Create optimizer
        # if params['optimizer'] == 'adam':
        #     optimizer = optim.Adam(model.parameters(), lr=params['learning_rate'])
        # elif params['optimizer'] == 'sgd':
        #     optimizer = optim.SGD(model.parameters(), lr=params['learning_rate'], momentum=0.9)

        # TODO: Create learning rate scheduler
        # Hint: scheduler = optim.lr_scheduler.StepLR(
        #           optimizer,
        #           step_size=params['lr_step_size'],
        #           gamma=params['lr_gamma']
        #       )

        # TODO: Initialize tracking variables
        best_val_acc = 0.0
        epochs_without_improvement = 0
        best_model_path = Path(self.config['model_save_path']) / 'best_model.pth'

        # TODO: Training loop
        for epoch in range(params['num_epochs']):
            epoch_start = time.time()

            logger.info(f"Epoch {epoch + 1}/{params['num_epochs']}")

            # TODO: Train epoch
            # train_loss, train_acc = self.train_epoch(model, train_loader, criterion, optimizer)

            # TODO: Validate
            # val_loss, val_acc = self.validate(model, val_loader, criterion)

            # TODO: Update learning rate
            # scheduler.step()

            # TODO: Log metrics to MLflow
            # self.tracker.log_metrics({
            #     'train_loss': train_loss,
            #     'train_accuracy': train_acc,
            #     'val_loss': val_loss,
            #     'val_accuracy': val_acc,
            #     'learning_rate': optimizer.param_groups[0]['lr']
            # }, step=epoch)

            # TODO: Save best model
            # if val_acc > best_val_acc:
            #     best_val_acc = val_acc
            #     torch.save(model.state_dict(), best_model_path)
            #     epochs_without_improvement = 0
            #     logger.info(f"New best model! Val accuracy: {val_acc:.2f}%")
            # else:
            #     epochs_without_improvement += 1

            # TODO: Early stopping check
            # if epochs_without_improvement >= params.get('early_stopping_patience', 5):
            #     logger.info(f"Early stopping triggered after {epoch + 1} epochs")
            #     break

            # TODO: Log epoch time
            epoch_time = time.time() - epoch_start
            logger.info(f"Epoch completed in {epoch_time:.2f}s")

        # TODO: Log best model to MLflow
        # self.tracker.log_model(model, "model")
        # self.tracker.log_artifact(str(best_model_path))

        # TODO: Log final metrics
        # self.tracker.log_metrics({
        #     'best_val_accuracy': best_val_acc,
        #     'total_epochs': epoch + 1
        # })

        # TODO: End MLflow run
        # self.tracker.end_run()

        logger.info(f"Training complete! Best val accuracy: {best_val_acc:.2f}%")

        # TODO: Return model and best accuracy
        return None, 0.0  # Replace with (model, best_val_acc)


# Example usage and testing
if __name__ == "__main__":
    """
    Example usage of ModelTrainer class.

    TODO:
    1. Set up MLflow tracker
    2. Create sample data loaders
    3. Initialize ModelTrainer
    4. Run training
    5. View results in MLflow UI

    To view results:
    - Start MLflow UI: mlflow ui --port 5000
    - Open browser: http://localhost:5000
    """

    # TODO: MLflow configuration
    mlflow_config = {
        'tracking_uri': 'http://localhost:5000',
        'experiment_name': 'image_classification_test'
    }

    # TODO: Training configuration
    training_config = {
        'model_save_path': 'models',
        'num_epochs': 5,
        'batch_size': 32,
        'learning_rate': 0.001,
        'model_name': 'resnet18',
        'optimizer': 'adam',
        'lr_step_size': 3,
        'lr_gamma': 0.1,
        'early_stopping_patience': 3
    }

    # TODO: Initialize MLflow tracker
    # tracker = MLflowTracker(
    #     tracking_uri=mlflow_config['tracking_uri'],
    #     experiment_name=mlflow_config['experiment_name']
    # )

    # TODO: Initialize trainer
    # trainer = ModelTrainer(training_config, tracker)

    # TODO: Create sample data loaders
    # Note: You would need to create actual DataLoaders with real data
    # For now, this is just a placeholder

    # TODO: Run training
    # model, best_acc = trainer.train(
    #     train_loader=train_loader,
    #     val_loader=val_loader,
    #     num_classes=4,
    #     params=training_config
    # )

    print("ModelTrainer module loaded. Implement the TODOs to complete functionality.")
    print("Don't forget to start MLflow server: mlflow server --port 5000")
