from django.contrib.auth.forms import UserChangeForm
from usersystem.models import User


class EditProfileForm(UserChangeForm):
    """
    Formularz edycji profilu. Ma mniejszą ilość pól niż UserChangeForm.
    """
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'password',
            'student_card_id',
            'phone'
        )
