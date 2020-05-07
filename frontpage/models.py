from django.db import models
from django.utils.translation import ugettext_lazy as _

#
# class FrontPage(models.Model):
#     order = models.IntegerField(_('order'), default=0,
#                                 help_text=_('Order in which links will be presented on home page. '
#                                             'The lower number the higher position.'))
#     title = models.CharField(_('title'), max_length=200)
#
#     class Meta:
#         verbose_name = _('front subpage')
#         verbose_name_plural = _('front subpages')
