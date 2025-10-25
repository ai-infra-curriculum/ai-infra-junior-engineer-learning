"""
Custom ML Metrics for Monitoring

This module implements ML-specific metrics that go beyond standard application monitoring:
- Data drift detection (distribution shift in features)
- Model performance degradation tracking
- Prediction confidence analysis
- Feature importance drift
- Data quality monitoring

Learning Objectives:
- Implement data drift detection using statistical tests
- Track model performance over time
- Monitor data quality issues
- Understand ML-specific observability challenges
- Build custom metric exporters for Prometheus

References:
- Statistical Tests: https://docs.scipy.org/doc/scipy/reference/stats.html
- Evidently AI: https://evidentlyai.com/
- ML Monitoring Best Practices: https://christophergs.com/machine%20learning/2020/03/14/how-to-monitor-machine-learning-models/
"""

import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime
import json

# TODO: Import your metrics from instrumentation.py
# from instrumentation import (
#     data_drift_score,
#     model_accuracy,
#     missing_features_total,
#     model_prediction_confidence
# )

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes for Results
# =============================================================================

@dataclass
class DriftDetectionResult:
    """Results from drift detection test."""
    feature_name: str
    statistic: float
    p_value: float
    is_drift: bool
    test_method: str
    timestamp: datetime


@dataclass
class ModelPerformanceMetrics:
    """Model performance metrics over time."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    sample_count: int
    timestamp: datetime


# =============================================================================
# Data Drift Detection
# =============================================================================

class DataDriftDetector:
    """
    Detect distribution shifts in input data using statistical tests.

    This class implements multiple drift detection methods:
    1. Kolmogorov-Smirnov (KS) Test: For continuous features
    2. Population Stability Index (PSI): For binned distributions
    3. Jensen-Shannon Divergence: For probability distributions
    4. Chi-Square Test: For categorical features

    Usage:
        # Initialize with reference data (training set)
        detector = DataDriftDetector(
            reference_data=X_train,
            feature_names=feature_names,
            threshold=0.05
        )

        # Check for drift in production data
        drift_results = detector.detect_drift(X_production)

        # Export metrics to Prometheus
        detector.export_drift_metrics()
    """

    def __init__(
        self,
        reference_data: np.ndarray,
        feature_names: List[str],
        threshold: float = 0.05,
        method: str = 'ks'
    ):
        """
        Initialize drift detector with reference distribution.

        Args:
            reference_data: Training data distribution (n_samples, n_features)
            feature_names: List of feature names
            threshold: P-value threshold for drift detection (default: 0.05)
            method: Drift detection method ('ks', 'psi', 'js', 'chi2')
        """
        # TODO: Store reference data and parameters
        # self.reference_data = reference_data
        # self.feature_names = feature_names
        # self.threshold = threshold
        # self.method = method
        # self.n_features = reference_data.shape[1]
        #
        # # Validate inputs
        # if len(feature_names) != self.n_features:
        #     raise ValueError(
        #         f"Number of feature names ({len(feature_names)}) "
        #         f"must match number of features ({self.n_features})"
        #     )

        pass  # Remove after implementing

    def kolmogorov_smirnov_test(
        self,
        reference: np.ndarray,
        current: np.ndarray
    ) -> Tuple[float, float]:
        """
        Perform Kolmogorov-Smirnov test for distribution shift.

        The KS test compares two distributions and returns:
        - statistic: Maximum distance between CDFs (0-1)
        - p_value: Probability distributions are the same

        Args:
            reference: Reference distribution (1D array)
            current: Current distribution to test (1D array)

        Returns:
            Tuple of (statistic, p_value)
        """
        # TODO: Implement KS test using scipy.stats.ks_2samp
        #
        # Example:
        # statistic, p_value = stats.ks_2samp(reference, current)
        #
        # Interpretation:
        # - statistic close to 0 = similar distributions
        # - statistic close to 1 = very different distributions
        # - p_value < threshold = reject null hypothesis (drift detected)
        #
        # return statistic, p_value

        pass  # Remove after implementing

    def population_stability_index(
        self,
        reference: np.ndarray,
        current: np.ndarray,
        bins: int = 10
    ) -> float:
        """
        Calculate Population Stability Index (PSI).

        PSI measures distribution shift using binned histograms:
        - PSI < 0.1: No significant change
        - PSI 0.1-0.25: Moderate change
        - PSI > 0.25: Significant change

        Formula:
        PSI = Σ (current% - reference%) * ln(current% / reference%)

        Args:
            reference: Reference distribution
            current: Current distribution
            bins: Number of bins for histogram

        Returns:
            PSI score (0 = identical, higher = more drift)
        """
        # TODO: Implement PSI calculation
        #
        # Steps:
        # 1. Create histogram bins from reference data
        #    ref_hist, bin_edges = np.histogram(reference, bins=bins)
        #    cur_hist, _ = np.histogram(current, bins=bin_edges)
        #
        # 2. Convert to percentages
        #    ref_pct = ref_hist / len(reference)
        #    cur_pct = cur_hist / len(current)
        #
        # 3. Avoid division by zero (add small epsilon)
        #    epsilon = 1e-10
        #    ref_pct = np.where(ref_pct == 0, epsilon, ref_pct)
        #    cur_pct = np.where(cur_pct == 0, epsilon, cur_pct)
        #
        # 4. Calculate PSI
        #    psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))
        #
        # return psi

        pass  # Remove after implementing

    def jensen_shannon_divergence(
        self,
        reference: np.ndarray,
        current: np.ndarray,
        bins: int = 50
    ) -> float:
        """
        Calculate Jensen-Shannon divergence between distributions.

        JS divergence is symmetric and bounded [0, 1]:
        - 0 = identical distributions
        - 1 = completely different distributions

        Args:
            reference: Reference distribution
            current: Current distribution
            bins: Number of bins for histogram

        Returns:
            JS divergence score (0-1)
        """
        # TODO: Implement JS divergence
        #
        # Steps:
        # 1. Create normalized histograms
        #    ref_hist, bin_edges = np.histogram(reference, bins=bins, density=True)
        #    cur_hist, _ = np.histogram(current, bins=bin_edges, density=True)
        #
        # 2. Normalize to probability distributions
        #    ref_prob = ref_hist / np.sum(ref_hist)
        #    cur_prob = cur_hist / np.sum(cur_hist)
        #
        # 3. Calculate JS divergence
        #    from scipy.spatial.distance import jensenshannon
        #    js_distance = jensenshannon(ref_prob, cur_prob)
        #
        # return js_distance

        pass  # Remove after implementing

    def detect_drift(
        self,
        current_data: np.ndarray
    ) -> List[DriftDetectionResult]:
        """
        Detect drift across all features.

        Args:
            current_data: Current production data (n_samples, n_features)

        Returns:
            List of drift detection results per feature
        """
        # TODO: Implement drift detection for all features
        #
        # Pseudocode:
        # results = []
        #
        # for i, feature_name in enumerate(self.feature_names):
        #     reference_feature = self.reference_data[:, i]
        #     current_feature = current_data[:, i]
        #
        #     # Choose method
        #     if self.method == 'ks':
        #         statistic, p_value = self.kolmogorov_smirnov_test(
        #             reference_feature, current_feature
        #         )
        #         is_drift = p_value < self.threshold
        #
        #     elif self.method == 'psi':
        #         statistic = self.population_stability_index(
        #             reference_feature, current_feature
        #         )
        #         p_value = None
        #         is_drift = statistic > 0.25  # PSI threshold
        #
        #     elif self.method == 'js':
        #         statistic = self.jensen_shannon_divergence(
        #             reference_feature, current_feature
        #         )
        #         p_value = None
        #         is_drift = statistic > 0.5  # JS threshold
        #
        #     # Create result
        #     result = DriftDetectionResult(
        #         feature_name=feature_name,
        #         statistic=statistic,
        #         p_value=p_value,
        #         is_drift=is_drift,
        #         test_method=self.method,
        #         timestamp=datetime.now()
        #     )
        #
        #     results.append(result)
        #
        #     # Log drift detection
        #     if is_drift:
        #         logger.warning(
        #             f"Drift detected in {feature_name}: "
        #             f"statistic={statistic:.4f}, p_value={p_value}"
        #         )
        #
        # return results

        pass  # Remove after implementing

    def export_drift_metrics(self, drift_results: List[DriftDetectionResult]):
        """
        Export drift detection results to Prometheus metrics.

        Args:
            drift_results: List of drift detection results
        """
        # TODO: Update Prometheus drift metrics
        #
        # for result in drift_results:
        #     # Update drift score gauge
        #     data_drift_score.labels(
        #         feature_name=result.feature_name
        #     ).set(result.statistic)
        #
        #     # Log to application logs (for Elasticsearch)
        #     logger.info(
        #         "Drift detection result",
        #         extra={
        #             'feature_name': result.feature_name,
        #             'statistic': result.statistic,
        #             'p_value': result.p_value,
        #             'is_drift': result.is_drift,
        #             'method': result.test_method
        #         }
        #     )

        pass  # Remove after implementing


# =============================================================================
# Model Performance Monitor
# =============================================================================

class ModelPerformanceMonitor:
    """
    Monitor model performance metrics over time.

    Tracks:
    - Accuracy, Precision, Recall, F1 Score
    - Performance degradation alerts
    - Ground truth feedback loop
    - Confusion matrix tracking

    Usage:
        monitor = ModelPerformanceMonitor(model_name='resnet50')

        # Log predictions
        monitor.log_prediction(prediction=1, ground_truth=1)

        # Calculate metrics (after collecting enough ground truth)
        metrics = monitor.calculate_metrics()

        # Check for degradation
        is_degraded = monitor.check_degradation(baseline_accuracy=0.90)
    """

    def __init__(self, model_name: str, min_samples: int = 100):
        """
        Initialize performance monitor.

        Args:
            model_name: Name of the model being monitored
            min_samples: Minimum samples before calculating metrics
        """
        # TODO: Initialize monitor
        # self.model_name = model_name
        # self.min_samples = min_samples
        # self.predictions = []
        # self.ground_truth = []
        # self.prediction_timestamps = []

        pass  # Remove after implementing

    def log_prediction(
        self,
        prediction: int,
        ground_truth: Optional[int] = None,
        prediction_id: Optional[str] = None
    ):
        """
        Log a prediction with optional ground truth.

        Args:
            prediction: Model prediction (class index)
            ground_truth: True label (optional, may come later)
            prediction_id: Unique ID to match prediction with future ground truth
        """
        # TODO: Store prediction
        #
        # self.predictions.append(prediction)
        # if ground_truth is not None:
        #     self.ground_truth.append(ground_truth)
        # self.prediction_timestamps.append(datetime.now())
        #
        # Note: In production, you might use a database to store predictions
        # and match them with ground truth that arrives later

        pass  # Remove after implementing

    def add_ground_truth(self, prediction_id: str, ground_truth: int):
        """
        Add ground truth label for a previous prediction.

        This simulates a feedback loop where ground truth labels
        arrive after the prediction is made.

        Args:
            prediction_id: ID of the prediction
            ground_truth: True label
        """
        # TODO: Implement ground truth feedback
        #
        # In a real system, you would:
        # 1. Look up prediction by ID
        # 2. Store ground truth
        # 3. Update metrics

        pass  # Remove after implementing

    def calculate_metrics(self) -> Optional[ModelPerformanceMetrics]:
        """
        Calculate performance metrics from predictions and ground truth.

        Returns:
            ModelPerformanceMetrics if enough samples, else None
        """
        # TODO: Implement metrics calculation
        #
        # if len(self.ground_truth) < self.min_samples:
        #     logger.warning(
        #         f"Not enough samples for metrics calculation "
        #         f"({len(self.ground_truth)} / {self.min_samples})"
        #     )
        #     return None
        #
        # # Import sklearn metrics
        # from sklearn.metrics import (
        #     accuracy_score,
        #     precision_score,
        #     recall_score,
        #     f1_score
        # )
        #
        # # Calculate metrics
        # accuracy = accuracy_score(self.ground_truth, self.predictions)
        # precision = precision_score(
        #     self.ground_truth,
        #     self.predictions,
        #     average='weighted'
        # )
        # recall = recall_score(
        #     self.ground_truth,
        #     self.predictions,
        #     average='weighted'
        # )
        # f1 = f1_score(
        #     self.ground_truth,
        #     self.predictions,
        #     average='weighted'
        # )
        #
        # metrics = ModelPerformanceMetrics(
        #     accuracy=accuracy,
        #     precision=precision,
        #     recall=recall,
        #     f1_score=f1,
        #     sample_count=len(self.ground_truth),
        #     timestamp=datetime.now()
        # )
        #
        # # Update Prometheus metrics
        # model_accuracy.labels(model_name=self.model_name).set(accuracy)
        #
        # # Log metrics
        # logger.info(
        #     f"Model performance metrics: accuracy={accuracy:.4f}, "
        #     f"precision={precision:.4f}, recall={recall:.4f}, f1={f1:.4f}"
        # )
        #
        # return metrics

        pass  # Remove after implementing

    def check_degradation(
        self,
        baseline_accuracy: float,
        threshold: float = 0.1
    ) -> bool:
        """
        Check if model performance has degraded significantly.

        Args:
            baseline_accuracy: Expected baseline accuracy
            threshold: Degradation threshold (e.g., 0.1 = 10% drop)

        Returns:
            True if degradation detected, False otherwise
        """
        # TODO: Implement degradation check
        #
        # if len(self.ground_truth) < self.min_samples:
        #     return False
        #
        # from sklearn.metrics import accuracy_score
        # current_accuracy = accuracy_score(self.ground_truth, self.predictions)
        # degradation = baseline_accuracy - current_accuracy
        #
        # if degradation > threshold:
        #     logger.error(
        #         f"Performance degradation detected! "
        #         f"Baseline: {baseline_accuracy:.4f}, "
        #         f"Current: {current_accuracy:.4f}, "
        #         f"Degradation: {degradation:.4f}"
        #     )
        #     return True
        #
        # return False

        pass  # Remove after implementing


# =============================================================================
# Prediction Confidence Analyzer
# =============================================================================

class ConfidenceAnalyzer:
    """
    Analyze prediction confidence scores over time.

    Tracks:
    - Confidence distribution
    - Low confidence predictions
    - Confidence vs accuracy correlation
    - Confidence drift

    Usage:
        analyzer = ConfidenceAnalyzer()
        analyzer.log_confidence(confidence=0.95, is_correct=True)
        stats = analyzer.get_statistics()
    """

    def __init__(self, window_size: int = 1000):
        """
        Initialize confidence analyzer.

        Args:
            window_size: Number of recent predictions to analyze
        """
        # TODO: Initialize analyzer
        # self.window_size = window_size
        # self.confidences = []
        # self.correctness = []  # Whether prediction was correct

        pass  # Remove after implementing

    def log_confidence(self, confidence: float, is_correct: Optional[bool] = None):
        """
        Log prediction confidence.

        Args:
            confidence: Prediction confidence (0-1)
            is_correct: Whether prediction was correct (optional)
        """
        # TODO: Store confidence
        #
        # self.confidences.append(confidence)
        # if is_correct is not None:
        #     self.correctness.append(is_correct)
        #
        # # Keep only recent window
        # if len(self.confidences) > self.window_size:
        #     self.confidences = self.confidences[-self.window_size:]
        #     self.correctness = self.correctness[-self.window_size:]

        pass  # Remove after implementing

    def get_statistics(self) -> Dict[str, float]:
        """
        Calculate confidence statistics.

        Returns:
            Dictionary with statistics (mean, median, std, percentiles)
        """
        # TODO: Calculate statistics
        #
        # if len(self.confidences) == 0:
        #     return {}
        #
        # confidences_array = np.array(self.confidences)
        #
        # stats = {
        #     'mean': np.mean(confidences_array),
        #     'median': np.median(confidences_array),
        #     'std': np.std(confidences_array),
        #     'min': np.min(confidences_array),
        #     'max': np.max(confidences_array),
        #     'p25': np.percentile(confidences_array, 25),
        #     'p50': np.percentile(confidences_array, 50),
        #     'p75': np.percentile(confidences_array, 75),
        #     'p95': np.percentile(confidences_array, 95),
        #     'count': len(self.confidences)
        # }
        #
        # # Calculate calibration (if ground truth available)
        # if len(self.correctness) > 0:
        #     # Group by confidence bins and check accuracy
        #     # This tells you if high confidence = high accuracy
        #     stats['calibration_score'] = self._calculate_calibration()
        #
        # return stats

        pass  # Remove after implementing

    def _calculate_calibration(self) -> float:
        """
        Calculate model calibration score.

        A well-calibrated model: predictions with 90% confidence are correct 90% of the time.

        Returns:
            Calibration error (lower is better)
        """
        # TODO: Implement calibration calculation
        #
        # This is advanced - optional for junior level
        #
        # Hint: Use sklearn.calibration.calibration_curve

        return 0.0


# =============================================================================
# Data Quality Monitor
# =============================================================================

class DataQualityMonitor:
    """
    Monitor data quality issues in production requests.

    Checks for:
    - Missing values
    - Out-of-range values
    - Type errors
    - Schema changes
    - Encoding errors
    """

    def __init__(self, expected_schema: Dict[str, str]):
        """
        Initialize data quality monitor.

        Args:
            expected_schema: Expected schema {feature_name: data_type}
        """
        # TODO: Initialize monitor
        # self.expected_schema = expected_schema
        # self.issue_counts = {
        #     'missing': {},
        #     'out_of_range': {},
        #     'type_error': {},
        #     'schema_mismatch': 0
        # }

        pass  # Remove after implementing

    def validate_request(self, data: Dict) -> Dict[str, List[str]]:
        """
        Validate incoming request data.

        Args:
            data: Request data dictionary

        Returns:
            Dictionary of issues found {issue_type: [feature_names]}
        """
        # TODO: Implement validation
        #
        # issues = {
        #     'missing': [],
        #     'type_error': [],
        #     'out_of_range': []
        # }
        #
        # # Check for missing features
        # for feature_name in self.expected_schema:
        #     if feature_name not in data:
        #         issues['missing'].append(feature_name)
        #         missing_features_total.labels(
        #             feature_name=feature_name
        #         ).inc()
        #
        # # Check data types
        # for feature_name, value in data.items():
        #     expected_type = self.expected_schema.get(feature_name)
        #     if expected_type and not isinstance(value, eval(expected_type)):
        #         issues['type_error'].append(feature_name)
        #
        # # Check value ranges (you'd define these)
        # # Example: if 'age' not in range(0, 120):
        # #     issues['out_of_range'].append('age')
        #
        # return issues

        pass  # Remove after implementing


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("Custom ML Metrics Module")
    print("=" * 50)

    # TODO: Add example usage
    #
    # Example 1: Drift Detection
    # print("\n1. Testing Drift Detection:")
    # # Generate reference data
    # np.random.seed(42)
    # reference_data = np.random.normal(0, 1, (1000, 3))
    # feature_names = ['feature_1', 'feature_2', 'feature_3']
    #
    # # Create detector
    # detector = DataDriftDetector(
    #     reference_data=reference_data,
    #     feature_names=feature_names,
    #     threshold=0.05,
    #     method='ks'
    # )
    #
    # # Test with drifted data (mean shifted)
    # drifted_data = np.random.normal(0.5, 1, (1000, 3))
    # drift_results = detector.detect_drift(drifted_data)
    #
    # for result in drift_results:
    #     print(f"{result.feature_name}: drift={result.is_drift}, "
    #           f"statistic={result.statistic:.4f}, p_value={result.p_value:.4f}")

    # Example 2: Performance Monitoring
    # print("\n2. Testing Performance Monitoring:")
    # monitor = ModelPerformanceMonitor('test_model', min_samples=10)
    #
    # # Simulate predictions
    # for i in range(20):
    #     pred = np.random.randint(0, 2)
    #     truth = np.random.randint(0, 2)
    #     monitor.log_prediction(pred, truth)
    #
    # # Calculate metrics
    # metrics = monitor.calculate_metrics()
    # if metrics:
    #     print(f"Accuracy: {metrics.accuracy:.4f}")
    #     print(f"F1 Score: {metrics.f1_score:.4f}")

    print("\nImplement the TODOs and uncomment examples to test!")
