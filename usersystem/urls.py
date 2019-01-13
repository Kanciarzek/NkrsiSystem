from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('faq', views.faq, name='faq'),
    path('account/me/password/', views.change_password, name='user-password'),
    path('account/me/', views.view_user, name='user'),
    path('account/<int:user_id>/', views.view_user, name='user-by-id'),
    path('account/me/edit/', views.edit_user, name='user-edit'),
    path('accounts/', views.all_users, name='user-list'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('ajax/door', views.door, name='ajax-door'),
    path('ajax/projector', views.projector, name='ajax-projector'),
    path('rest/card_id', views.is_student_card_id_in_db, name='card-id'),

]
