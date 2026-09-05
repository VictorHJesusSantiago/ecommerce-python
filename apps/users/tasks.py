from celery import shared_task
from django.utils import timezone


@shared_task
def send_welcome_email(user_id):
    from django.contrib.auth import get_user_model
    from apps.common.utils import send_templated_email
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        send_templated_email(
            subject='Welcome to Our Store!',
            template_name='emails/welcome.html',
            context={'user': user},
            recipient_list=[user.email],
        )
    except User.DoesNotExist:
        pass


@shared_task
def send_verification_email(user_id):
    from django.contrib.auth import get_user_model
    from apps.common.utils import send_templated_email, generate_unique_code
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        code = generate_unique_code(32)
        send_templated_email(
            subject='Verify Your Email',
            template_name='emails/verify_email.html',
            context={'user': user, 'verification_code': code},
            recipient_list=[user.email],
        )
    except User.DoesNotExist:
        pass


@shared_task
def cleanup_inactive_sessions():
    from apps.users.models import UserSession
    threshold = timezone.now() - timezone.timedelta(days=30)
    deleted, _ = UserSession.objects.filter(
        last_activity__lt=threshold, is_active=True
    ).update(is_active=False)
    return deleted
