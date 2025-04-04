from celery import shared_task
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
