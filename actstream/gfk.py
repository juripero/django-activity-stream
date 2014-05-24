from django.db.models import Manager
from django.db.models.query import QuerySet, EmptyQuerySet

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

from actstream.compat import smart_text
from actstream import settings


class GFKManager(Manager):
    """
    A manager that returns a GFKQuerySet instead of a regular QuerySet.

    """
    def get_query_set(self):
        return GFKQuerySet(self.model)
    get_queryset = get_query_set

    def none(self):
        return self.get_queryset().none()


class GFKQuerySet(QuerySet):
    """
    A QuerySet with a fetch_generic_relations() method to bulk fetch
    all generic related items.  Similar to select_related(), but for
    generic foreign keys. This wraps QuerySet.prefetch_related.
    """
    def fetch_generic_relations(self, *args):
        qs = self._clone()

        if not settings.FETCH_RELATIONS:
            return qs

        gfk_fields = [g for g in self.model._meta.virtual_fields
                      if isinstance(g, GenericForeignKey)]

        if args:
            gfk_fields = [g for g in gfk_fields if g.name in args]

        return qs.prefetch_related(*[g.name for g in gfk_fields])

    def none(self):
        clone = self._clone(klass=EmptyGFKQuerySet)
        if hasattr(clone.query, 'set_empty'):
            clone.query.set_empty()
        return clone


class EmptyGFKQuerySet(GFKQuerySet, EmptyQuerySet):
    def fetch_generic_relations(self, *args):
        return self
