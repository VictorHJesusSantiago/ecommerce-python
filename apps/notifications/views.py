from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import (
    Notification, EmailTemplate, NotificationPreference,
    SMSLog, PushNotificationLog
)
from .serializers import (
    NotificationSerializer, NotificationListSerializer, EmailTemplateSerializer,
    NotificationPreferenceSerializer, SMSLogSerializer, PushNotificationLogSerializer
)
from apps.common.pagination import SmallResultsSetPagination


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'success': True, 'message': 'Notification marked as read.'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({'success': True, 'message': 'All notifications marked as read.'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return Response({'success': True, 'unread_count': count})

    @action(detail=False, methods=['get'])
    def summary(self, request):
        user = request.user
        total = Notification.objects.filter(user=user).count()
        unread = Notification.objects.filter(user=user, is_read=False).count()
        by_type = {}
        for ntype, label in Notification.NOTIFICATION_TYPES:
            by_type[ntype] = Notification.objects.filter(
                user=user, notification_type=ntype, is_read=False
            ).count()
        return Response({
            'success': True,
            'summary': {
                'total': total,
                'unread': unread,
                'by_type': by_type,
            }
        })


class EmailTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = EmailTemplate.objects.all()


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pref, _ = NotificationPreference.objects.get_or_create(user=self.request.user)
        return pref


class SMSLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SMSLogSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = SMSLog.objects.all()


class PushNotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PushNotificationLogSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = PushNotificationLog.objects.all()
