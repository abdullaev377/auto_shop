from django.urls import path

from .views import (
    CreateProduct,
    DetailProduct,
    ListProduct,
    UpdateProduct,
    DeactiveProduct,
    ActiveProduct,
    DeleteProduct,
)


urlpatterns = [
    path(
        '',
        ListProduct.as_view(),
        name='product-list',
    ),

    path(
        'create/',
        CreateProduct.as_view(),
        name='product-create',
    ),

    path(
        '<uuid:pk>/',
        DetailProduct.as_view(),
        name='product-detail',
    ),

    path(
        '<uuid:pk>/update/',
        UpdateProduct.as_view(),
        name='product-update',
    ),

    path(
        '<uuid:pk>/deactivate/',
        DeactiveProduct.as_view(),
        name='product-deactivate',
    ),

    path(
        '<uuid:pk>/activate/',
        ActiveProduct.as_view(),
        name='product-activate',
    ),

    path(
        '<uuid:pk>/delete/',
        DeleteProduct.as_view(),
        name='product-delete',
    ),
]