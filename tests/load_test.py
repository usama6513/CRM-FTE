"""
Load Testing Script for Customer Success FTE
Uses Locust to simulate high traffic loads
"""

from locust import HttpUser, task, between
import random


class WebFormUser(HttpUser):
    """Simulate users submitting support forms."""
    wait_time = between(2, 10)
    weight = 3  # Web form is most common

    @task
    def submit_support_form(self):
        categories = ['general', 'technical', 'billing', 'feedback', 'bug_report']

        self.client.post("/support/submit", json={
            "name": f"Load Test User {random.randint(1, 10000)}",
            "email": f"loadtest{random.randint(1, 10000)}@example.com",
            "subject": f"Load Test Query {random.randint(1, 100)}",
            "category": random.choice(categories),
            "message": "This is a load test message to verify system performance under stress."
        })


class HealthCheckUser(HttpUser):
    """Monitor system health during load test."""
    wait_time = between(5, 15)
    weight = 1

    @task
    def check_health(self):
        self.client.get("/health")

    @task
    def check_metrics(self):
        self.client.get("/metrics/channels")


# Additional task for API endpoint testing
class APIUser(HttpUser):
    """Test other API endpoints under load."""
    wait_time = between(10, 20)
    weight = 1

    @task
    def get_agent_status(self):
        self.client.get("/agent/status")

    @task
    def get_config(self):
        self.client.get("/config")


# Example scenario with mixed traffic
class MixedUser(HttpUser):
    """Simulate mixed traffic patterns."""
    wait_time = between(3, 8)
    weight = 2

    @task(5)  # More frequent
    def submit_support_form(self):
        self.client.post("/support/submit", json={
            "name": f"Mixed Test User {random.randint(1, 1000)}",
            "email": f"mixedtest{random.randint(1, 1000)}@example.com",
            "subject": "Mixed Traffic Test",
            "category": random.choice(['general', 'technical']),
            "message": "Testing with mixed traffic pattern."
        })

    @task(1)  # Less frequent
    def check_health(self):
        self.client.get("/health")

    @task(1)  # Less frequent
    def check_agent_status(self):
        self.client.get("/agent/status")


if __name__ == "__main__":
    print("Load test script ready. Run with: locust -f tests/load_test.py")