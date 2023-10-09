from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class PublishingState(models.Model):
    # the publishing state enabled model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="cms_publishing_state",
    )
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey("content_type", "object_id")
    # the publishing state
    published = models.BooleanField(default=False)
