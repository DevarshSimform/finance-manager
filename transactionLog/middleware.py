import json
from uuid import UUID
from django.utils.timezone import now
from finance.models import Transaction  # Adjust import paths
from transactionLog.models import TransactionLog



class TransactionLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        saved_data = None
        transaction_id = None

        # Capture request data early
        if request.method in ['POST', 'PUT', 'PATCH'] and request.path.startswith('/api/v1/transactions'):
            try:
                saved_data = json.loads(request.body.decode('utf-8'))
                if request.method in ['PUT', 'PATCH']:
                    # Try to extract UUID from URL
                    transaction_id = request.path.rstrip('/').split('/')[-1]
                    transaction_id = UUID(transaction_id)
            except Exception as e:
                print("Failed to parse request body or extract ID:", e)

        # view executes here
        response = self.get_response(request)

        # After view logic
        try:
            if saved_data and request.user.is_authenticated and response.status_code in [200, 201]:
                action = 'created' if request.method == 'POST' else 'updated'

                # For POST, get transaction ID from response
                if request.method == 'POST':
                    transaction_id = response.data.get('id') if hasattr(response, 'data') else None

                if not transaction_id:
                    print("No transaction ID found. Skipping log.")
                    return response

                tx = Transaction.objects.filter(id=transaction_id).first()
                if not tx:
                    print("Transaction not found. Skipping log.")
                    return response

                TransactionLog.objects.create(
                    transaction=tx.id,
                    user=tx.user_id.username,
                    category=tx.category_id.name,
                    amount=tx.amount,
                    type=tx.type,
                    action=action,
                    description=tx.description,
                    logged_at=now()
                )

        except Exception as e:
            print("Transaction logging failed:", e)

        return response


# class TransactionLogMiddleware:

#     def __init__(self, get_response):
#         print('Initialized')
#         self.get_response = get_response

#     def __call__(self, request):
#         print('before request')
#         response = self.get_response(request)
#         print(request.body)
#         print('after request')
#         return response
    
#     def process_view(self, request, view_func, view_args, view_kwargs):
#         print('inside process_view')
#         print(view_func)
#         print(view_args)
#         print(view_kwargs)

#     def process_request(self, request):
#         pass

#     def process_response(self, request):
#         pass

