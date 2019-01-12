import json
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.http import JsonResponse
from django.shortcuts import render, redirect
from pypjlink import Projector
from requests import ConnectTimeout
from nkrsiSystem import settings
from usersystem.forms import EditProfileForm
from .models import FrontLink, FAQ, User, DoorOpenLog


@login_required
def index(request):
    front_link = FrontLink.objects.order_by('order')
    return render(request, 'main.html', {'links': front_link})


@login_required()
def door(request):
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


@login_required()
def projector(request):
    try:
        p = Projector.from_address(settings.PROJECTOR_IP)
        p.authenticate()
        if p.get_power() == 'on':
            p.set_power('off')
        elif p.get_power() == 'off':
            p.set_power('on')
        return JsonResponse({'ok': True})
    except TimeoutError:
        return JsonResponse({'ok': False})


@login_required()
def faq(request):
    questions = FAQ.objects.all()
    return render(request, 'faq/faq.html', {'questions': questions})


@login_required()
def view_user(request):
    pass


@login_required()
def edit_user(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/account/me')
    form = EditProfileForm(instance=request.user)
    return render(request, 'user/user.html', {'form': form})


def is_student_card_id_in_db(request):
    data = json.loads(request.body)
    users = User.objects.filter(student_card_id=data.get('card_id', 0))
    if len(users) == 0:
        return JsonResponse({'ok': False}, status=404)
    else:
        return JsonResponse({'ok': True})
