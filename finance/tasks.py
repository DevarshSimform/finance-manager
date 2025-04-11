from celery import shared_task
from django.conf import settings
from django.utils import timezone
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
def send_transaction_limit_reached_email(user_id):
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject='Transaction Limit Reached',
            message='You have already made 3 transactions today. Please try again tomorrow.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return "Rate limit email sended after 3 transactions"
    except User.DoesNotExist:
        pass