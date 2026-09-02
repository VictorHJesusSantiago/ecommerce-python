from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import TimeStampedModel, UUIDModel, SoftDeleteModel


class Review(UUIDModel, TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reviews'
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='reviews'
    )
    order_item = models.ForeignKey(
        'orders.OrderItem', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviews'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True, default='')
    body = models.TextField()
    pros = models.TextField(blank=True, default='', help_text='What you liked')
    cons = models.TextField(blank=True, default='', help_text='What could be improved')
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    admin_reply = models.TextField(blank=True, default='')
    admin_reply_at = models.DateTimeField(null=True, blank=True)
    admin_reply_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='review_replies'
    )

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['user', 'product']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['user', 'product']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name} ({self.rating}/5)"

    def approve(self):
        self.is_approved = True
        self.save(update_fields=['is_approved', 'updated_at'])
        self.product.update_rating()

    def admin_reply(self, reply_text, replied_by):
        from django.utils import timezone
        self.admin_reply = reply_text
        self.admin_reply_by = replied_by
        self.admin_reply_at = timezone.now()
        self.save(update_fields=['admin_reply', 'admin_reply_by', 'admin_reply_at', 'updated_at'])


class ReviewImage(UUIDModel, TimeStampedModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/%Y/%m/')
    alt_text = models.CharField(max_length=255, blank=True, default='')
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Review Image'
        verbose_name_plural = 'Review Images'
        ordering = ['sort_order']

    def __str__(self):
        return f"Image for review {self.review.pk}"

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)


class ReviewVote(UUIDModel, TimeStampedModel):
    VOTE_TYPES = [
        ('helpful', 'Helpful'),
        ('not_helpful', 'Not Helpful'),
    ]
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=20, choices=VOTE_TYPES)

    class Meta:
        verbose_name = 'Review Vote'
        verbose_name_plural = 'Review Votes'
        unique_together = ['review', 'user']

    def __str__(self):
        return f"{self.user.email} voted {self.vote_type} on review {self.review.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.vote_type == 'helpful':
            self.review.helpful_count = self.review.votes.filter(vote_type='helpful').count()
        else:
            self.review.not_helpful_count = self.review.votes.filter(vote_type='not_helpful').count()
        self.review.save(update_fields=['helpful_count', 'not_helpful_count'])


class ReviewReport(UUIDModel, TimeStampedModel):
    REASONS = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate'),
        ('fake', 'Fake Review'),
        ('offensive', 'Offensive'),
        ('other', 'Other'),
    ]
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REASONS)
    description = models.TextField(blank=True, default='')
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resolved_reports'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Review Report'
        verbose_name_plural = 'Review Reports'
        unique_together = ['review', 'user']

    def __str__(self):
        return f"Report for review {self.review.pk}"

    def resolve(self, resolved_by=None):
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_by = resolved_by
        self.resolved_at = timezone.now()
        self.save(update_fields=['is_resolved', 'resolved_by', 'resolved_at', 'updated_at'])


class ReviewSummary(UUIDModel):
    product = models.OneToOneField(
        'products.Product', on_delete=models.CASCADE,
        related_name='review_summary'
    )
    total_reviews = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_1_count = models.PositiveIntegerField(default=0)
    rating_2_count = models.PositiveIntegerField(default=0)
    rating_3_count = models.PositiveIntegerField(default=0)
    rating_4_count = models.PositiveIntegerField(default=0)
    rating_5_count = models.PositiveIntegerField(default=0)
    verified_count = models.PositiveIntegerField(default=0)
    with_images_count = models.PositiveIntegerField(default=0)
    would_recommend = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Review Summary'
        verbose_name_plural = 'Review Summaries'

    def __str__(self):
        return f"Summary for {self.product.name}"

    def update(self):
        reviews = Review.objects.filter(product=self.product, is_approved=True)
        self.total_reviews = reviews.count()
        if self.total_reviews > 0:
            from django.db.models import Avg
            self.avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        self.rating_1_count = reviews.filter(rating=1).count()
        self.rating_2_count = reviews.filter(rating=2).count()
        self.rating_3_count = reviews.filter(rating=3).count()
        self.rating_4_count = reviews.filter(rating=4).count()
        self.rating_5_count = reviews.filter(rating=5).count()
        self.verified_count = reviews.filter(is_verified_purchase=True).count()
        self.with_images_count = reviews.filter(images__isnull=False).distinct().count()
        self.save()
