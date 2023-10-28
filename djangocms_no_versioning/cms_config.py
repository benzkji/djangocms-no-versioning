from cms.app_base import CMSAppExtension, CMSAppConfig
from cms.models import PageContent
from cms.utils.i18n import get_language_tuple
from django.conf import settings
from django.contrib.admin.utils import flatten_fieldsets
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import get_language_from_request

from djangocms_no_versioning import versionables, indicators
from djangocms_no_versioning.admin import VersioningAdminMixin
from djangocms_no_versioning.datastructures import VersionableItem
from djangocms_no_versioning.helpers import (
    replace_admin_for_models,
    register_versionadmin_proxy,
    inject_generic_relation_to_version,
    replace_manager,
)
from djangocms_no_versioning.manager import (
    PublishedContentManagerMixin,
    AdminManagerMixin,
)
from djangocms_no_versioning.models import Version

"""
PublisherExtension: Check for all cms apps that could support versioning, if yes do
the necessary configuration for our non versioning (changelist/admin, toolbar, queryset)

CMSAppConfig: Implement versioning for core cms models
"""


class PublisherExtension(CMSAppExtension):
    def __init__(self):
        self.publishables = []

    def handle_admin_classes(self, cms_config):
        """Replaces admin model classes for all registered content types
        with an admin model class that inherits from `versionable.content_admin_mixin`.
        """
        replace_admin_for_models(
            [
                (versionable.content_model, versionable.content_admin_mixin)
                for versionable in cms_config.versioning
            ]
        )

    def handle_version_admin(self, cms_config):
        """
        Registers version admin for all registered content types
        with filtering by content type applied, so only versions for
        that specific content type are shown.
        """
        for versionable in cms_config.versioning:
            if versionable.concrete:
                register_versionadmin_proxy(versionable)

    def handle_content_model_generic_relation(self, cms_config):
        """Adds `versions` GenericRelation field to all provided
        content models.
        """
        for versionable in cms_config.versioning:
            inject_generic_relation_to_version(versionable.content_model)

    def handle_content_model_manager(self, cms_config):
        """Replaces default manager in provided content models with
        one inheriting from PublishedContentManagerMixin.
        """
        for versionable in cms_config.versioning:
            replace_manager(
                versionable.content_model, "objects", PublishedContentManagerMixin
            )
            replace_manager(
                versionable.content_model,
                "admin_manager",
                AdminManagerMixin,
                _group_by_key=list(versionable.grouping_fields),
            )

    def configure_app(self, cms_config):
        if hasattr(cms_config, "extended_admin_field_modifiers"):
            self.handle_admin_field_modifiers(cms_config)

        # Validation to ensure either the versioning or the
        # versioning_add_to_confirmation_context config has been defined
        has_extra_context = hasattr(
            cms_config, "versioning_add_to_confirmation_context"
        )
        has_models_to_register = hasattr(cms_config, "versioning")
        if not has_extra_context and not has_models_to_register:
            raise ImproperlyConfigured(
                "The versioning or versioning_add_to_confirmation_context setting must be defined"
            )
        if has_models_to_register:
            self.handle_versioning_setting(cms_config)
            self.handle_admin_classes(cms_config)
            self.handle_version_admin(cms_config)
            self.handle_content_model_generic_relation(cms_config)
            self.handle_content_model_manager(cms_config)


class VersioningCMSPageAdminMixin(VersioningAdminMixin):
    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj:
            version = Version.objects.get_for_content(obj)
            if not version.check_modify.as_bool(request.user):
                form = self.get_form_class(request)
                if form.fieldsets:
                    fields = flatten_fieldsets(form.fieldsets)
                fields = list(fields)
                for f_name in ["slug", "overwrite_url"]:
                    fields.remove(f_name)
        return fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            version = Version.objects.get_for_content(obj)
            if not version.check_modify.as_bool(request.user):
                for f_name in ["slug", "overwrite_url"]:
                    form.declared_fields[f_name].widget.attrs["readonly"] = True
        return form

    def get_queryset(self, request):
        urls = ("cms_pagecontent_get_tree",)
        queryset = super().get_queryset(request)
        if request.resolver_match.url_name in urls:
            versionable = versionables.for_content(queryset.model)

            # TODO: Improve the grouping filters to use anything defined in the
            #       apps versioning config extra_grouping_fields
            grouping_filters = {}
            if "language" in versionable.extra_grouping_fields:
                grouping_filters["language"] = get_language_from_request(request)

            return queryset.filter(
                pk__in=versionable.distinct_groupers(**grouping_filters)
            )
        return queryset

    # CAVEAT:
    #   - PageContent contains the template, this can differ for each language,
    #     it is assumed that templates would be the same when copying from one language to another
    # FIXME: The long term solution will require knowing:
    #           - why this view is an ajax call
    #           - where it should live going forwards (cms vs versioning)
    #           - A better way of making the feature extensible / modifiable for versioning
    def copy_language(self, request, object_id):
        target_language = request.POST.get("target_language")

        # CAVEAT: Avoiding self.get_object because it sets the page cache,
        #         We don't want a draft showing to a regular site visitor!
        #         source_page_content = self.get_object(request, object_id=object_id)
        source_page_content = PageContent._original_manager.get(pk=object_id)

        if source_page_content is None:
            raise self._get_404_exception(object_id)

        page = source_page_content.page

        if not target_language or target_language not in get_language_list(
            site_id=page.node.site_id
        ):
            return HttpResponseBadRequest(
                force_str(_("Language must be set to a supported language!"))
            )

        target_page_content = get_latest_admin_viewable_content(
            page, language=target_language
        )

        # First check that we are able to edit the target
        if not self.has_change_permission(request, obj=target_page_content):
            raise PermissionDenied

        for placeholder in source_page_content.get_placeholders():
            # Try and get a matching placeholder, only if it exists
            try:
                target = target_page_content.get_placeholders().get(
                    slot=placeholder.slot
                )
            except ObjectDoesNotExist:
                continue

            plugins = placeholder.get_plugins_list(source_page_content.language)

            if not target.has_add_plugins_permission(request.user, plugins):
                return HttpResponseForbidden(
                    force_str(_("You do not have permission to copy these plugins."))
                )
            copy_plugins_to_placeholder(plugins, target, language=target_language)
        return HttpResponse("ok")

    def change_innavigation(self, request, object_id):
        page_content = self.get_object(request, object_id=object_id)
        version = Version.objects.get_for_content(page_content)
        try:
            version.check_modify(request.user)
        except ConditionFailed as e:
            # Send error message
            return HttpResponseForbidden(force_str(e))
        return super().change_innavigation(request, object_id)

    @property
    def indicator_descriptions(self):
        """Publish indicator description to CMSPageAdmin"""
        return INDICATOR_DESCRIPTIONS

    @classmethod
    def get_indicator_menu(cls, request, page_content):
        """Get the indicator menu for PageContent object taking into account the
        currently available versions"""
        menu_template = "admin/cms/page/tree/indicator_menu.html"
        status = page_content.content_indicator()
        if not status or status == "empty":  # pragma: no cover
            return super().get_indicator_menu(request, page_content)
        versions = page_content._version  # Cache from .content_indicator()
        back = (
            admin_reverse("cms_pagecontent_changelist")
            + f"?language={request.GET.get('language')}"
        )
        menu = indicators.content_indicator_menu(request, status, versions, back=back)
        return menu_template if menu else "", menu


class PublisherCMSConfig(CMSAppConfig):
    """Implement versioning for core cms models"""

    cms_enabled = True
    # TODO: where is this actually used?
    djangocms_versioning_enabled = getattr(
        settings, "VERSIONING_CMS_MODELS_ENABLED", True
    )
    versioning = [
        VersionableItem(
            content_model=PageContent,
            grouper_field_name="page",
            extra_grouping_fields=["language"],
            version_list_filter_lookups={"language": get_language_tuple},
            # copy_function=copy_page_content,
            # grouper_selector_option_label=label_from_instance,
            # on_publish=on_page_content_publish,
            # on_unpublish=on_page_content_unpublish,
            # on_draft_create=on_page_content_draft_create,
            # on_archive=on_page_content_archive,
            copy_function=None,
            grouper_selector_option_label=None,
            on_publish=None,
            on_unpublish=None,
            on_draft_create=None,
            on_archive=None,
            content_admin_mixin=VersioningCMSPageAdminMixin,
        )
    ]
    # cms_toolbar_mixin = CMSToolbarVersioningMixin
    PageContent.add_to_class("is_editable", indicators.is_editable)
    PageContent.add_to_class("content_indicator", indicators.content_indicator)