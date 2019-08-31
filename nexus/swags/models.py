# -*- coding: utf-8 -*-
# Third Party Stuff
from django.db import models
from django.utils.translation import ugettext_lazy as _

# nexus Stuff
from nexus.base.models import ImageMixin, TimeStampedUUIDModel


class Swag(ImageMixin, TimeStampedUUIDModel):
    item = models.ForeignKey('SwagItem', on_delete=models.CASCADE, verbose_name=_('Item'), null=False, blank=False)
    users = models.ManyToManyField('users.User', through='SwagOwnership')
    description = models.TextField(verbose_name=_('Description'), null=False, blank=False)

    class Meta:
        verbose_name = _('Swag')
        verbose_name_plural = _('Swags')
        db_table = 'swags'

    def __str__(self):
        return self.item.name


class SwagItem(TimeStampedUUIDModel):
    name = models.CharField(_('Name'), max_length=50, null=False, blank=False)

    class Meta:
        verbose_name = _('Swag item')
        verbose_name_plural = _('Swag items')
        db_table = 'swag_items'

    def __str__(self):
        return self.name


class SwagOwnership(TimeStampedUUIDModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name=_('User'), null=False, blank=False)
    swag = models.ForeignKey('Swag', on_delete=models.CASCADE, verbose_name=_('Swag'), null=False, blank=False)

    class Meta:
        verbose_name = _('Swag ownership')
        verbose_name_plural = _('Swag ownerships')
        db_table = 'swag_ownerships'

    def __str__(self):
        return f'{self.user}{self.swag}'
