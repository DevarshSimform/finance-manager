import redis,time

from django.shortcuts import render, get_object_or_404
from finance.models import Transaction
from finance.serializers import RegisterSerializer, LoginSerializer, CategorySerializer, TransactionSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


class TransactionListCreateApiView(ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionRetrieveUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def destroy(self, destroy, *args, **kwargs):
        instance =self.get_object()
        instance.delete()
        return Response({'msg': 'soft delete performed'}, status=status.HTTP_200_OK)
    


class RegisterAPIView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'User Registered'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            token = request.auth  # Get the access token from request
            refresh_token = request.data.get("refresh_token")  # Get refresh token from request body

            # Blacklist Access Token in Redis
            if token:
                access_exp = 3600  # Blacklist for 1 hour (adjust as needed)
                redis_client.setex(f"blacklist:access:{token}", access_exp, "blacklisted")

            # Blacklist Refresh Token in PostgreSQL only
            if refresh_token:
                try:
                    refresh = RefreshToken(refresh_token)

                    # Store refresh token in PostgreSQL blacklist
                    OutstandingToken.objects.filter(jti=refresh["jti"]).update(blacklisted_at=True)
                    BlacklistedToken.objects.create(token_id=refresh["jti"])

                except Exception:
                    return Response({"error": "Invalid refresh token"}, status=400)

            return Response({"message": "Successfully logged out"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=400)

            # Check if refresh token is blacklisted in PostgreSQL
            try:
                token = RefreshToken(refresh_token)  # Convert to token object
                if BlacklistedToken.objects.filter(token__jti=token["jti"]).exists():
                    return Response({"error": "Refresh token has been blacklisted"}, status=401)
            except Exception:
                return Response({"error": "Invalid refresh token"}, status=400)

            # Proceed with generating a new access token
            return super().post(request, *args, **kwargs)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

class BalanceViewAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        balance = request.user.balance
        return Response({'total-balance': balance} ,status=status.HTTP_200_OK)
    

class AllTransactionAPIView(APIView):
    
    def get(self, request):
        transactions = Transaction.objects.with_deleted()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class DeletedTransactionAPIView(APIView):

    def get(self, request):
        transactions = Transaction.objects.only_deleted()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RestoreTransactionAPIView(APIView):

    def post(self, request, pk):
        transaction = get_object_or_404(Transaction.objects.only_deleted(), pk=pk)
        if not transaction.is_deleted:
            return Response({'msg': 'transaction is active'}, status=status.HTTP_400_BAD_REQUEST)
        transaction.restore()
        return Response({'msg': 'Transaction Restored'}, status=status.HTTP_200_OK)


class HardDeleteTransactionAPIView(APIView):

    def delete(self, request, pk):
        transaction = get_object_or_404(Transaction.objects.with_deleted(), pk=pk)
        transaction.delete(hard=True)
        return Response({'msg': 'Transaction Hard deleted'}, status=status.HTTP_200_OK)