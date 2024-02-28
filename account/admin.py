from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import City, CityGroup, CustomUser
from django.core.signals import setting_changed

from .signals import set_cases

# Register your models here.


class UserAdmin(UserAdmin):
    pass


admin.site.register(CustomUser, UserAdmin)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = (
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

def ready():
    setting_changed.connect(set_cases)
