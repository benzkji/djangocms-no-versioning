from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from djangocms_no_versioning import versionables


class VersionQuerySet(models.QuerySet):
    def get_for_content(self, content_object):
        """Returns Version object corresponding to provided content object"""
        if hasattr(content_object, "_version_cache"):
            return content_object._version_cache
        versionable = versionables.for_content(content_object)
        version = self.get(
            object_id=content_object.pk, content_type__in=versionable.content_types
        )
        content_object._version_cache = version
        return version

    def filter_by_grouper(self, grouper_object):
        """Returns a list of Version objects for the provided grouper
        object
        """
        versionable = versionables.for_grouper(grouper_object)
        return self.filter_by_grouping_values(
            versionable, **{versionable.grouper_field_name: grouper_object}
        )

    def filter_by_grouping_values(self, versionable, **kwargs):
        """Returns a list of Version objects for the provided grouping
        values (unique grouper version list)
        """
        content_objects = versionable.for_grouping_values(**kwargs)
        return self.filter(
            object_id__in=content_objects, content_type__in=versionable.content_types
        )

    def filter_by_content_grouping_values(self, content):
        """Returns a list of Version objects for grouping values taken
        from provided content object. In other words:
        it uses the content instance property values as filter parameters
        """
        versionable = versionables.for_content(content)
        content_objects = versionable.for_content_grouping_values(content)
        return self.filter(
            object_id__in=content_objects, content_type__in=versionable.content_types
        )


class Version(models.Model):
    # the publishing state enabled model, as generic foreign key
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey("content_type", "object_id")
    # the publishing state
    published = models.BooleanField(default=False)

    objects = VersionQuerySet.as_manager()

    class Meta:
        unique_together = ("content_type", "object_id")

    def __str__(self):
        return f"Version #{self.pk}"

    @property
    def versionable(self):
        """Helper property to get the versionable for the content type
        of the version
        """
        return versionables.for_content(self.content)
