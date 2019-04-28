from django.db import models
from django.db.models.manager import Manager
import datetime
from django.utils.translation import gettext as _


class Faq(models.Model):
    title = models.CharField(max_length=250, verbose_name=_('faq title'))
    description = models.CharField(max_length=250, verbose_name=_('faq description'))
    is_published = models.BooleanField(default=True, verbose_name=_('is published'))
    position = models.SmallIntegerField(default=0, verbose_name=_('position'))

    objects = models.Manager()

    class Meta:
        ordering = ['position']
        verbose_name = _('faq')
        verbose_name_plural = _('faqs')

    def __str__(self):
        return self.title

class Item(models.Model):
    faq = models.ForeignKey(Faq, related_name='items', on_delete=models.CASCADE)
    value = models.CharField(max_length=250, verbose_name=_('value'))
    position = models.SmallIntegerField(default=0, verbose_name=_('position'))

    class Meta:
        verbose_name = _('items')
        verbose_name_plural = _('items')
        ordering = ['position']

    def __str__(self):
        return u'%s' % (self.value,)
