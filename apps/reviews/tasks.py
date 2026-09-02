from celery import shared_task


@shared_task
def update_review_summaries():
    from .models import ReviewSummary
    summaries = ReviewSummary.objects.all()
    updated = 0
    for summary in summaries:
        summary.update()
        updated += 1
    return updated
