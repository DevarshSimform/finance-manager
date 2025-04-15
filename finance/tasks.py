from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from finance.models import CustomUser, Transaction
from datetime import timedelta, date
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

@shared_task
def cleanup_expired_tokens():
    expired_tokens = OutstandingToken.objects.filter(expires_at__lt=timezone.now())
    count = expired_tokens.count()

    # Delete related blacklisted tokens
    BlacklistedToken.objects.filter(token__in=expired_tokens).delete()

    expired_tokens.delete()

    return f"Deleted {count} expired tokens"


@shared_task
def send_daily_transaction_email():
    yesterday = date.today() - timedelta(days=1)
    print("Sending email...")
    for user in CustomUser.objects.exclude(username='root'):
        
        if not user.email or user.email == 'AnonymousUser':
            continue

        transactions = Transaction.objects.filter(
            user_id=user.id,
            created_at__date = yesterday,
            is_deleted = False
        )
        
        total_income = sum(txn.amount for txn in transactions if txn.type == 'income')
        total_expense = -sum(txn.amount for txn in transactions if txn.type == 'expense')  # amount is negative
        net_balance = total_income - total_expense

        context = {
            'user': user,
            'date': yesterday,
            'transactions': transactions,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
        }

        html_content = render_to_string('finance/daily_transaction_summary.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject="Your Daily Transaction Summary",
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()