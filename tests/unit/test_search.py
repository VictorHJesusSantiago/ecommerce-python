import pytest
from apps.search.models import SearchQuery, PopularSearch, SavedSearch


@pytest.mark.django_db
class TestSearchModel:
    def test_search_query(self, user):
        query = SearchQuery.objects.create(
            user=user,
            query='wireless headphones',
            results_count=15,
        )
        assert query.query == 'wireless headphones'

    def test_popular_search(self):
        ps = PopularSearch.objects.create(query='headphones', count=100)
        assert ps.count == 100

    def test_record_search(self):
        PopularSearch.record_search('test query')
        PopularSearch.record_search('test query')
        ps = PopularSearch.objects.get(query='test query')
        assert ps.count == 2

    def test_saved_search(self, user):
        saved = SavedSearch.objects.create(
            user=user,
            name='My Search',
            query='headphones',
        )
        assert saved.name == 'My Search'
