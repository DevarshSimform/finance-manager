import redis
from django.http import JsonResponse
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class JWTBlacklistMiddleware:
    """
    Middleware to check if JWT tokens (access and refresh) are blacklisted in Redis.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]  # Extract the token

            # Check if token is blacklisted
            if redis_client.exists(f"blacklist:access:{token}"):
                return JsonResponse({"error": "Token has been blacklisted. Please log in again."}, status=401)

            try:
                # Validate the token
                jwt_authenticator = JWTAuthentication()
                user, validated_token = jwt_authenticator.authenticate(request)
                request.user = user
            except InvalidToken:
                return JsonResponse({"error": "Invalid token"}, status=401)

        response = self.get_response(request)
        return response
