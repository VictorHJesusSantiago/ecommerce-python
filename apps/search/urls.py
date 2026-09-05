from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'search'

router = DefaultRouter()
router.register(r'popular-searches', views.PopularSearchViewSet, basename='popular-search')
router.register(r'saved-searches', views.SavedSearchViewSet, basename='saved-search')

urlpatterns = [
    path('search/', views.SearchView.as_view(), name='search'),
    path('autocomplete/', views.AutocompleteView.as_view(), name='autocomplete'),
    path('', include(router.urls)),
]
