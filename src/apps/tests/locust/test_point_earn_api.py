from locust import HttpUser, task, between


class PointEarnUser(HttpUser):
    wait_time = between(1, 3)  # 각 요청 사이의 대기 시간 (1~3초)

    @task
    def earn_point(self):
        payload = {
            "user_id": 100,
            "amount": 100,
            "description": "string"
        }
        self.client.post("/api/v1/points/earn", json=payload)
