from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import (
    Coupon, CouponUsage, Promotion, Banner, Newsletter,
    EmailCampaign, LoyaltyProgram, ReferralProgram
)
from .serializers import (
    CouponSerializer, CouponValidateSerializer, PromotionSerializer,
    BannerSerializer, NewsletterSerializer, EmailCampaignSerializer,
    LoyaltyProgramSerializer, ReferralProgramSerializer
)
from apps.common.permissions import IsAdminUser, CanManageMarketing
from apps.common.pagination import StandardResultsSetPagination


class CouponViewSet(viewsets.ModelViewSet):
    serializer_class = CouponSerializer
    permission_classes = [CanManageMarketing]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Coupon.objects.all()

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def validate_coupon(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Invalid coupon code.'}
            }, status=status.HTTP_404_NOT_FOUND)

        if not coupon.is_valid:
            return Response({
                'success': False,
                'error': {'message': 'This coupon has expired or is no longer valid.'}
            }, status=status.HTTP_400_BAD_REQUEST)

        if not coupon.is_valid_for_user(request.user):
            return Response({
                'success': False,
                'error': {'message': 'You have already used this coupon the maximum number of times.'}
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'coupon': CouponSerializer(coupon).data,
        })


class PromotionViewSet(viewsets.ModelViewSet):
    serializer_class = PromotionSerializer
    permission_classes = [CanManageMarketing]

    def get_queryset(self):
        return Promotion.objects.all()

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def active(self, request):
        promotions = Promotion.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
        serializer = PromotionSerializer(promotions, many=True)
        return Response({'success': True, 'promotions': serializer.data})


class BannerViewSet(viewsets.ModelViewSet):
    serializer_class = BannerSerializer
    permission_classes = [CanManageMarketing]

    def get_queryset(self):
        return Banner.objects.all()

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def active(self, request):
        banners = Banner.objects.filter(
            is_active=True,
        )
        now = timezone.now()
        banners = banners.filter(
            models.Q(start_date__isnull=True) | models.Q(start_date__lte=now)
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
        )
        serializer = BannerSerializer(banners, many=True)
        return Response({'success': True, 'banners': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def record_click(self, request, pk=None):
        banner = self.get_object()
        banner.record_click()
        return Response({'success': True})


class NewsletterViewSet(viewsets.ModelViewSet):
    serializer_class = NewsletterSerializer
    permission_classes = [CanManageMarketing]
    queryset = Newsletter.objects.all()

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def subscribe(self, request):
        serializer = NewsletterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        subscriber, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={
                'user': request.user if request.user.is_authenticated else None,
                'source': serializer.validated_data.get('source', 'website'),
            }
        )
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.unsubscribed_at = None
            subscriber.save()
        from apps.common.signals import newsletter_subscribed
        newsletter_subscribed.send(sender=Newsletter, subscriber=subscriber)
        return Response({
            'success': True,
            'message': 'Successfully subscribed to newsletter.',
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def unsubscribe(self, request, pk=None):
        subscriber = self.get_object()
        subscriber.unsubscribe()
        return Response({'success': True, 'message': 'Successfully unsubscribed.'})


class EmailCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = EmailCampaignSerializer
    permission_classes = [CanManageMarketing]
    queryset = EmailCampaign.objects.all()

    @action(detail=True, methods=['post'])
    def send_campaign(self, request, pk=None):
        campaign = self.get_object()
        if campaign.status != 'draft':
            return Response({
                'success': False,
                'error': {'message': 'Only draft campaigns can be sent.'}
            }, status=400)

        subscribers = Newsletter.objects.filter(is_active=True, confirmed=True)
        campaign.total_recipients = subscribers.count()
        campaign.status = 'sending'
        campaign.save(update_fields=['status', 'total_recipients', 'updated_at'])

        from .tasks import send_email_campaign
        send_email_campaign.delay(str(campaign.id))

        return Response({'success': True, 'message': 'Campaign is being sent.'})

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        campaign = self.get_object()
        return Response({
            'success': True,
            'stats': {
                'total_recipients': campaign.total_recipients,
                'total_sent': campaign.total_sent,
                'total_opened': campaign.total_opened,
                'total_clicked': campaign.total_clicked,
                'total_bounced': campaign.total_bounced,
                'total_unsubscribed': campaign.total_unsubscribed,
                'open_rate': campaign.open_rate,
                'click_rate': campaign.click_rate,
            }
        })


class LoyaltyProgramViewSet(viewsets.ModelViewSet):
    serializer_class = LoyaltyProgramSerializer
    permission_classes = [CanManageMarketing]
    queryset = LoyaltyProgram.objects.all()


class ReferralProgramViewSet(viewsets.ModelViewSet):
    serializer_class = ReferralProgramSerializer
    permission_classes = [CanManageMarketing]
    queryset = ReferralProgram.objects.all()
