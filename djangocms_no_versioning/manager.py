import warnings
from copy import copy

from django.contrib.auth import get_user_model
from django.db import models

from . import constants
from .constants import PUBLISHED
from .models import Version


class PublishedContentManagerMixin:
    """Manager mixin used for overriding the managers of content models"""

    versioning_enabled = True

    def get_queryset(self):
        """Limit query to published content"""
        qs = super().get_queryset()
        # TODO: when is versioning_enabled False?
        if not self.versioning_enabled:
            return qs
        qs = qs.filter(versions__published=True)
        return qs

    def create(self, *args, **kwargs):
        obj = super().create(*args, **kwargs)
        Version.objects.create(content=obj)
        return obj

    def with_user(self, user):
        new_manager = copy(self)
        return new_manager


class AdminQuerySetMixin:
    def _chain(self):
        # Also clone group by key when chaining querysets!
        clone = super()._chain()
        clone._group_by_key = self._group_by_key
        return clone

    def current_content_iterator(self, **kwargs):
        """Returns generator (not a queryset) over current content versions. Current versions are either draft
        versions or published versions (in that order)"""
        warnings.warn(
            "current_content_iterator is deprecated in favour of current_conent",
            DeprecationWarning,
            stacklevel=2,
        )
        return iter(self.current_content(**kwargs))

    def current_content(self, **kwargs):
        """Returns a queryset current content versions. Current versions are either draft
        versions or published versions (in that order). This optimized query assumes that
        draft versions always have a higher pk than any other version type. This is true as long as
        no other version type can be converted to draft without creating a new version.
        """
        qs = self.filter(**kwargs)
        return qs

    def latest_content(self, **kwargs):
        """Returns the "latest" content object which is in this order
           1. a draft version (should it exist)
           2. a published version (should it exist)
           3. any other version with the highest pk

        This filter assumes that there can only be one draft created and that the draft as
        the highest pk of all versions (should it exist).
        """
        return self.current_content(**kwargs)


class AdminManagerMixin:
    versioning_enabled = True
    _group_by_key = []

    def get_queryset(self):
        qs_class = super().get_queryset().__class__
        if not self._group_by_key:
            # Not initialized (e.g. by using content_set(manager="admin_manager"))?
            # Get grouping fields from versionable
            from . import versionables

            versionable = versionables.for_content(self.model)
            self._group_by_key = list(versionable.grouping_fields)
        qs = type(
            f"Admin{qs_class.__name__}",
            (AdminQuerySetMixin, qs_class),
            {"_group_by_key": self._group_by_key},  # Pass grouping fields to queryset
        )(self.model, using=self._db)
        return qs

    def current_content(self, **kwargs):  # pragma: no cover
        """Syntactic sugar: admin_manager.current_content()"""
        return self.get_queryset().current_content(**kwargs)

    def latest_content(self, **kwargs):  # pragma: no cover
        """Syntactic sugar: admin_manager.latest_content()"""
        return self.get_queryset().latest_content(**kwargs)
