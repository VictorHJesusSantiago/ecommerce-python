from rest_framework import serializers
from .models import Review, ReviewImage, ReviewVote, ReviewReport, ReviewSummary


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'alt_text', 'sort_order']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    images = ReviewImageSerializer(many=True, read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField(read_only=True)
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_email', 'user_name', 'product', 'rating',
            'title', 'body', 'pros', 'cons', 'is_verified_purchase',
            'is_approved', 'helpful_count', 'not_helpful_count',
            'admin_reply', 'admin_reply_at', 'images', 'user_vote',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'is_verified_purchase', 'is_approved',
            'helpful_count', 'not_helpful_count', 'admin_reply',
            'admin_reply_at', 'created_at', 'updated_at',
        ]

    def get_user_name(self, obj):
        return obj.user.full_name

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = ReviewVote.objects.filter(review=obj, user=request.user).first()
            if vote:
                return vote.vote_type
        return None


class ReviewCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    title = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')
    body = serializers.CharField()
    pros = serializers.CharField(required=False, allow_blank=True, default='')
    cons = serializers.CharField(required=False, allow_blank=True, default='')


class ReviewVoteSerializer(serializers.Serializer):
    vote_type = serializers.ChoiceField(choices=['helpful', 'not_helpful'])


class ReviewReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReport
        fields = ['id', 'review', 'reason', 'description', 'is_resolved', 'created_at']
        read_only_fields = ['id', 'is_resolved', 'created_at']


class ReviewSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewSummary
        fields = [
            'id', 'total_reviews', 'avg_rating', 'rating_1_count',
            'rating_2_count', 'rating_3_count', 'rating_4_count',
            'rating_5_count', 'verified_count', 'with_images_count',
            'would_recommend',
        ]
