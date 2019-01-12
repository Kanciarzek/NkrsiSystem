from django import forms
from django.contrib.auth.forms import UserChangeForm

from usersystem.models import User


class EditProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'password',
            'student_card_id',
            'phone'
        )
