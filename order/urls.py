from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderStatusView,
)


urlpatterns = [
    path(
        '',
        OrderListCreateView.as_view(),
    ),

    path(
        '<uuid:pk>/',
        OrderDetailView.as_view(),
    ),

    path(
        '<uuid:pk>/status/',
        OrderStatusView.as_view(),
    ),
]