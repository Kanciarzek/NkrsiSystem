import json

import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from pypjlink import Projector
from requests import ConnectTimeout
from django.contrib import messages
from nkrsiSystem import settings
from usersystem.forms import EditProfileForm
from .models import FrontLink, FAQ, User, DoorOpenLog
from django.utils.translation import ugettext_lazy as _


@login_required
def index(request):
    """
    Generuje widok strony głównej wraz z listą kart z linkami.
    :param request:
    :return:
    """
    front_link = FrontLink.objects.order_by('order')
    return render(request, 'main.html', {'links': front_link})


@login_required
def faq(request):
    """
    Generuje widok z 'najczęściej zadawanymi pytaniami użytkowników' w postaci listy.
    :param request:
    :return:
    """
    questions = FAQ.objects.all()
    return render(request, 'faq/faq.html', {'questions': questions})


@login_required
def view_user(request, user_id=None):
    """
    Generuje widok zawierający profil danego użytkownika.
    :param request:
    :param user_id: Id użytkownika wyświetlanego profilu. Gdy nie zostanie podane, to wyświetlany jest profil
    bieżącego użytkownika.
    :return:
    """
    if user_id is None:
        return render(request, 'user/profile.html', {'user': request.user})
    else:
        return render(request, 'user/profile.html', {'user': User.objects.get(id=user_id)})


@login_required
def edit_user(request):
    """
    Generuje formularz modyfikacji profilu członka. Gdy ten zostanie wysłany i zaakceptowany, to przekierowuje na porfil
    aktualnie zalogowanego użytkownika.
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/account/me')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'user/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """
    Generuje formularz modyfikacji profilu członka. Gdy ten zostanie wysłany i zaakceptowany, to przekierowuje na porfil
    aktualnie zalogowanego użytkownika - użytkownik i tak musi w tej sytuacji się zalogować ponownie.
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.info(request, _("Password changed"))
            # request.user.update_radius_password(form.cleaned_data['new_password1'], request)
            return redirect('/account/me')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'user/edit_profile.html', {'form': form})


@login_required
def all_users(request):
    """
    Generuje widok zawierający listę wszystkich użytkowników.
    :param request:
    :return:
    """
    users = User.objects.order_by('id')
    return render(request, 'user/user_list.html', {'users': users})


def is_student_card_id_in_db(request):
    """
    Endpoint dla aplikacji zewnętrznej przyjmujący obiekt JSON postaci:
    {
        'card_id':numer_karty_z_legitymacją_studencką
    }
    :param request:
    :return: Odpowiedź w postaci JSON w wypadku znalezienia danego id w bazie:
    {
        'ok': True
    }
    W przypadku niepowodzenia:
    {
        'ok': False
    }
    """
    data = json.loads(request.body)
    users = User.objects.filter(student_card_id=data.get('card_id', 0))
    if len(users) == 0:
        return JsonResponse({'ok': False}, status=404)
    else:
        return JsonResponse({'ok': True})


@login_required
def door(request):
    """
    Funkcja obsługująca żądanie otwarcia drzwi. Wszystkie rządania są zapisywanie jako :model:`usersystem.DoorOpenLog`
    Jeżeli w ciągu 3 sekund system kołowy nie dostanie odpowiedzi od sterownika kontrolującego zamek w drzwiach, to
    operacja kończy się niepowodzeniem.
    :param request:
    :return: Odpowiedź w postaci JSON w wypadku powodzenia operacji:
    {
        'ok': True
    }
    W przypadku niepowodzenia:
    {
        'ok': False
    }
    """
    if request.user.is_candidate:
        return JsonResponse({'ok': False, 'reason': 'candidate'})
    log = DoorOpenLog()
    log.user = request.user
    try:
        response = requests.get(settings.DOOR_ENDPOINT, timeout=3)
    except (ConnectTimeout, requests.exceptions.ConnectionError):
        log.succeeded = False
        log.save()
        return JsonResponse({'ok': False})
    if response.status_code == 200:
        log.succeeded = True
        log.save()
        return JsonResponse({'ok': True})
    else:
        log.succeeded = False
        log.save()
        return JsonResponse({'ok': False})


@login_required
def projector(request):
    """
    Funkcja obsługująca żądanie włącznie lub wyłączenia rzutnika.
    Rzutnik może być w 3 stanach: 'on', 'off' lub 'warmup'.
    Gdy jest w stanie 'on' zostaje wysłane żądanie wyłączenia, gdy w stanie 'off' włączenia.
    :param request:
    :return: Odpowiedź w postaci JSON w wypadku powodzenia operacji:
    {
        'ok': True
    }
    W przypadku niepowodzenia:
    {
        'ok': False
    }
    """
    try:
        p = Projector.from_address(settings.PROJECTOR_IP)
        p.authenticate()
        if p.get_power() == 'on':
            p.set_power('off')
        elif p.get_power() == 'off':
            p.set_power('on')
        return JsonResponse({'ok': True})
    except (Exception, TimeoutError):
        return JsonResponse({'ok': False})


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Klasa dziedzicząca po PasswordResetConfirmView w celu modyfikacji hasła do konta radius w trakcie resetowania hasła
    przez użytkownika.
    """

    def form_valid(self, form):
        # user = form.user
        # user.update_radius_password(form.cleaned_data['new_password1'], self.request)
        return super().form_valid(form)
