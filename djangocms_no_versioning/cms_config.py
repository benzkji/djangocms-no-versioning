from cms.app_base import CMSAppExtension, CMSAppConfig
from cms.models import PageContent
from django.conf import settings


class PublisherExtension(CMSAppExtension):
    def __init__(self):
        self.publishables = []

    def configure_app(self, cms_config):
        print(cms_config)
        self.publishables.append("that's it")


class PublisherCMSConfig(CMSAppConfig):
    """Implement versioning for core cms models"""

    djangocms_publisher_enabled = getattr(
        settings, "PUBLISHER_CMS_MODELS_ENABLED", True
    )
    content_model = PageContent
    # content_admin_mixin=VersioningCMSPageAdminMixin,
    # cms_toolbar_mixin = CMSToolbarVersioningMixin
    # PageContent.add_to_class("is_published", indicators.is_editable)
