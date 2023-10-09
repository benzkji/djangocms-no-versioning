from cms.models import CMSPlugin
from django.db import models


class TestPluginModel(CMSPlugin):
    field1 = models.CharField(max_length=64, default='', blank=False)
    field_date = models.DateField(default=None, null=True, )
    field_datetime = models.DateTimeField(default=None, null=True, )
    field_time = models.TimeField(default=None, null=True, )

    def __str__(self):
        return self.field1
