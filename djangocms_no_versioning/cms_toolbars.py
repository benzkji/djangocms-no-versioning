from collections import OrderedDict

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from cms.toolbar.items import ButtonList
from cms.toolbar.utils import get_object_preview_url
from cms.toolbar_pool import toolbar_pool
from cms.cms_toolbars import PlaceholderToolbar
from django.apps import apps


class NoVersioningToolbar(PlaceholderToolbar):
    class Media:
        js = ("cms/js/admin/actions.js",)

    def render_object_editable_buttons(self):
        self.init_placeholders()

        if not self.toolbar.obj:
            return

        # Edit button
        if self.toolbar.content_mode_active and self._can_add_button():
            self.add_edit_button()
        # Preview button
        if self.toolbar.edit_mode_active and self._can_add_button():
            self.add_quit_or_publish_button()
        # Structure mode
        if self._can_add_structure_mode():
            self.add_structure_mode()

    def add_quit_or_publish_button(self):
        item = ButtonList(side=self.toolbar.RIGHT)
        version = self.toolbar.obj.versions.first()
        if version.published:
            if hasattr(self.toolbar.obj, "get_absolute_url"):
                url = self.toolbar.obj.get_absolute_url()
            else:
                url = get_object_preview_url(self.toolbar.obj)
            item.add_button(
                _("Quit editing"),
                url=url,
                disabled=False,
                extra_classes=[
                    "cms-btn",
                ],
            )
        else:
            if not self._is_versioned():
                return
            # Add the publish button if in edit mode
            item = ButtonList(side=self.toolbar.RIGHT)
            proxy_model = self._get_proxy_model()
            publish_url = reverse(
                "admin:{app}_{model}_publish".format(
                    app=proxy_model._meta.app_label,
                    model=proxy_model.__name__.lower(),
                ),
                args=(version.pk,),
            )
            item.add_button(
                _("Publish"),
                url=publish_url,
                disabled=False,
                extra_classes=[
                    "cms-btn",
                    "cms-btn-action",
                    "js-action",
                    "cms-form-post-method",
                ],
            )
        self.toolbar.add_item(item)

    def _get_versionable(self):
        """Helper method to get the versionable for the content type
        of the version
        """
        versioning_extension = apps.get_app_config(
            "djangocms_no_versioning"
        ).cms_extension
        return versioning_extension.versionables_by_content[self.toolbar.obj.__class__]

    def _is_versioned(self):
        """Helper method to check if the model has been registered for
        versioning
        """
        versioning_extension = apps.get_app_config(
            "djangocms_no_versioning"
        ).cms_extension
        return versioning_extension.is_content_model_versioned(
            self.toolbar.obj.__class__
        )

    def _get_proxy_model(self):
        """Helper method to get the proxy model class for the content
        model class
        """
        return self._get_versionable().version_model_proxy


def replace_toolbar(old, new):
    """Replace `old` toolbar class with `new` class,
    while keeping its position in toolbar_pool.
    """
    new_name = ".".join((new.__module__, new.__name__))
    old_name = ".".join((old.__module__, old.__name__))
    toolbar_pool.toolbars = OrderedDict(
        (new_name, new) if name == old_name else (name, toolbar)
        for name, toolbar in toolbar_pool.toolbars.items()
    )


replace_toolbar(PlaceholderToolbar, NoVersioningToolbar)
