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
        'email', ('first_name', 'last_name'), ('is_candidate', 'is_staff', 'is_active', 'is_superuser'), 'function',
        'phone', 'student_card_id', 'date_joined')

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
                                            {"username": obj.get_full_name(), "password": password,
                                             "protocol": request.scheme, "domain": request.get_host})
            obj.email_user("Witamy w NKRSI", None, html_message=html_message)
            obj.invite_to_slack(request)
        else:
            if form.initial['is_candidate'] and not form.cleaned_data['is_candidate']:
                html_message = render_to_string("email/promote.html",
                                                {"username": obj.get_full_name()})
                obj.email_user("Zostajesz członkiem zwyczajnym w NKRSI", None, html_message=html_message)
            if form.initial['is_active'] and not form.cleaned_data['is_active']:
                html_message = render_to_string("email/degredate.html",
                                                {"username": obj.get_full_name()})
                obj.email_user("NKRSI żegna", None, html_message=html_message)
        obj.save()
