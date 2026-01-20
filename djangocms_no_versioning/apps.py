from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PublisherConfig(AppConfig):
    name = "djangocms_no_versioning"
    verbose_name = _("django CMS No Versioning")
    default_auto_field = "django.db.models.BigAutoField"
