from django.db import connection
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from finance.models import Transaction, Category, CustomUser, PasswordReset
from finance.serializers import (
    CategorySerializer, 
    TransactionSerializer, 
    TransactionDetailSerializer, 
    UserDetailSerializer, 
    ResetPasswordRequestSerializer,
    ResetPasswordSerializer
)
from finance.signals import post_save_with_request
from finance.custompermissions import HasObjectPermOrAdmin, IsOwnerOrAdmin

from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView, 
    RetrieveUpdateDestroyAPIView, 
    ListCreateAPIView, 
    RetrieveAPIView, 
    GenericAPIView
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.throttling import ScopedRateThrottle

from guardian.shortcuts import get_objects_for_user

from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)


class UserProfileView(RetrieveAPIView):
    """
    API view to retrieve the details of the currently authenticated user.

    This view requires the user to be authenticated and uses the `UserDetailSerializer`
    to serialize the user data.

    Attributes:
        permission_classes (list): Specifies the permissions required to access this view.
        serializer_class (Serializer): The serializer class used to serialize the user data.

    Methods:
        get_object(): Returns the currently authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user    



class CategoryListCreateAPIView(ListCreateAPIView):
    """
    API view to list and create Category objects.
    - Permissions: Requires `HasObjectPermOrAdmin` permission.
    - Serializer: Uses `CategorySerializer` for validation and serialization.
    - Throttling: Scoped rate throttling with 'high' for GET and 'low' for other methods.
    - Filtering: Supports search by 'name' field.

    Methods:
    - get_queryset(): Returns categories accessible by the requesting user.
    - post(request): Creates a new category and triggers a post-save signal.
    - get_throttles(): Dynamically sets throttle scope based on request method.
    """
    
    permission_classes = [HasObjectPermOrAdmin]
    serializer_class = CategorySerializer
    throttle_classes = [ScopedRateThrottle]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Category.objects.all()
        return get_objects_for_user(self.request.user, 'view_category', Category)
    
    def post(self, request):
        ''' sending request in custom signal to get user and add object permission to created category '''
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            name = serializer.validated_data.get('name')
            category = Category.objects.get(name=name)
            post_save_with_request.send(sender=Category, instance=category, request=request, created=True, is_superuser=request.user.is_superuser)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_throttles(self):
        if self.request.method == 'GET':
            self.throttle_scope = 'high'
        else:
            self.throttle_Scope = 'low'
        return super(CategoryListCreateAPIView, self).get_throttles()

        

class CategoryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific Category instance.

    - Requires appropriate object-level permissions or admin access.
    - Uses `CategorySerializer` for serialization.
    - Operates on the `Category` model.
    """

    permission_classes = [HasObjectPermOrAdmin]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class TransactionListCreateAPIView(ListCreateAPIView):
    '''This API view provides functionality for authenticated users to list and create transactions. 
    It enforces specific permissions, throttling, and filtering rules to ensure proper access control 
    and efficient handling of requests.
    Attributes:
        permission_classes (list): Specifies that only authenticated users can access this view.
        serializer_class (TransactionSerializer): Defines the serializer used for validating and 
            representing transaction data.
        throttle_classes (list): Applies rate throttling to requests based on the defined scope.
        filter_backends (list): Enables filtering of transactions using search fields.
        search_fields (list): Specifies the fields ('description', 'amount', 'type', 'source') 
            that can be searched.
    Methods:
        get_queryset():
            Returns the queryset of transactions based on the user's role. Superusers can view all 
            transactions, while regular users can only view their own transactions.
        perform_create(serializer):
            Handles the creation of a new transaction. Superusers are restricted from creating 
            transactions and will receive a PermissionDenied error.
        get_throttles():
            Applies different throttle scopes based on the HTTP method. 'high' throttle scope is 
            applied for GET requests, while 'low' throttle scope is applied for other methods.
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    throttle_classes = [ScopedRateThrottle]
    filter_backends = [SearchFilter]
    search_fields = ['description', 'amount', 'type', 'source']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Transaction.objects.all()
        return Transaction.objects.filter(user_id=self.request.user)
    
    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            raise PermissionDenied(detail='Superuser cannot create any transaction')
        return super().perform_create(serializer)
    
    def get_throttles(self):
        if self.request.method == 'GET':
            self.throttle_scope = 'high'
        else:
            self.throttle_Scope = 'low'
        return super(TransactionListCreateAPIView, self).get_throttles()
        


class TransactionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    TransactionRetrieveUpdateDestroyAPIView is a view that allows retrieving, updating, 
    and disabling the deletion of a transaction. It enforces permissions and throttling 
    based on the request method.
    Attributes:
        permission_classes (list): Specifies the permissions required to access this view. 
            Only the owner or an admin can access.
        throttle_classes (list): Specifies the throttling classes to be used for rate limiting.
        queryset (QuerySet): The base queryset for retrieving transactions.
    Methods:
        get_serializer_class():
            Returns the appropriate serializer class based on the request method.
            - GET: Uses TransactionDetailSerializer.
            - Other methods: Uses TransactionSerializer.
        get_throttles():
            Configures the throttle scope based on the request method.
            - GET: High throttle scope.
            - Other methods: Low throttle scope.
        Note:
            The deletion of transactions is disabled, and attempting to delete will raise 
            a PermissionDenied exception (commented out in the code).
    """

    permission_classes = [IsOwnerOrAdmin]
    throttle_classes = [ScopedRateThrottle]

    queryset = Transaction.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TransactionDetailSerializer
        return TransactionSerializer

    # def perform_destroy(self, serializer):
    #     raise PermissionDenied(detail='You cannot delete any transaction')
    
    def get_throttles(self):
        if self.request.method.lower() == 'get':
            self.throttle_scope = 'high'
        else:
            self.throttle_scope = 'low'
        return super(TransactionRetrieveUpdateDestroyAPIView, self).get_throttles()
    


class BalanceViewAPIView(APIView):
    """
    BalanceViewAPIView is an API view that retrieves the balance of the currently logged-in user.

    This view requires the user to be authenticated and calculates the user's balance using 
    a property function named `balance`.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the user's balance by calculating it using the property function named balance."""
        balance = request.user.balance
        return Response({'total-balance': balance}, status=status.HTTP_200_OK)
    


class RequestPasswordReset(GenericAPIView):
    """
    API view to handle password reset requests.

    This view allows users to request a password reset by providing their email address.
    If the email corresponds to a registered user, a password reset token is generated
    and sent to the user's email address.

    Attributes:
        permission_classes (list): Specifies the permissions required to access this view.
                                   In this case, it allows unrestricted access.
        throttle_classes (list): Specifies the throttling policy for this view.
        throttle_Scope (str): Defines the scope for rate limiting.
        serializer_class (Serializer): Serializer class used to validate the input data.

    Methods:
        post(request):
            Handles POST requests to initiate the password reset process.
            Validates the provided email, generates a reset token, and sends an email
            with the reset link if the user exists.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_Scope = 'low'
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        to_email = request.data['email']
        user = CustomUser.objects.filter(email__iexact=to_email).first()

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = PasswordReset(email=to_email, token=token)
            reset.save()

            reset_url = f"http://localhost:8000/api/v1/reset-password/{token}"

            email = EmailMessage(
                subject="Reset Password",
                body=reset_url,
                from_email=settings.EMAIL_HOST_USER,
                to=[to_email],
            )
            # email.content_subtype = "html"
            email.send()

            return Response({'success': 'Check your email to reset password'}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User with credentials not found"}, status=status.HTTP_404_NOT_FOUND)
        


class ResetPassword(GenericAPIView):
    """
    API endpoint to reset a user's password using a token.
    This view allows users to reset their password by providing a valid token
    and new password details. It validates the token, ensures the new password
    and confirmation password match, and updates the user's password if all
    conditions are met.
    Methods:
        post(request, token):
            Handles the password reset process.
    Attributes:
        permission_classes (list): A list of permission classes. This endpoint
            does not require authentication.
        serializer_class (ResetPasswordSerializer): The serializer used to
            validate the input data.
    POST Parameters:
        token (str): The token used to validate the password reset request.
        new_password (str): The new password for the user.
        confirm_password (str): Confirmation of the new password.
    Responses:
        200 OK:
            - Password updated successfully.
        400 Bad Request:
            - Passwords do not match.
            - Invalid token error.
        404 Not Found:
            - No user found with the provided email.
    """
    
    permission_classes = []
    serializer_class = ResetPasswordSerializer

    def post(self, request, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        new_password = data['new_password']
        confirm_password = data['confirm_password']

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        
        reset_obj = PasswordReset.objects.filter(token=token).first()

        if not reset_obj:
            return Response({'error': 'Invalid token error'}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(email=reset_obj.email).first()

        if user:
            user.set_password(request.data['new_password'])
            user.save()
            reset_obj.delete()
            return Response({'success': 'Password updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No user found'}, status=status.HTTP_404_NOT_FOUND)


class GetCategoryTotal(APIView):
    """
    API view to retrieve the total amount grouped by category for the authenticated user.

    This view uses a raw SQL query to fetch data from the database by calling the 
    `get_total_by_category` function with the user's ID as a parameter.

    Methods:
        get(request):
            Handles GET requests to retrieve the total amount grouped by category.

    Attributes:
        permission_classes (list): Specifies that the view requires the user to be authenticated.

    Raises:
        Exception: If any error occurs during the database query execution, it returns a 500 
        Internal Server Error response with the error message.

    Returns:
        Response: A JSON response containing a list of dictionaries with `category` and 
        `total_amount` keys, or an error message in case of failure.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM get_total_by_category(%s)", [user_id])
                data = cursor.fetchall()

            result = [{'category': row[0], 'total_amount': float(row[1])} for row in data]
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TransactionDetailByDate(APIView):
    """
    APIView to retrieve transaction details by date for the authenticated user.

    This view uses a raw SQL query to fetch transaction details from the database
    by invoking a stored procedure `get_transaction_details_by_date`. The stored
    procedure is expected to return transaction details for the given user ID.

    Methods:
        get(request):
            Handles GET requests to retrieve transaction details for the authenticated user.

    Attributes:
        permission_classes (list): Specifies the permissions required to access this view.
            Only authenticated users are allowed.

    Raises:
        Exception: If any error occurs during the database query execution, it is caught
            and returned as a 500 Internal Server Error response.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM get_transaction_details_by_date(%s)", [user_id])
                columns = [col[0] for col in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response(rows, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)