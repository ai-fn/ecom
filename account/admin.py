from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import City, CityGroup, CustomUser

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