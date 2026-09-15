import pytest
from apps.cms.models import Page, FAQ, ContactMessage


@pytest.mark.django_db
class TestPageModel:
    def test_page_creation(self):
        page = Page.objects.create(
            title='About Us',
            slug='about-us',
            content='We are an e-commerce company.',
            is_published=True,
        )
        assert page.title == 'About Us'
        assert page.slug == 'about-us'


@pytest.mark.django_db
class TestFAQModel:
    def test_faq_creation(self):
        faq = FAQ.objects.create(
            question='How do I return an item?',
            answer='You can return items within 30 days.',
            category='returns',
        )
        assert faq.question == 'How do I return an item?'


@pytest.mark.django_db
class TestContactMessage:
    def test_contact_message(self):
        msg = ContactMessage.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Help needed',
            message='I need help with my order.',
        )
        assert msg.status == 'new'
