from django.urls import path
from .views import CommentListCreateView, SavedView, ProductViewCreate

urlpatterns = [
    path('product/<uuid:product_id>/', CommentListCreateView.as_view()),
    path('saved/', SavedView.as_view()),
    path('saved/<uuid:product_id>/', SavedView.as_view()),
    path('views/<uuid:product_id>/', ProductViewCreate.as_view()),
]