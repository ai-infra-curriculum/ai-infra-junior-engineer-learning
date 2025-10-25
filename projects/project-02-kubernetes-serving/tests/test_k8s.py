"""
Kubernetes Deployment Tests

These tests verify that the Kubernetes deployment is correctly configured
and functioning as expected. They test infrastructure-level concerns like
health checks, auto-scaling, and service availability.

Learning Objectives:
- Write integration tests for Kubernetes deployments
- Use kubectl and Kubernetes Python client
- Test auto-scaling behavior
- Verify service discovery and load balancing

Prerequisites:
- kubectl configured to access cluster
- Deployment applied to cluster
- Python packages: kubernetes, requests, pytest
"""

import pytest
import subprocess
import json
import time
import requests
from typing import Dict, List, Any
from kubernetes import client, config

# TODO: Import Kubernetes Python client
# from kubernetes import client, config

# TODO: Configure Kubernetes client
# This loads kubeconfig from default location (~/.kube/config)
# For in-cluster access, use config.load_incluster_config()
def setup_k8s_client():
    """
    Configure Kubernetes client.

    TODO: Implement:
    1. Try to load in-cluster config (if running in pod)
    2. If that fails, load from kubeconfig file
    3. Create API client instances (AppsV1Api, CoreV1Api, AutoscalingV1Api)
    4. Return client instances

    Example:
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()

        apps_v1 = client.AppsV1Api()
        core_v1 = client.CoreV1Api()
        autoscaling_v1 = client.AutoscalingV1Api()
        return apps_v1, core_v1, autoscaling_v1
    """
    pass


# Configuration
NAMESPACE = "ml-serving"  # TODO: Update if using different namespace
DEPLOYMENT_NAME = "model-api"
SERVICE_NAME = "model-api-service"
HPA_NAME = "model-api-hpa"

# TODO: Initialize Kubernetes clients
# apps_v1, core_v1, autoscaling_v1 = setup_k8s_client()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def run_kubectl(command: List[str]) -> Dict[str, Any]:
    """
    Execute kubectl command and return JSON output.

    TODO: Implement:
    1. Build full command: kubectl + command + ["-o", "json"]
    2. Run subprocess.run() with capture_output=True
    3. Parse JSON output
    4. Return parsed data
    5. Handle errors gracefully

    Args:
        command: kubectl command parts (e.g., ["get", "pods", "-n", "ml-serving"])

    Returns:
        Dict with command output

    Example:
        result = run_kubectl(["get", "deployment", DEPLOYMENT_NAME, "-n", NAMESPACE])
        replica_count = result["spec"]["replicas"]
    """
    # TODO: Implement kubectl execution
    pass


def wait_for_condition(
    check_func,
    timeout: int = 300,
    interval: int = 5,
    condition_name: str = "condition"
) -> bool:
    """
    Wait for a condition to be true.

    TODO: Implement:
    1. Record start time
    2. Loop until timeout:
       a. Call check_func()
       b. If True, return True
       c. If False, sleep interval seconds
    3. If timeout exceeded, return False
    4. Log progress

    Args:
        check_func: Function that returns True when condition met
        timeout: Maximum time to wait (seconds)
        interval: Time between checks (seconds)
        condition_name: Description for logging

    Returns:
        bool: True if condition met, False if timeout

    Example:
        def pods_ready():
            return get_ready_pod_count() == 3

        success = wait_for_condition(pods_ready, timeout=300, condition_name="pods ready")
        assert success, "Pods did not become ready in time"
    """
    # TODO: Implement wait loop
    pass


def get_service_url(service_name: str, namespace: str) -> str:
    """
    Get external URL for LoadBalancer Service.

    TODO: Implement:
    1. Get Service object using core_v1.read_namespaced_service()
    2. Check service type (ClusterIP vs LoadBalancer)
    3. For LoadBalancer: extract external IP from status.loadBalancer.ingress
    4. For ClusterIP: use kubectl port-forward or return internal DNS name
    5. Construct URL: http://<ip>:<port>
    6. Return URL

    Args:
        service_name: Name of Service
        namespace: Kubernetes namespace

    Returns:
        str: Service URL

    Example:
        url = get_service_url(SERVICE_NAME, NAMESPACE)
        # Returns: "http://34.123.45.67:80"
    """
    # TODO: Implement service URL retrieval
    pass


# ============================================================================
# DEPLOYMENT TESTS
# ============================================================================

class TestDeployment:
    """Tests for Deployment configuration and status."""

    def test_deployment_exists(self):
        """
        Test that Deployment resource exists.

        TODO: Implement:
        1. Call apps_v1.read_namespaced_deployment(DEPLOYMENT_NAME, NAMESPACE)
        2. Assert deployment is not None
        3. Assert deployment name matches DEPLOYMENT_NAME
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_deployment_exists")

    def test_deployment_replicas(self):
        """
        Test that Deployment has correct number of replicas.

        TODO: Implement:
        1. Read Deployment
        2. Get spec.replicas (desired count)
        3. Get status.replicas (current count)
        4. Get status.readyReplicas (ready count)
        5. Assert desired == current == ready
        6. Assert count is at least 3 (minimum for HA)
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_deployment_replicas")

    def test_deployment_image(self):
        """
        Test that Deployment uses correct container image.

        TODO: Implement:
        1. Read Deployment
        2. Get container spec: deployment.spec.template.spec.containers[0]
        3. Check image tag (should not be 'latest' in production)
        4. Assert image name matches expected (model-api)
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_deployment_image")

    def test_deployment_resource_limits(self):
        """
        Test that Deployment has resource requests and limits.

        TODO: Implement:
        1. Read Deployment container spec
        2. Assert resources.requests.cpu is set
        3. Assert resources.requests.memory is set
        4. Assert resources.limits.cpu is set
        5. Assert resources.limits.memory is set
        6. Assert limits >= requests
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_deployment_resource_limits")

    def test_deployment_health_probes(self):
        """
        Test that Deployment has liveness and readiness probes.

        TODO: Implement:
        1. Read Deployment container spec
        2. Assert livenessProbe is configured
        3. Assert readinessProbe is configured
        4. Check probe paths (/health)
        5. Check probe timing (initialDelay, period, timeout)
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_deployment_health_probes")

    def test_deployment_update_strategy(self):
        """
        Test that Deployment has RollingUpdate strategy.

        TODO: Implement:
        1. Read Deployment
        2. Assert spec.strategy.type == "RollingUpdate"
        3. Assert maxSurge is configured (should be 1)
        4. Assert maxUnavailable is configured (should be 0)
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_deployment_update_strategy")


# ============================================================================
# POD TESTS
# ============================================================================

class TestPods:
    """Tests for Pod status and health."""

    def test_all_pods_running(self):
        """
        Test that all pods are in Running state.

        TODO: Implement:
        1. List pods with label selector: app=model-api
        2. Get pod statuses
        3. Assert all pods have phase == "Running"
        4. Assert count matches desired replicas
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_all_pods_running")

    def test_all_pods_ready(self):
        """
        Test that all pods are ready (passing readiness probe).

        TODO: Implement:
        1. List pods
        2. For each pod, check conditions
        3. Assert "Ready" condition status == "True"
        4. Assert containerStatuses[0].ready == True
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_all_pods_ready")

    def test_no_pod_restarts(self):
        """
        Test that pods haven't restarted excessively.

        TODO: Implement:
        1. List pods
        2. For each pod, get containerStatuses[0].restartCount
        3. Assert restart count < 3 (some restarts OK during deployment)
        4. Alert if any pod has high restart count
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_no_pod_restarts")

    def test_pod_resource_usage(self):
        """
        Test that pod resource usage is within limits.

        TODO: Implement:
        1. Get pod metrics: kubectl top pods
        2. Parse CPU and memory usage
        3. Compare to resource requests
        4. Assert usage < limits (not throttling)
        5. Warn if usage consistently below requests (over-provisioned)
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_pod_resource_usage")


# ============================================================================
# SERVICE TESTS
# ============================================================================

class TestService:
    """Tests for Service configuration and connectivity."""

    def test_service_exists(self):
        """
        Test that Service resource exists.

        TODO: Implement:
        1. Read Service: core_v1.read_namespaced_service()
        2. Assert service exists
        3. Assert service name matches SERVICE_NAME
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_service_exists")

    def test_service_endpoints(self):
        """
        Test that Service has endpoints (pod IPs).

        TODO: Implement:
        1. Read Endpoints: core_v1.read_namespaced_endpoints()
        2. Assert endpoints exist
        3. Assert number of endpoints == number of ready pods
        4. Assert each endpoint has IP and port
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_service_endpoints")

    def test_service_health_endpoint(self):
        """
        Test that Service /health endpoint is accessible.

        TODO: Implement:
        1. Get service URL
        2. Make GET request to /health
        3. Assert status code == 200
        4. Assert response JSON has "status": "healthy"
        5. Handle connection errors gracefully
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_service_health_endpoint")

    def test_service_metrics_endpoint(self):
        """
        Test that Service /metrics endpoint is accessible.

        TODO: Implement:
        1. Get service URL
        2. Make GET request to /metrics
        3. Assert status code == 200
        4. Assert response contains Prometheus metrics
        5. Check for expected metrics (model_api_requests_total)
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_service_metrics_endpoint")

    def test_service_load_balancing(self):
        """
        Test that Service distributes traffic across pods.

        TODO: Implement:
        1. Make multiple requests (100+) to service
        2. Track which pod handled each request (from logs or response)
        3. Assert all pods received requests
        4. Assert distribution is roughly even (within 20% variance)
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_service_load_balancing")


# ============================================================================
# AUTO-SCALING TESTS
# ============================================================================

class TestAutoScaling:
    """Tests for Horizontal Pod Autoscaler."""

    def test_hpa_exists(self):
        """
        Test that HPA resource exists.

        TODO: Implement:
        1. Read HPA: autoscaling_v1.read_namespaced_horizontal_pod_autoscaler()
        2. Assert HPA exists
        3. Assert HPA targets correct deployment
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_hpa_exists")

    def test_hpa_configuration(self):
        """
        Test that HPA has correct min/max replicas and target.

        TODO: Implement:
        1. Read HPA
        2. Assert minReplicas == 3
        3. Assert maxReplicas == 10
        4. Assert target CPU utilization == 70%
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_hpa_configuration")

    def test_hpa_current_metrics(self):
        """
        Test that HPA is reading current metrics.

        TODO: Implement:
        1. Read HPA status
        2. Assert currentReplicas is set
        3. Assert current CPU metrics are available
        4. Assert metrics are within expected range (0-100%)
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_hpa_current_metrics")

    @pytest.mark.slow
    def test_hpa_scale_up(self):
        """
        Test that HPA scales up under load.

        This is a slow test that generates load and waits for scaling.
        Mark as @pytest.mark.slow and skip in CI if needed.

        TODO: Implement:
        1. Record initial replica count
        2. Generate CPU load (kubectl run load-generator)
        3. Wait for CPU to exceed target (70%)
        4. Wait for HPA to scale up (timeout: 5 minutes)
        5. Assert new replica count > initial
        6. Clean up load generator
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_hpa_scale_up")

    @pytest.mark.slow
    def test_hpa_scale_down(self):
        """
        Test that HPA scales down after load decreases.

        TODO: Implement:
        1. Ensure replicas are scaled up (from previous test or manual)
        2. Stop load generator
        3. Wait for stabilization window (5 minutes)
        4. Wait for HPA to scale down (timeout: 10 minutes)
        5. Assert replica count decreased towards minimum
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_hpa_scale_down")


# ============================================================================
# ROLLING UPDATE TESTS
# ============================================================================

class TestRollingUpdate:
    """Tests for zero-downtime rolling updates."""

    @pytest.mark.slow
    def test_rolling_update_zero_downtime(self):
        """
        Test that rolling update completes without downtime.

        TODO: Implement:
        1. Record current image version
        2. Start background thread making continuous requests
        3. Update deployment image: kubectl set image
        4. Monitor rollout: kubectl rollout status
        5. Assert all requests succeeded (no 503 errors)
        6. Assert rollout completed successfully
        7. Rollback to original version
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_rolling_update_zero_downtime")

    @pytest.mark.slow
    def test_rolling_update_rollback(self):
        """
        Test that rollback works correctly.

        TODO: Implement:
        1. Record current revision number
        2. Perform update (change image tag or config)
        3. Wait for rollout to complete
        4. Trigger rollback: kubectl rollout undo
        5. Wait for rollback to complete
        6. Assert pods are running previous version
        7. Assert all health checks passing
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_rolling_update_rollback")


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

class TestConfiguration:
    """Tests for ConfigMap and Secrets."""

    def test_configmap_exists(self):
        """
        Test that ConfigMap exists and has expected keys.

        TODO: Implement:
        1. Read ConfigMap: core_v1.read_namespaced_config_map()
        2. Assert ConfigMap exists
        3. Assert required keys present: model_name, log_level, max_batch_size
        4. Assert values are non-empty
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_configmap_exists")

    def test_pods_use_configmap(self):
        """
        Test that pods successfully load configuration from ConfigMap.

        TODO: Implement:
        1. Get pod
        2. Execute: kubectl exec pod -- env
        3. Assert environment variables set from ConfigMap:
           - MODEL_NAME
           - LOG_LEVEL
           - MAX_BATCH_SIZE
        4. Assert values match ConfigMap
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_pods_use_configmap")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance and load tests."""

    @pytest.mark.slow
    def test_latency_under_load(self):
        """
        Test that P95 latency stays below 500ms under load.

        TODO: Implement:
        1. Get service URL
        2. Make 100 requests, recording latencies
        3. Calculate P95 latency (95th percentile)
        4. Assert P95 < 500ms
        5. Warn if P50 > 200ms
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_latency_under_load")

    @pytest.mark.slow
    def test_throughput(self):
        """
        Test that cluster can handle 1000+ requests per second.

        TODO: Implement:
        1. Use load testing tool (k6, locust, or custom script)
        2. Ramp up to 1000 RPS
        3. Sustain for 2 minutes
        4. Assert error rate < 1%
        5. Assert P99 latency < 1000ms
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_throughput")


# ============================================================================
# MONITORING TESTS
# ============================================================================

class TestMonitoring:
    """Tests for monitoring and observability."""

    def test_prometheus_scraping(self):
        """
        Test that Prometheus is scraping metrics from pods.

        TODO: Implement:
        1. Port-forward to Prometheus
        2. Query Prometheus API: /api/v1/targets
        3. Find targets matching "ml-serving/model-api"
        4. Assert targets are "up"
        5. Assert last scrape was recent (< 60s ago)
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_prometheus_scraping")

    def test_metrics_available(self):
        """
        Test that expected metrics are available in Prometheus.

        TODO: Implement:
        1. Port-forward to Prometheus
        2. Query Prometheus API for each metric:
           - model_api_requests_total
           - model_api_request_duration_seconds
           - model_api_predictions_total
        3. Assert metrics exist and have recent data
        """
        # TODO: Implement test
        pytest.skip("TODO: Implement test_metrics_available")


# ============================================================================
# RUNNING TESTS
# ============================================================================

if __name__ == "__main__":
    """
    Run tests from command line.

    Usage:
        # Run all tests
        python test_k8s.py

        # Run with pytest (recommended)
        pytest test_k8s.py

        # Run specific test class
        pytest test_k8s.py::TestDeployment

        # Run specific test
        pytest test_k8s.py::TestDeployment::test_deployment_exists

        # Run with verbose output
        pytest test_k8s.py -v

        # Run and show print statements
        pytest test_k8s.py -s

        # Skip slow tests
        pytest test_k8s.py -m "not slow"

        # Run only slow tests
        pytest test_k8s.py -m slow
    """
    pytest.main([__file__, "-v"])


# ============================================================================
# LEARNING NOTES
# ============================================================================

"""
Testing Kubernetes Deployments: Best Practices

1. TEST PYRAMID FOR KUBERNETES
   - Unit Tests: Test individual functions (app logic)
   - Integration Tests: Test k8s resources (these tests)
   - E2E Tests: Test entire workflow (user perspective)

2. TEST CATEGORIES
   - Static: Configuration correctness (replicas, limits)
   - Dynamic: Runtime behavior (health checks, scaling)
   - Performance: Latency, throughput, resource usage

3. WHEN TO RUN TESTS
   - Pre-deployment: CI pipeline
   - Post-deployment: Smoke tests
   - Periodic: Continuous validation (chaos engineering)

4. TOOLS
   - pytest: Test framework
   - kubernetes Python client: Programmatic k8s access
   - kubectl: CLI operations
   - k6/locust: Load testing
   - conftest: Policy enforcement (OPA)

5. COMMON PITFALLS
   - Testing on local cluster only (test on real cloud!)
   - Not cleaning up resources
   - Flaky tests due to timing issues (use wait_for_condition)
   - Not testing failure scenarios (pod crashes, node failures)

6. ADVANCED TESTING
   - Chaos engineering: Intentionally cause failures
   - Security scanning: Check for vulnerabilities
   - Cost analysis: Measure resource costs
   - Compliance: Ensure policies met (PodSecurityPolicy, NetworkPolicy)

Next Steps:
- Complete all TODO tests
- Add custom tests for your specific requirements
- Integrate into CI/CD pipeline
- Set up continuous testing (every hour/day)
"""
