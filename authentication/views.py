import secrets, json
from redis import Redis
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from finance.serializers import RegisterSerializer, LoginSerializer
from finance.models import CustomUser
from authentication.utils import encrypt_password, decrypt_password


redis_client = Redis()

# Register user API with email verification (2FA)

class RegisterAPIView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            token = secrets.token_urlsafe(32)

            # encrypt password before saving into redis
            redis_data = {
                "username": data["username"],
                "email": data["email"],
                "password": encrypt_password(data["password"]),  
            }

            redis_client.setex(f"verify:{token}", 120, json.dumps(redis_data))  # 2 min

            verification_url = f"http://localhost:8000/api/verify-email/?token={token}"
            html_content = render_to_string("authentication/register_email.html", {
                "username": data["username"],
                "verification_url": verification_url
            })

            email = EmailMessage(
                subject="Welcome! Verify Your Email",
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[data["email"]],
            )
            email.content_subtype = "html"
            email.send()

            return Response({"message": "Check your email to verify your account."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmailAPIView(APIView):

    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        redis_key = f"verify:{token}"
        user_data_json = redis_client.get(redis_key)

        if not user_data_json:
            return Response({"error": "Invalid or expired token"}, status=400)

        user_data = json.loads(user_data_json)

        if CustomUser.objects.filter(email=user_data["email"]).exists():
            return Response({"error": "User already registered."}, status=400)

        # Decrypt password after get encrypted_passwrod from redis
        user = CustomUser.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            password=decrypt_password(make_password(user_data["password"])),
        )

        redis_client.delete(redis_key)
        return Response({"message": "Email verified. Account created successfully!"})



class LoginAPIView(APIView):
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'msg': 'Enter valid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Refresh token blacklisted and user logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


# Register user API without 2FA 
# class RegisterAPIView(APIView):

#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'msg': 'User Registered'}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)