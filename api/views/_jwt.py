from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers import MyTokenObtainPairSerializer

# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Возвращает access и refresh токены
    """
    serializer_class = MyTokenObtainPairSerializer
