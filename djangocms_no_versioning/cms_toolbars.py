from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from cms.toolbar.items import ButtonList
from cms.toolbar_pool import toolbar_pool
from cms.cms_toolbars import PlaceholderToolbar


class NoVersioningToolbar(PlaceholderToolbar):
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
        if self.toolbar.obj.versions.first().published:
            url = self.toolbar.obj.get_absolute_url()
            item.add_button(
                _("Quit editing"),
                url=url,
                disabled=False,
                extra_classes=[
                    "cms-btn",
                ],
            )
        else:
            url = self.toolbar.obj.get_absolute_url()
            item.add_button(
                _("Publish"),
                url=url,
                disabled=False,
                extra_classes=[
                    "cms-btn",
                    "cms-btn-action",
                ],
            )
        self.toolbar.add_item(item)


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
