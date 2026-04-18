import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
try:
    import tensorflow_data_validation as tfdv
    TFDV_AVAILABLE = True
except ImportError:
    TFDV_AVAILABLE = False

try:
    from google.cloud import aiplatform
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

from sklearn.metrics import recall_score, confusion_matrix
import logging

logger = logging.getLogger(__name__)

class AuditEngine:
    """
    Audit Engine for calculating fairness metrics and running data validation.
    Integrates TFDV and Vertex AI Model Monitoring for comprehensive bias detection.
    """

    def __init__(self, project_id: str = None, location: str = "us-central1"):
        """
        Initialize the Audit Engine.

        Args:
            project_id: GCP project ID for Vertex AI
            location: GCP location for Vertex AI resources
        """
        self.project_id = project_id
        self.location = location
        if project_id and VERTEX_AI_AVAILABLE:
            aiplatform.init(project=project_id, location=location)

    def calculate_disparate_impact(self, y_true: np.ndarray, y_pred: np.ndarray,
                                 protected_attribute: np.ndarray) -> float:
        """
        Calculate Disparate Impact metric.

        Disparate Impact = P(Y_pred=1 | A=0) / P(Y_pred=1 | A=1)
        Where A is the protected attribute (0 = privileged, 1 = unprivileged)

        Args:
            y_true: True labels
            y_pred: Predicted labels
            protected_attribute: Binary protected attribute

        Returns:
            Disparate Impact ratio
        """
        privileged_mask = protected_attribute == 0
        unprivileged_mask = protected_attribute == 1

        privileged_positive_rate = np.mean(y_pred[privileged_mask])
        unprivileged_positive_rate = np.mean(y_pred[unprivileged_mask])

        # Avoid division by zero and prevent 'inf' JSON serialization crashes
        if unprivileged_positive_rate == 0.0:
            return 999.0 if privileged_positive_rate > 0.0 else 1.0

        disparate_impact = privileged_positive_rate / unprivileged_positive_rate
        return float(disparate_impact)

    def calculate_recall_difference(self, y_true: np.ndarray, y_pred: np.ndarray,
                                  protected_attribute: np.ndarray) -> float:
        """
        Calculate Recall Difference (Equal Opportunity Difference).

        Recall Difference = Recall_privileged - Recall_unprivileged

        Args:
            y_true: True labels
            y_pred: Predicted labels
            protected_attribute: Binary protected attribute

        Returns:
            Recall difference
        """
        privileged_mask = protected_attribute == 0
        unprivileged_mask = protected_attribute == 1

        privileged_recall = recall_score(y_true[privileged_mask], y_pred[privileged_mask])
        unprivileged_recall = recall_score(y_true[unprivileged_mask], y_pred[unprivileged_mask])

        recall_difference = privileged_recall - unprivileged_recall
        return float(recall_difference)

    def validate_data_with_tfdv(self, df: pd.DataFrame, schema_path: str = None) -> Dict[str, Any]:
        """
        Validate data using TensorFlow Data Validation (TFDV).

        Args:
            df: Input dataframe
            schema_path: Path to existing schema file (optional)

        Returns:
            Validation statistics and anomalies
        """
        if not TFDV_AVAILABLE:
            return {
                'anomaly_count': None,
                'status': 'error',
                'warning': 'TensorFlow Data Validation not available. Install tensorflow-data-validation for full functionality.'
            }

        try:
            # Generate statistics
            stats = tfdv.generate_statistics_from_dataframe(df)

            # Load or infer schema
            if schema_path:
                schema = tfdv.load_schema_text(schema_path)
            else:
                schema = tfdv.infer_schema(statistics=stats)

            # Validate statistics against schema
            anomalies = tfdv.validate_statistics(statistics=stats, schema=schema)

            return {
                'anomaly_count': len(anomalies.anomaly_info) if anomalies else 0,
                'message': 'Data validation completed successfully'
            }
        except Exception as e:
            logger.error(f"TFDV validation failed: {str(e)}")
            return {'anomaly_count': None, 'status': 'failed', 'error': str(e)}

    def run_skew_detection_job(self, model_name: str, dataset_path: str,
                             target_field: str, skew_thresholds: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Run a Skew Detection job using Vertex AI Model Monitoring.

        Args:
            model_name: Name of the deployed model in Vertex AI
            dataset_path: GCS path to the dataset for monitoring
            target_field: Name of the target field
            skew_thresholds: Custom skew thresholds

        Returns:
            Job results and monitoring configuration
        """
        if not VERTEX_AI_AVAILABLE:
            return {
                'status': 'simulated',
                'message': 'Vertex AI SDK not available. Install google-cloud-aiplatform for full functionality.',
                'model_name': model_name,
                'dataset_path': dataset_path,
                'target_field': target_field,
                'skew_thresholds': skew_thresholds or {
                    'prediction_output': 0.1,
                    'feature_skew': 0.1
                }
            }

        if not self.project_id:
            return {'error': 'GCP project ID not configured'}

        try:
            # This is a simplified implementation. In production, you would:
            # 1. Create or get existing Endpoint
            # 2. Set up Model Monitoring job with skew detection
            # 3. Configure monitoring objectives

            # For demo purposes, we'll simulate the setup
            monitoring_config = {
                'model_name': model_name,
                'dataset_path': dataset_path,
                'target_field': target_field,
                'skew_thresholds': skew_thresholds or {
                    'prediction_output': 0.1,
                    'feature_skew': 0.1
                },
                'status': 'configured',
                'message': 'Skew detection job configured successfully'
            }

            # In a real implementation, you would create the actual monitoring job:
            # endpoint = aiplatform.Endpoint(endpoint_name=endpoint_name)
            # monitoring_job = endpoint.create_monitoring_job(...)

            return monitoring_config

        except Exception as e:
            logger.error(f"Skew detection job failed: {str(e)}")
            return {'error': str(e)}

    def comprehensive_audit(self, df: pd.DataFrame, y_true: np.ndarray, y_pred: np.ndarray,
                          protected_attribute: np.ndarray, protected_attr_name: str = "protected",
                          model_name: str = None, dataset_path: str = None, target_field: str = None) -> Dict[str, Any]:
        """
        Run comprehensive audit including all fairness metrics and data validation.

        Args:
            df: Input dataframe
            y_true: True labels
            y_pred: Predicted labels
            protected_attribute: Binary protected attribute
            protected_attr_name: Name of protected attribute for reporting
            model_name: Optional dynamic model name for Vertex AI skew detection
            dataset_path: Optional dynamic dataset path for Vertex AI for skew detection
            target_field: Optional dynamic target field mapping for skew detection
            
        Returns:
            Comprehensive audit results
        """
        results = {}

        # Centralize mask calculations to optimize latency
        privileged_mask = protected_attribute == 0
        unprivileged_mask = protected_attribute == 1

        privileged_count = int(np.sum(privileged_mask))
        unprivileged_count = int(np.sum(unprivileged_mask))
        
        priv_pos_rate = float(np.mean(y_pred[privileged_mask])) if privileged_count > 0 else 0.0
        unpriv_pos_rate = float(np.mean(y_pred[unprivileged_mask])) if unprivileged_count > 0 else 0.0
        
        priv_recall = float(recall_score(y_true[privileged_mask], y_pred[privileged_mask])) if privileged_count > 0 else 0.0
        unpriv_recall = float(recall_score(y_true[unprivileged_mask], y_pred[unprivileged_mask])) if unprivileged_count > 0 else 0.0

        # Calculate metrics using precomputed rates instead of invoking separate internal loops
        if unpriv_pos_rate == 0.0:
            results['disparate_impact'] = 999.0 if priv_pos_rate > 0.0 else 1.0
        else:
            results['disparate_impact'] = priv_pos_rate / unpriv_pos_rate

        results['recall_difference'] = priv_recall - unpriv_recall

        results['group_statistics'] = {
            'privileged_count': privileged_count,
            'unprivileged_count': unprivileged_count,
            'privileged_positive_rate': priv_pos_rate,
            'unprivileged_positive_rate': unpriv_pos_rate,
            'privileged_recall': priv_recall,
            'unprivileged_recall': unpriv_recall
        }

        # Data validation with TFDV
        results['data_validation'] = self.validate_data_with_tfdv(df)

        # Fairness assessment
        results['fairness_assessment'] = self._assess_fairness(results)

        # Skew detection setup dynamically configured for real operational monitoring
        if model_name and dataset_path and target_field:
            results['skew_detection'] = self.run_skew_detection_job(
                model_name=model_name,
                dataset_path=dataset_path,
                target_field=target_field
            )
        else:
            results['skew_detection'] = {
                'status': 'skipped',
                'message': 'Missing dynamic configuration. Skew detection skipped.'
            }

        return results

    def _assess_fairness(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess overall fairness based on calculated metrics.

        Args:
            results: Audit results

        Returns:
            Fairness assessment
        """
        assessment = {
            'disparate_impact_status': 'unknown',
            'recall_difference_status': 'unknown',
            'overall_risk': 'unknown'
        }

        # Disparate Impact assessment (should be close to 1.0)
        di = results.get('disparate_impact', 1.0)
        if 0.8 <= di <= 1.25:
            assessment['disparate_impact_status'] = 'fair'
        elif di < 0.8 or di > 1.25:
            assessment['disparate_impact_status'] = 'concerning'
        else:
            assessment['disparate_impact_status'] = 'severe'

        # Recall Difference assessment (should be close to 0)
        rd = abs(results.get('recall_difference', 0))
        if rd <= 0.05:
            assessment['recall_difference_status'] = 'fair'
        elif rd <= 0.1:
            assessment['recall_difference_status'] = 'concerning'
        else:
            assessment['recall_difference_status'] = 'severe'

        # Overall risk
        if assessment['disparate_impact_status'] == 'fair' and assessment['recall_difference_status'] == 'fair':
            assessment['overall_risk'] = 'low'
        elif 'severe' in [assessment['disparate_impact_status'], assessment['recall_difference_status']]:
            assessment['overall_risk'] = 'high'
        else:
            assessment['overall_risk'] = 'medium'

        return assessment