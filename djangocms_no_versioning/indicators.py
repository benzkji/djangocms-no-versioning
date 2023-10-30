from cms.utils.urlutils import admin_reverse
from django.contrib.auth import get_permission_codename
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _

from .constants import PUBLISHED, UNPUBLISHED, VERSION_STATES
from .models import Version


"""
indicators: the admin column with a circle in it, indicating the status of the versionable object 
"""


def _reverse_action(version, action, back=None):
    get_params = f"?{urlencode({'back': back})}" if back else ""
    return (
        admin_reverse(
            f"{version._meta.app_label}_{version.versionable.version_model_proxy._meta.model_name}_{action}",
            args=(version.pk,),
        )
        + get_params
    )


def content_indicator_menu(request, status, version, back=""):
    from .helpers import version_list_url

    menu = []
    if request.user.has_perm(f"cms.{get_permission_codename('change', version._meta)}"):
        if not version.published:
            menu.append(
                (
                    _("Publish"),
                    "cms-icon-publish",
                    _reverse_action(version, "publish"),
                    "js-cms-tree-lang-trigger",  # Triggers POST from the frontend
                )
            )
        if version.published:
            menu.append(
                (
                    _("Unpublish"),
                    "cms-icon-unpublish",
                    _reverse_action(version, "unpublish"),
                    "js-cms-tree-lang-trigger",
                )
            )
    return menu


def content_indicator(content_obj):
    """Translates available versions into status to be reflected by the indicator.
    Function caches the result in the page_content object"""

    if not content_obj:
        return None  # pragma: no cover
    elif not hasattr(content_obj, "_indicator_status"):
        version = Version.objects.get_for_content(content_obj)
        content_obj._version = version
        if version.published:
            content_obj._indicator_status = "published"
        else:
            content_obj._indicator_status = "unpublished"
    return content_obj._indicator_status


def is_editable(content_obj, request):
    return True
    """Check of content_obj is editable"""
    if not content_obj.content_indicator():
        # Something's wrong: content indicator not identified. Maybe no version?
        return False
    versions = content_obj._version
    return versions[0].check_modify.as_bool(request.user)
