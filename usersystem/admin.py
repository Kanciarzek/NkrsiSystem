from django.contrib import admin
from django.template.loader import render_to_string
from usersystem.models import User, FrontLink

admin.register(FrontLink)(admin.ModelAdmin)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = (
        'email', ('first_name', 'last_name'), ('is_candidate', 'is_staff', 'is_active'), 'phone', 'student_card_id',
        'groups')

    def save_model(self, request, obj: User, form, change):
        if not change:
            password = User.objects.make_random_password()
            obj.set_password(password)
            html_message = render_to_string("email/register.html",
                                            {"username": obj.get_full_name(), "password": password, "home": "lol"})
            obj.email_user("Witamy w NKRSI", None, html_message=html_message)
            obj.invite_to_slack(request)
        return super().save_model(request, obj, form, change)
