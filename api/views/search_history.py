from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from api.serializers import SearchHistorySerializer
from api.permissions import IsOwner
from shop.models import SearchHistory

from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=['Shop']
)
class SearchHistoryViewSet(ModelViewSet):

    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
