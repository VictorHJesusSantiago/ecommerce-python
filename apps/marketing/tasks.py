from celery import shared_task
from django.utils import timezone


@shared_task
def cleanup_expired_coupons():
    from .models import Coupon
    expired = Coupon.objects.filter(end_date__lt=timezone.now(), is_active=True)
    count = expired.update(is_active=False)
    return count


@shared_task
def send_email_campaign(campaign_id):
    from .models import EmailCampaign, Newsletter
    from apps.common.utils import send_templated_email
    try:
        campaign = EmailCampaign.objects.get(pk=campaign_id)
        subscribers = Newsletter.objects.filter(is_active=True, confirmed=True)
        count = 0
        for subscriber in subscribers:
            try:
                send_templated_email(
                    subject=campaign.subject,
                    template_name='emails/campaign.html',
                    context={
                        'subscriber': subscriber,
                        'campaign': campaign,
                        'unsubscribe_url': f'/unsubscribe/{subscriber.email}/',
                    },
                    recipient_list=[subscriber.email],
                )
                count += 1
            except Exception:
                continue
        campaign.total_sent = count
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.save(update_fields=['total_sent', 'status', 'sent_at', 'updated_at'])
        return count
    except EmailCampaign.DoesNotExist:
        return 0


@shared_task
def process_newsletter_queue():
    from .models import Newsletter
    pending = Newsletter.objects.filter(confirmed=False, is_active=True)
    return pending.count()


@shared_task
def generate_promotion_report():
    from .models import Promotion, Coupon
    from django.db.models import Sum
    active_promotions = Promotion.objects.filter(is_active=True).count()
    total_coupon_usage = Coupon.objects.aggregate(total=Sum('times_used'))['total'] or 0
    return {
        'active_promotions': active_promotions,
        'total_coupon_usage': total_coupon_usage,
    }
