from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from django.core.mail import send_mail
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from api.serializers.user import UserCreateSerializer, UserRegistrationSerializer

from account.models import CustomUser

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

# from .forms import UserRegistrationForm


# def register(request):
#     if request.method == "POST":
#         user_form = UserRegistrationForm(request.POST)
#         if user_form.is_valid():
#             new_user = user_form.save(commit=False)
#             new_user.set_password(user_form.cleaned_data["password"])
#             new_user.save()
#             return render(request, "account/register_done.html", {"new_user": new_user})
#     else:
#         user_form = UserRegistrationForm()

#     return render(request, "account/register.html", {"user_form": user_form})

class Register(GenericAPIView):

    serializer_class = UserRegistrationSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            new_user = serializer.create(serializer.validated_data)
            self._send_confirm_email(request, new_user)
            return Response({'message': 'Successfullly signed up'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
    def _generate_unique_token(
            self,
            request,
            user,
    ):
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            "email": user.email,
            "domain": domain,
            "site_name": site_name,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            "token": settings.DEFAULT_TOKEN_GENERATOR.make_token(user),
            "protocol": ['https', 'http'][settings.DEBUG]
        }
        print(context)
        return context

    def _send_confirm_email(
            self,
            request,
            user,
            email_template_name="email/base_template.html"
    ):
        context = self._generate_unique_token(request, user)
        body = loader.render_to_string(email_template_name, context)

        result = send_mail(
            "Confrim email",
            body,
            settings.EMAIL_HOST_USER,
            [user.email],
            False,
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD,
        )
        print(result)
        if result:
            return Response({"message": "Message sent successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Message sent failed"}, status=status.HTTP_400_BAD_REQUEST)


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uid64, token):
        user = self.get_user(request.user, uid64)
        if user is not None and settings.DEFAULT_TOKEN_GENERATOR.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": 'User %s email successfully verified' % user}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Confirmation code expired, request a new code"})

    @staticmethod
    def get_user(user, uid64):
        try:
            uid = urlsafe_base64_decode(uid64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist) as e:
            # logger.warning(f"User %s tried to verify email, but got error %s", user, e)
            user = None
        return user
