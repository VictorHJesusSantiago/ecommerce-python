from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Page, MenuItem, Menu, FAQ, Testimonial, Partner, ContactMessage, Subscriber
from .serializers import (
    PageSerializer, PageListSerializer, MenuItemSerializer, MenuSerializer,
    FAQSerializer, TestimonialSerializer, PartnerSerializer,
    ContactMessageSerializer, ContactMessageCreateSerializer, SubscriberSerializer
)
from apps.common.permissions import IsAdminUser, CanManageCMS
from apps.common.pagination import StandardResultsSetPagination


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    permission_classes = [CanManageCMS]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return Page.objects.all()
        return Page.objects.filter(is_published=True, is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return PageListSerializer
        return PageSerializer

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def published(self, request):
        pages = Page.objects.filter(is_published=True, is_active=True, parent=None)
        serializer = PageListSerializer(pages, many=True)
        return Response({'success': True, 'pages': serializer.data})

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def by_slug(self, request):
        slug = request.query_params.get('slug')
        if not slug:
            return Response({'success': False, 'error': {'message': 'Slug is required.'}}, status=400)
        try:
            page = Page.objects.get(slug=slug, is_published=True, is_active=True)
            serializer = PageSerializer(page)
            return Response({'success': True, 'page': serializer.data})
        except Page.DoesNotExist:
            return Response({'success': False, 'error': {'message': 'Page not found.'}}, status=404)


class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer
    permission_classes = [CanManageCMS]
    queryset = Menu.objects.all()

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def items(self, request, pk=None):
        menu = self.get_object()
        items = menu.items.filter(parent=None, is_active=True)
        serializer = MenuItemSerializer(items, many=True)
        return Response({'success': True, 'items': serializer.data})


class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return FAQ.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [CanManageCMS()]


class TestimonialViewSet(viewsets.ModelViewSet):
    serializer_class = TestimonialSerializer
    permission_classes = [CanManageCMS]

    def get_queryset(self):
        return Testimonial.objects.filter(is_active=True)


class PartnerViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerSerializer
    permission_classes = [CanManageCMS]

    def get_queryset(self):
        return Partner.objects.filter(is_active=True)


class ContactMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ContactMessage.objects.all()
        return ContactMessage.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return ContactMessageCreateSerializer
        return ContactMessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        msg = ContactMessage.objects.create(**serializer.validated_data)
        from apps.notifications.tasks import send_notification
        if request.user.is_authenticated:
            send_notification.delay(
                user_id=request.user.id,
                notification_type='system',
                title='Contact message received',
                message=f'Your message "{msg.subject}" has been received.',
            )
        return Response({
            'success': True,
            'message': 'Your message has been sent.',
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def mark_read(self, request, pk=None):
        msg = self.get_object()
        msg.status = 'read'
        msg.save(update_fields=['status', 'updated_at'])
        return Response({'success': True, 'message': 'Message marked as read.'})


class SubscriberViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriberSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Subscriber.objects.all()
        return Subscriber.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def subscribe(self, request):
        serializer = SubscriberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscriber, created = Subscriber.objects.get_or_create(
            email=serializer.validated_data['email'],
            defaults={
                'first_name': serializer.validated_data.get('first_name', ''),
                'source': 'api',
            }
        )
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=['is_active'])
        return Response({
            'success': True,
            'message': 'Successfully subscribed.',
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
