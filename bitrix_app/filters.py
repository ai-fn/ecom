from django_filters import rest_framework as filters

from bitrix_app.models import Lead


class LeadFilterSet(filters.FilterSet):

    class Meta:
        model = Lead
        fields = [
            "status",
        ]
