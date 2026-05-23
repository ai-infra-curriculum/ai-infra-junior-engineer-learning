"""Locust load test for the Project 02 model serving API.

Usage
-----
Run a smoke test from your laptop:

    pip install 'locust>=2.20'
    locust -f loadtest/locustfile.py --host https://model-api.example.com

Run headless with explicit load shape:

    locust -f loadtest/locustfile.py \\
        --host https://model-api.example.com \\
        --headless --users 200 --spawn-rate 10 \\
        --run-time 5m --csv loadtest/results/run1

The accompanying README documents test plans (smoke, ramp, soak, spike) and the
results structure stored under ``loadtest/results/``.
"""
from __future__ import annotations

import os
import random
from locust import HttpUser, between, events, task


FEATURE_COUNT = int(os.getenv("FEATURE_COUNT", "10"))
MODEL_VERSIONS = os.getenv("MODEL_VERSIONS", "latest").split(",")


def random_features() -> list[float]:
    """Return a feature vector shaped like real production traffic."""
    return [round(random.gauss(0.0, 1.0), 4) for _ in range(FEATURE_COUNT)]


class ModelAPIUser(HttpUser):
    wait_time = between(0.05, 0.30)

    @task(10)
    def predict(self) -> None:
        payload = {
            "features": random_features(),
            "model_version": random.choice(MODEL_VERSIONS),
        }
        with self.client.post(
            "/v1/predict",
            json=payload,
            name="POST /v1/predict",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"unexpected status {response.status_code}")
                return
            try:
                body = response.json()
            except ValueError:
                response.failure("response body was not JSON")
                return
            if "prediction" not in body:
                response.failure("missing 'prediction' in response")

    @task(2)
    def predict_batch(self) -> None:
        payload = {
            "items": [
                {"features": random_features()} for _ in range(8)
            ]
        }
        self.client.post("/v1/predict/batch", json=payload, name="POST /v1/predict/batch")

    @task(1)
    def health(self) -> None:
        self.client.get("/health", name="GET /health")


@events.test_start.add_listener
def _on_start(environment, **_kwargs) -> None:
    print("Load test starting — target:", environment.host)


@events.test_stop.add_listener
def _on_stop(environment, **_kwargs) -> None:
    stats = environment.stats.total
    print(
        f"Done. requests={stats.num_requests} "
        f"failures={stats.num_failures} "
        f"p95={stats.get_response_time_percentile(0.95):.1f}ms "
        f"rps={stats.current_rps:.1f}"
    )
