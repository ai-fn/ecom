from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import City, CityGroup, CustomUser
from django.core.signals import setting_changed
from django.utils.translation import gettext_lazy as _

from .signals import set_cases

# Register your models here.


class UserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets[:2],
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "email_confirmed",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        *UserAdmin.fieldsets[3:]
    )

admin.site.register(CustomUser, UserAdmin)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "domain",
        "address",
        "population",
    )
    search_fields = (
        "name",
        "domain",
        "address",
    )


@admin.register(CityGroup)
class CityGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "main_city",
    )
    search_fields = (
        "name",
    )

def ready():
    setting_changed.connect(set_cases)
