from django.urls import path
from .views import CategoryListCreateView, CategoryDetailView

urlpatterns = [
    path('', CategoryListCreateView.as_view()),
    path('<uuid:pk>/', CategoryDetailView.as_view()),
]