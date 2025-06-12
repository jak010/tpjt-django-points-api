from locust import HttpUser, task, between


class PointEarnUser(HttpUser):
    wait_time = between(1, 3)  # 각 요청 사이의 대기 시간 (1~3초)

    @task
    def earn_point(self):
        payload = {
            "user_id": 100,
            "amount": 10000,
            "description": "string"
        }
        self.client.post("/api/v2/points/earn", json=payload)
