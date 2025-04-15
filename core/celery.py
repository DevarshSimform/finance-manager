import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-daily-transaction-email': {
        'task': 'finance.tasks.send_daily_transaction_email',
        'schedule': crontab(hour=9, minute=00),  # Every day at 9 AM
    },
}