import requests
from django.shortcuts import render
from datetime import datetime
from nkrsiSystem import settings


def index(request):
    response = requests.get(
        'https://graph.facebook.com/v6.0/nkrsiuj/posts?access_token={}'.format(settings.FACEBOOK_TOKEN))
    result = response.json()
    if 'data' not in result:
        args = dict()
    else:
        post_text = result['data'][0]['message']
        post_time = datetime.strptime(result['data'][0]['created_time'], "%Y-%m-%dT%H:%M:%S+0000")
        args = {'fb_news_text': post_text, 'fb_news_date': str(post_time)}
    return render(request, 'front_page/main.html', args)
