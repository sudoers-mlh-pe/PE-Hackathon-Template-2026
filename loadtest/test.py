from locust import HttpUser, task, between

class ShortenUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def shorten_url(self):
        self.client.post(
            "/shorten",
            json={"url": "https://www.google.com"},
            headers={"Content-Type": "application/json"}
        )