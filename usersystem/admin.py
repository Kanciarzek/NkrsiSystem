from django.contrib import admin
from django.template.loader import render_to_string
from usersystem.models import User, FrontLink, FAQ, DoorOpenLog

admin.register(FrontLink)(admin.ModelAdmin)
admin.register(FAQ)(admin.ModelAdmin)


@admin.register(DoorOpenLog)
class DoorOpenLogAdmin(admin.ModelAdmin):
    """
    Modysikacja tej klasy sprawia, że administrator ma możliwość jedynie podglądu logów otwarcia drzwi.
    """

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = (
        'email', ('first_name', 'last_name'), ('is_candidate', 'is_staff', 'is_active'), 'phone', 'student_card_id',
        'date_joined')

    def save_model(self, request, obj: User, form, change):
        """
        Zapisuje użytkonika. Wysyłane jest jednocześnie zaproszenie do platformy Slack, email powitalny z hasłem oraz
        dodawany jest użytkownik do bazy radius.
        :param request:
        :param obj:
        :param form:
        :param change: True w wypadku, gdy użytkownik został zmodyfikowany, False, gdy jest tworzony.
        :return: :model:`usersystem.User`
        """
        if not change:
            password = User.objects.make_random_password()
            obj.set_password(password)
            html_message = render_to_string("email/register.html",
                                            {"username": obj.get_full_name(), "password": password})
            obj.email_user("Witamy w NKRSI", None, html_message=html_message)
            obj.invite_to_slack(request)
            obj.create_radius_user(password, request)
        return super().save_model(request, obj, form, change)
