import pytest

from src.apps.models.point import Point, PointBalance


@pytest.mark.django_db
def test_initilaized_point_model():
    """ Point Model 생성 테스트 """
    # Assert

    user_id = 1
    amount = 100.0
    type = Point.Type.EARN
    description = "Test description"
    balance_snapshot = 50.0

    # Act
    point_balance = PointBalance.initialized(user_id=user_id, balance=balance_snapshot)
    point_balance.save()

    point = Point.initilaized(
        user_id=user_id,
        amount=amount,
        type=type,
        description=description,
        balance_snapshot=balance_snapshot,
        point_balance=point_balance
    )
    point.save()

    # Arrange
    assert point.user_id == user_id
    assert point.amount == amount
    assert point.type == type.value
    assert point.description == description
    assert point.balance_snapshot == balance_snapshot
    assert point.point_balance == point_balance
