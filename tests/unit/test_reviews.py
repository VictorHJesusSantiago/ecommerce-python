import pytest
from apps.reviews.models import Review, ReviewVote, ReviewReport


@pytest.mark.django_db
class TestReviewModel:
    def test_review_creation(self, user, product):
        review = Review.objects.create(
            user=user,
            product=product,
            rating=5,
            title='Great product!',
            body='I love this product. It works perfectly.',
            is_approved=True,
        )
        assert review.rating == 5
        assert review.is_approved is True

    def test_review_vote(self, user, product):
        review = Review.objects.create(
            user=user,
            product=product,
            rating=4,
            body='Good product.',
        )
        from django.contrib.auth import get_user_model
        User = get_user_model()
        voter = User.objects.create_user(email='voter@test.com', password='pass')
        vote = ReviewVote.objects.create(
            review=review,
            user=voter,
            vote_type='helpful',
        )
        review.refresh_from_db()
        assert review.helpful_count == 1

    def test_review_report(self, user, product):
        review = Review.objects.create(
            user=user,
            product=product,
            rating=1,
            body='Bad product.',
        )
        from django.contrib.auth import get_user_model
        User = get_user_model()
        reporter = User.objects.create_user(email='reporter@test.com', password='pass')
        report = ReviewReport.objects.create(
            review=review,
            user=reporter,
            reason='spam',
        )
        assert report.is_resolved is False
        report.resolve()
        assert report.is_resolved is True
