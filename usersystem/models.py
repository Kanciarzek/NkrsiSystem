import requests
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from colorfield.fields import ColorField
from nkrsiSystem import settings
from .managers import UserManager


class FrontLink(models.Model):
    url = models.CharField(_('url'), max_length=200)
    type = models.IntegerField(_('type'), choices=((0, 'remote'), (1, 'local'), (2, 'localWithAJAX')))
    icon = models.CharField(_('icon-name'), null=True, max_length=30)
    bgcolor = ColorField(_('bgcolor'), default='#FFFFFF')
    textcolor = ColorField(_('textcolor'), default='#000000')
    order = models.IntegerField(_('order'), default=0)
    title = models.CharField(_('title'), max_length=30, default=None)
    description = models.CharField(_('description'), max_length=100, null=True, default=None)

    class Meta:
        verbose_name = _('front link')
        verbose_name_plural = _('front links')

    def __str__(self):
        return 'Link: ' + self.title


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True, null=True, editable=True)
    is_candidate = models.BooleanField(_('candidate'), default=True)
    phone = models.IntegerField(_('phone number'), blank=True, null=True, default=None)
    student_card_id = models.IntegerField(_('student card id'), blank=True, null=True, default=None)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def invite_to_slack(self, request=None):
        """
        Sends an invitation to slack based on the user email.
        """
        result_of_add_to_slack = requests.post(settings.SLACK_API_INVITE_URL,
                                               {"token": settings.SLACK_TOKEN, "email": self.email,
                                                "first_name": self.first_name,
                                                "last_name": self.last_name})
        if not result_of_add_to_slack.json()["ok"]:
            if request is None:
                raise RuntimeError("Failed to send invitation. Error: " + result_of_add_to_slack.json()['error'])
            else:
                messages.error(request, "Failed to send invitation. Error: " + result_of_add_to_slack.json()['error'])