import secrets
from redis import Redis
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.cache import cache
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from finance.serializers import RegisterSerializer, LoginSerializer
from finance.models import CustomUser


redis_client = Redis()

# Register user API with email verification (2FA)

class RegisterAPIView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            token = secrets.token_urlsafe(32)

            # Create user with is_active = False
            user = CustomUser.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                is_active=False
            )

            # Store token in Redis via Django cache, mapped to email
            cache.set(f"verify:{token}", user.email, timeout=180)  # 3 mins

            verification_url = f"http://localhost:8000/api/verify-email/?token={token}"
            html_content = render_to_string("authentication/regstration_email.html", {
                "username": user.username,
                "verification_url": verification_url
            })

            email = EmailMessage(
                subject="Verify Your Email",
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
            )
            email.content_subtype = "html"
            email.send()

            return Response({"message": "User created. Check your email to verify your account.", "warning": "Token is expiring in 3 minutes"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmailAPIView(APIView):

    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        email = cache.get(f"verify:{token}")
        if not email:
            user = CustomUser.objects.filter(is_active=False).first()
            if user:
                user.delete(hard=True)
            return Response({"error": "Invalid or expired token, Register user again"}, status=400)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user.is_active:
            return Response({"message": "User already verified."})

        user.is_active = True
        user.save()


        cache.delete(f"verify:{token}")

        return Response({"message": "Email verified. Account activated successfully!"})



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