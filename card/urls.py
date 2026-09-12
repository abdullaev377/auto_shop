from django.urls import path
from .views import CardView, CardItemView

urlpatterns = [
    path('', CardView.as_view()),
    path('items/<uuid:pk>/', CardItemView.as_view()),
]