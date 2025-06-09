from __future__ import annotations

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.settings.local')

django.setup()

from model_bakery import baker

# 특정 필드는 지정 가능
points = baker.make('apps.Point', _quantity=10)
points = baker.make('apps.PointBalance', _quantity=10)

print(points)
