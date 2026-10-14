import uuid
from django.db import models

class BaseUUIDModel(models.Model):
    """
    Abstract base model that enforces UUID primary keys
    and automatic timestamp tracking across all Ralyn's models.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
