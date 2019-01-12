from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('faq', views.faq, name='faq'),
    path('account/me', views.view_user, name='user'),
    path('account/me/edit', views.edit_user, name='user-edit'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('ajax/door', views.door),
    path('ajax/projector', views.projector),
    path('rest/card_id', views.is_student_card_id_in_db)

]