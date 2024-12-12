from django import forms
from api.models import ApiKey
from django.contrib import admin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _


class ApiKeyForm(forms.ModelForm):
    key = ReadOnlyPasswordHashField(
        label=_("API key"),
        help_text="Raw API keys are not stored, so there is no way to see this API key"
    )

    class Meta:
        model = ApiKey
        fields = "__all__"


class ApiKeyAddForm(forms.ModelForm):
    key = forms.CharField(
        label=_("API key"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = ApiKey
        fields = "__all__"

    def save(self, commit=True):
        instance: ApiKey = super().save(commit=False)
        raw_key = self.cleaned_data.get('key')
        if raw_key:
            instance.set_api_key(raw_key)
        if commit:
            instance.save()
        return instance


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели API Key.
    """
    form = ApiKeyForm
    add_form = ApiKeyAddForm
    list_display = ('id', 'client_id', 'created_at')

    fieldsets = (
        (None, {'fields': ('client_id', 'key', 'allowed_ips', 'allowed_hosts', 'expires_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('client_id', 'key', 'allowed_ips', 'allowed_hosts', 'expires_at'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Поле `key` становится доступным только при добавлении нового объекта.
        """
        if obj:
            return ('key', *self.readonly_fields)
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        """
        Возвращает форму для добавления или редактирования объекта.
        """
        if obj is None:
            kwargs['form'] = self.add_form
        else:
            kwargs['form'] = self.form
        return super().get_form(request, obj, **kwargs)
