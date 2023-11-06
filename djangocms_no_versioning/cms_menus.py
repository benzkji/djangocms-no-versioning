from cms import constants as cms_constants
from cms.apphook_pool import apphook_pool
from cms.cms_menus import (
    CMSMenu as OriginalCMSMenu,
    get_visible_nodes,
    CMSNavigationNode,
    get_menu_node_for_page,
)
from cms.models import Page
from cms.toolbar.utils import (
    get_object_preview_url,
    get_toolbar_from_request,
    get_object_edit_url,
)
from cms.utils.page import get_page_queryset
from django.apps import apps
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool


class CMSVersionedNavigationNode(NavigationNode):
    def is_selected(self, request):
        try:
            page_id = request.current_page.pk
        except AttributeError:
            return False
        return page_id == self.id


def _get_attrs_for_node(renderer, page_content):
    page = page_content.page
    language = renderer.request_language
    attr = {
        "is_page": True,
        "soft_root": page_content.soft_root,
        "auth_required": page.login_required,
        "reverse_id": page.reverse_id,
    }
    limit_visibility_in_menu = page_content.limit_visibility_in_menu

    if limit_visibility_in_menu is cms_constants.VISIBILITY_ALL:
        attr["visible_for_authenticated"] = True
        attr["visible_for_anonymous"] = True
    else:
        attr["visible_for_authenticated"] = (
            limit_visibility_in_menu == cms_constants.VISIBILITY_USERS
        )
        attr["visible_for_anonymous"] = (
            limit_visibility_in_menu == cms_constants.VISIBILITY_ANONYMOUS
        )

    attr["is_home"] = page.is_home
    extenders = []

    if page.navigation_extenders:
        if page.navigation_extenders in renderer.menus:
            extenders.append(page.navigation_extenders)
        elif f"{page.navigation_extenders}:{page.pk}" in renderer.menus:
            extenders.append(f"{page.navigation_extenders}:{page.pk}")

    if page.application_urls:
        app = apphook_pool.get_apphook(page.application_urls)

        if app:
            extenders += app.get_menus(page, language)

    exts = []

    for ext in extenders:
        if hasattr(ext, "get_instances"):
            exts.append(f"{ext.__name__}:{page.pk}")
        elif hasattr(ext, "__name__"):
            exts.append(ext.__name__)
        else:
            exts.append(ext)

    if exts:
        attr["navigation_extenders"] = exts

    attr["redirect_url"] = page_content.redirect

    return attr


class CMSMenu(Menu):
    def get_nodes(self, request):
        site = self.renderer.site
        language = self.renderer.request_language
        pages_qs = get_page_queryset(site).select_related("node")
        visible_pages_for_user = get_visible_nodes(request, pages_qs, site)

        if not visible_pages_for_user:
            return []

        cms_extension = apps.get_app_config("djangocms_no_versioning").cms_extension
        toolbar = get_toolbar_from_request(request)
        is_edit_mode = toolbar.edit_mode_active
        menu_nodes = []
        node_id_to_page = {}
        homepage_content = None

        # Depending on the toolbar mode, we need to get the correct version.
        if is_edit_mode:
            published_filter = {}
        else:
            published_filter = {"versions__published": True}

        versionable_item = cms_extension.versionables_by_grouper[Page]
        versioned_page_contents = (
            versionable_item.content_model._base_manager.filter(
                language=language,
                page__in=pages_qs,
                **published_filter,
            )
            .order_by("page__node__path")
            .select_related("page", "page__node")
            .prefetch_related("versions")
        )
        added_pages = []

        for page_content in versioned_page_contents:
            page = page_content.page

            if page not in visible_pages_for_user:
                # The page is restricted for the user.
                # Therefore we avoid adding it to the menu.
                continue

            page_tree_node = page.node
            parent_id = node_id_to_page.get(page_tree_node.parent_id)

            if page_tree_node.parent_id and not parent_id:
                # If the parent page is not available,
                # we skip adding the menu node.
                continue

            # Construct the url based on the toolbar mode.
            if is_edit_mode:
                url = get_object_edit_url(page_content)
            else:
                url = page_content.get_absolute_url()

            # Create the new navigation node.
            # why not?! ARF, fallbacks new_node = get_menu_node_for_page(self.renderer, page, language)
            new_node = CMSVersionedNavigationNode(
                id=page.pk,
                attr=_get_attrs_for_node(self.renderer, page_content),
                title=page_content.menu_title or page_content.title,
                url=url,
                visible=page_content.in_navigation,
            )

            if not homepage_content:
                # Set the home page content.
                homepage_content = page_content if page.is_home else None

            cut_homepage = homepage_content and not homepage_content.in_navigation

            if cut_homepage and parent_id == homepage_content.page.pk:
                # When the homepage is hidden from navigation,
                # we need to cut all its direct children from it.
                new_node.parent_id = None
            else:
                new_node.parent_id = parent_id

            node_id_to_page[page_tree_node.pk] = page.pk
            menu_nodes.append(new_node)
            added_pages.append(page.pk)
        return menu_nodes


# Remove the core djangoCMS CMSMenu and register the new CMSVersionedMenu.
menu_pool.menus.pop(OriginalCMSMenu.__name__)
menu_pool.register_menu(CMSMenu)
