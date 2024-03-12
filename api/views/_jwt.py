from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers import MyTokenObtainPairSerializer

# Create your views here.
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


@extend_schema(
    tags=['account']
)
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Возвращает access и refresh токены
    """
    serializer_class = MyTokenObtainPairSerializer
