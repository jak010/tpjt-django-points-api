from locust import FastHttpUser, task, HttpUser


class PointEarnUser(FastHttpUser):

    max_retries = 3


    @task
    def earn_point(self):
        payload = {
            "user_id": 100,
            "amount": 10000,
            "description": "string"
        }
        self.client.post(
            "/api/v1/points/earn",
            json=payload,
        )

