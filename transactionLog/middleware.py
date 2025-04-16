import json
from uuid import UUID
from django.utils.timezone import now
from finance.models import Transaction
from transactionLog.models import TransactionLog



class TransactionLogMiddleware:
    """
    Middleware to log transaction actions (create, update, delete) for authenticated users interacting with the transactions API.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        saved_data = None
        transaction_id = None
        pre_delete_tx = None  # Store transaction info before DELETE

        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and request.path.startswith('/api/v1/transactions'):
            try:
                if request.method in ['POST', 'PUT', 'PATCH']:
                    saved_data = json.loads(request.body.decode('utf-8'))
                elif request.method == 'DELETE':
                    saved_data = 1

                if request.method in ['PUT', 'PATCH', 'DELETE']:
                    transaction_id = UUID(request.path.rstrip('/').split('/')[-1])
                    pre_delete_tx = Transaction.objects.filter(id=transaction_id).first()
            except Exception as e:
                print("Failed to parse request or extract transaction ID:", e)

        # Execute view
        response = self.get_response(request)

        try:
            if saved_data and request.user.is_authenticated and response.status_code in [200, 201, 204]:
                if request.method == 'POST':
                    action = 'created'
                    transaction_id = response.data.get('id') if hasattr(response, 'data') else None
                    tx = Transaction.objects.filter(id=transaction_id).first()
                elif request.method == 'DELETE':
                    action = 'deleted'
                    tx = pre_delete_tx
                else:
                    action = 'updated'
                    tx = Transaction.objects.filter(id=transaction_id).first()

                if not tx:
                    print("Transaction not found. Skipping log.")
                    return response

                # Store as string values in TransactionLog
                TransactionLog.objects.create(
                    transaction=str(tx.id),
                    user=str(tx.user_id),
                    category=str(tx.category_id),
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