from django.utils.translation import gettext_lazy as _

"""publishing states"""
PUBLISHED = "published"
UNPUBLISHED = "unpublished"

VERSION_STATES = (
    (PUBLISHED, _("Published")),
    (UNPUBLISHED, _("Unpublished")),
)
OPERATION_PUBLISH = "operation_publish"
OPERATION_UNPUBLISH = "operation_unpublish"

INDICATOR_DESCRIPTIONS = {
    "published": _("Published"),
    "unpublished": _("Unpublished"),
}
