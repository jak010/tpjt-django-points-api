from django.urls import path

from src.apps.views.v1 import point_view

urlpatterns = [
    path('earn', view=point_view.PointEarnView.as_view(), name="point-earn-view"),
]
