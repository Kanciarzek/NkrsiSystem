from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from pypjlink import Projector
from requests import ConnectTimeout

from nkrsiSystem import settings
from .models import FrontLink
import requests


@login_required
def index(request):
    front_link = FrontLink.objects.order_by('order')
    return render(request, 'main.html', {'links': front_link})


@login_required()
def door(request):
    try:
        response = requests.get(settings.DOOR_ENDPOINT, timeout=3)
    except (ConnectTimeout, requests.exceptions.ConnectionError):
        return JsonResponse({'ok': False})
    if response.status_code == 200:
        return JsonResponse({'ok': True})
    else:
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
