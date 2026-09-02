from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Review, ReviewImage, ReviewVote, ReviewReport, ReviewSummary
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, ReviewVoteSerializer,
    ReviewReportSerializer, ReviewSummarySerializer, ReviewImageSerializer
)
from apps.common.permissions import IsAdminUser, IsReviewOwnerOrAdmin
from apps.common.pagination import ReviewPagination
from apps.common.signals import review_created


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ReviewPagination

    def get_queryset(self):
        qs = Review.objects.filter(is_approved=True).select_related('user', 'product')
        product = self.request.query_params.get('product')
        if product:
            qs = qs.filter(product_id=product)
        rating = self.request.query_params.get('rating')
        if rating:
            qs = qs.filter(rating=rating)
        verified_only = self.request.query_params.get('verified')
        if verified_only and verified_only.lower() == 'true':
            qs = qs.filter(is_verified_purchase=True)
        sort = self.request.query_params.get('sort', '-created_at')
        if sort == 'helpful':
            qs = qs.order_by('-helpful_count')
        elif sort == 'rating_high':
            qs = qs.order_by('-rating')
        elif sort == 'rating_low':
            qs = qs.order_by('rating')
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'summary']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.products.models import Product
        product = Product.objects.get(pk=serializer.validated_data['product_id'])

        existing = Review.objects.filter(user=request.user, product=product).first()
        if existing:
            return Response({
                'success': False,
                'error': {'message': 'You have already reviewed this product.'}
            }, status=status.HTTP_400_BAD_REQUEST)

        order_item = None
        if Review.objects.filter(
            user=request.user, product=product, is_verified_purchase=True
        ).exists():
            pass

        review = Review.objects.create(
            user=request.user,
            product=product,
            order_item=order_item,
            rating=serializer.validated_data['rating'],
            title=serializer.validated_data.get('title', ''),
            body=serializer.validated_data['body'],
            pros=serializer.validated_data.get('pros', ''),
            cons=serializer.validated_data.get('cons', ''),
            is_verified_purchase=order_item is not None,
        )

        review_created.send(sender=Review, review=review, product=product)

        return Response({
            'success': True,
            'message': 'Review submitted for approval.',
            'review': ReviewSerializer(review, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vote, created = ReviewVote.objects.update_or_create(
            review=review, user=request.user,
            defaults={'vote_type': serializer.validated_data['vote_type']}
        )

        return Response({
            'success': True,
            'message': 'Vote recorded.',
            'helpful_count': review.helpful_count,
            'not_helpful_count': review.not_helpful_count,
        })

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report, created = ReviewReport.objects.get_or_create(
            review=review, user=request.user,
            defaults={
                'reason': serializer.validated_data['reason'],
                'description': serializer.validated_data.get('description', ''),
            }
        )
        if not created:
            return Response({
                'success': False,
                'error': {'message': 'You have already reported this review.'}
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': True, 'message': 'Report submitted.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def pending(self, request):
        reviews = Review.objects.filter(is_approved=False).select_related('user', 'product')
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response({'success': True, 'reviews': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.approve()
        return Response({'success': True, 'message': 'Review approved.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reply(self, request, pk=None):
        review = self.get_object()
        reply_text = request.data.get('reply', '')
        if not reply_text:
            return Response({'success': False, 'error': {'message': 'Reply text is required.'}}, status=400)
        review.admin_reply(reply_text, request.user)
        return Response({'success': True, 'message': 'Reply added.'})


class ReviewSummaryView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ReviewSummarySerializer

    def get_object(self):
        product_id = self.kwargs['product_pk']
        summary, _ = ReviewSummary.objects.get_or_create(
            product_id=product_id,
            defaults={'total_reviews': 0, 'avg_rating': 0}
        )
        summary.update()
        return summary
