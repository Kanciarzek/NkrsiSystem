import requests
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from colorfield.fields import ColorField
from phonenumber_field.modelfields import PhoneNumberField
from nkrsiSystem import settings
from .managers import UserManager


class FAQ(models.Model):
    """
    Model przechowujący pytania służące pomocą członkom koła.
    """
    question = models.CharField(_('question'), max_length=200)
    order = models.IntegerField(_('order'), default=0,
                                help_text=_('Order in which links will be presented on home page.'
                                            ' The lower number the higher position.'))
    answer = models.TextField(_('answer'), max_length=1000)

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')

    def __str__(self):
        return self.question


class FrontLink(models.Model):
    """
    Model kart z linkami widoczny na stronie głównej. Są 2 ich typy: 'zwykłe' oraz wykorzystujące AJAX. Te pierwsze to
    linki przekierowujące na inną stronę, te drugie służą głównie obsłudze koła (np. otwarcie drzwi, uruchomienie
    projektora itp. Administrator ma możliwość zmiany koloru tła, tekstu, czy ikony pokazywanej na karcie. Ikona
    jest przechowywana jako nazwa pliku z katalogu static/icon.
    """
    url = models.CharField(_('url'), max_length=200)
    type = models.IntegerField(_('type'), choices=((1, _('withoutAJAX')), (2, _('localWithAJAX'))),
                               help_text=_('"withoutAJAX" means standard link, "localWithAJAX" means local links '
                                           'accessible using AJAX technology (currently only door opening: '
                                           '"ajax/door" and projector turning on/off: "ajax/projector")'))
    icon = models.CharField(_('icon-name'), null=True, max_length=30, blank=True,
                            help_text=_('Filename of icon from static/icon dir which will be presented on a card.'))
    bgcolor = ColorField(_('bgcolor'), default='#000000')
    textcolor = ColorField(_('textcolor'), default='#FFFFFF')
    order = models.IntegerField(_('order'), default=0,
                                help_text=_('Order in which links will be presented on home page. '
                                            'The lower number the higher position.'))
    title = models.CharField(_('title'), max_length=30, default=None)
    description = models.CharField(_('description'), max_length=100, null=True, default=None, blank=True)

    class Meta:
        verbose_name = _('front link')
        verbose_name_plural = _('front links')

    def __str__(self):
        return 'Link: ' + self.title


class User(AbstractBaseUser, PermissionsMixin):
    """
    Model członka koła. Może przechowywwać informację o imieniu, nazwisku, dacie dołączenia, numerze telefonu, stanie
    członkostwa (byciu kandydatem, w zarządzie itp.). Przyjęto założenie, że członkowie zarządu mają dostęp do panelu
    administracyjnego. Pole student_card_id oznacza numer zczytany z legitymacji studenckiej za pomocą czytnika - nie ma
    on nic wspólnego z numerem albumu.
    """
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now, null=True, editable=True)
    is_candidate = models.BooleanField(_('candidate'), default=True)
    phone = PhoneNumberField(_('phone'), blank=True, null=True)
    student_card_id = models.CharField(_('student card id'), blank=True, null=True, default=None, max_length=20,
                                       help_text=_('It is used to access Ślimak room. It is id of your student card and'
                                                   ' has nothing to do with your student id number. It can be read by a'
                                                   'device from NKRSI headquarters.'))
    function = models.CharField(_('function'), default="", blank=True, max_length=30,
                                help_text=_('Position in NKRSI. If blank it will be depended on candidate status.'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Zwraca imię i nazwisko użytkownika ze spacją pomiędzy nimi.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Zwraca imię użytkownika.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Wysyła email użytkownikowi.
        :param subject: temat widomości
        :param message: treść wiadomości
        :param from_email: adres nadawcy
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def invite_to_slack(self, request=None):
        """
        Wysyła zaproszenie do Slacka na podstawie adresu email.
        """
        result_of_add_to_slack = requests.post(settings.SLACK_API_INVITE_URL,
                                               {"token": settings.SLACK_TOKEN, "email": self.email,
                                                "first_name": self.first_name,
                                                "last_name": self.last_name})
        if not result_of_add_to_slack.json()["ok"]:
            if request is None:
                raise RuntimeError(_("Failed to send invitation. Error: ") + result_of_add_to_slack.json()['error'])
            else:
                messages.error(request,
                               _("Failed to send invitation. Error: ") + result_of_add_to_slack.json()['error'])
        elif request is not None:
            messages.info(request, _("Invitation to Slack has been sent"))


class DoorOpenLog(models.Model):
    """
    Model przechowujący logi otwierania drzwi do koła. Jako, że tylko zalogowani użytkownicy mają możliwość otwierania
    drzwi, jest powiązany bezpośrednio z modelem członka za pomocą pola User. Administrator ma możliwość jedynie
    podejrzenia logów w panelu administracyjnym - nie ma możliwości ich modyfikacji.
    """
    date = models.DateTimeField(_('request date'), default=timezone.now, editable=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    succeeded = models.BooleanField(_('succeeded'))

    def __str__(self):
        return _('Door open request') + ': ' + self.user.get_full_name()

    class Meta:
        verbose_name = _('door open request')
        verbose_name_plural = _('door open requests')
