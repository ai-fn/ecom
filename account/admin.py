from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.signals import setting_changed
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from account.models import City, CityGroup, CustomUser
from api.mixins import ValidatePhoneNumberMixin, ActiveAdminMixin


class CustomUserValidation(ValidatePhoneNumberMixin):

    def clean_phone(self):
        try:
            return self.validate_phone(self.cleaned_data.get('phone'))
        except ValidationError as e:
            self.add_error("phone", _(str(e.detail[0])))


class CustomUserChangeForm(CustomUserValidation, UserChangeForm):
    class Meta:
        model = CustomUser
        fields = "__all__"


class CustomUserCreationForm(CustomUserValidation, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = "__all__"
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data.get('phone')
        if commit:
            user.save()

        return user


class CustomUserAdmin(ActiveAdminMixin, UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = (
        "phone",
        "email",
        "last_name",
        "first_name",
        "is_staff",
    )
    fieldsets = (
        *UserAdmin.fieldsets[:1],
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'address')}),
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
    add_fieldsets = (
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'address')}),
        (None, {
            'classes': ('wide',),
            'fields': ('password1', 'password2'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(City)
class CityAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "city_group",
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
class CityGroupAdmin(ActiveAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "main_city",
    )
    search_fields = (
        "name",
    )
