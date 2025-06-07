import json

import pytest
from rest_framework.test import APIRequestFactory, APIClient


@pytest.mark.django_db
class TestPointEarniew:

    def setup_class(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()

        self.request_url = '/api/v1/points/earn'

    def test_point_earn_view(self):
        """ 적림금 조회 API 테스트 """

        # Arrange
        data = {
            "user_id": 1,
            "amount": 1000,
            "description": "test"
        }

        # Act
        response = self.client.post(
            self.request_url,
            content_type="application/json",
            data=json.dumps(data)
        )

        # Assert
        assert response.status_code == 200
