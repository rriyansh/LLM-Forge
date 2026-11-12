"""Locust load test. Run: locust -f tests/load/locustfile.py --host http://localhost:8000"""
import os
import random

from locust import HttpUser, between, task

API_KEY = os.getenv("API_KEY", "a" * 40)


class LLMUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(3)
    def generate(self):
        self.client.post(
            "/generate",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"prompt": f"Explain concept {random.randint(1, 1000)}", "max_tokens": 64},
        )

    @task(1)
    def health(self):
        self.client.get("/health/live")
