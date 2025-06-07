from django.urls import path

from src.apps.views.v1 import point_view

urlpatterns = [
    path('earn', view=point_view.PointEarnView.as_view(), name="point-earn-view"),
    path('use', view=point_view.PointUseView.as_view(), name="point-use-view"),
    path('<int:point_id>/cancel', view=point_view.PointCancelView.as_view(), name="point-cancel-view"),
]
