# core/models.py
from django.db import models


class PubdateModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        # Это абстрактная модель:
        abstract = True


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        # Это абстрактная модель:
        abstract = True
