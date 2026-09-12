from django.db.models import Q
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import IsSellerOrManager, IsOwnerOrManager
from .models import Product
from .serilizer import ProductSerializer


class CreateProduct(APIView):
    permission_classes = [IsSellerOrManager]

    def post(self, request):
        serializer = ProductSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(
            {
                'msg': 'Product created',
                'status': status.HTTP_201_CREATED,
                'product': serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class DetailProduct(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        product = (
            Product.objects
            .select_related('category', 'user')
            .prefetch_related(
                'images',
                'product_views',
                'product_comments',
            )
            .filter(
                pk=pk,
                is_deleted=False,
                is_active=True,
            )
            .first()
        )

        if product is None:
            return Response(
                {
                    'msg': 'Product not found',
                    'status': status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProductSerializer(
            product,
            context={'request': request},
        )

        return Response(
            {
                'msg': 'Product',
                'status': status.HTTP_200_OK,
                'product': serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ListProduct(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        products = (
            Product.objects
            .select_related('category', 'user')
            .prefetch_related('images')
            .filter(
                is_deleted=False,
                is_active=True,
            )
        )

        query = request.query_params.get('search')

        if query:
            products = products.filter(
                Q(title__icontains=query)
                | Q(brand__icontains=query)
                | Q(model_name__icontains=query)
                | Q(short_desc__icontains=query)
                | Q(desc__icontains=query)
                | Q(location__icontains=query)
            )

        for field in (
            'brand',
            'model_name',
            'year',
            'fuel_type',
            'transmission',
            'body_type',
            'location',
            'category_id',
        ):
            value = request.query_params.get(field)

            if value:
                products = products.filter(
                    **{field: value}
                )

        for field in (
            'price',
            'mileage',
            'year',
        ):
            for suffix in ('min', 'max'):
                value = request.query_params.get(
                    f'{field}_{suffix}'
                )

                if value:
                    lookup = (
                        'gte'
                        if suffix == 'min'
                        else 'lte'
                    )

                    products = products.filter(
                        **{
                            f'{field}__{lookup}': value
                        }
                    )

        ordering = request.query_params.get(
            'ordering',
            '-created_at',
        )

        allowed_ordering = {
            'created_at',
            '-created_at',
            'price',
            '-price',
            'year',
            '-year',
            'mileage',
            '-mileage',
            'brand',
            '-brand',
        }

        products = products.order_by(
            ordering
            if ordering in allowed_ordering
            else '-created_at'
        )

        paginator = PageNumberPagination()
        paginator.page_size = 12
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 48

        page = paginator.paginate_queryset(
            products,
            request,
        )

        serializer = ProductSerializer(
            page,
            many=True,
            context={'request': request},
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class UpdateProduct(APIView):
    permission_classes = [IsOwnerOrManager]

    def put(self, request, pk):
        product = Product.objects.filter(pk=pk).first()

        if not product:
            return Response(
                {
                    'msg': 'Product not found',
                    'status': status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(
            request,
            product,
        )

        serializer = ProductSerializer(
            instance=product,
            data=request.data,
            context={'request': request},
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'msg': 'Product updated',
                'status': status.HTTP_200_OK,
                'product': serializer.data,
            }
        )


class DeactiveProduct(APIView):
    permission_classes = [IsOwnerOrManager]

    def patch(self, request, pk):
        product = Product.objects.filter(pk=pk).first()

        if not product:
            return Response(
                {
                    'msg': 'Product not found',
                    'status': status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(
            request,
            product,
        )

        product.is_active = False

        product.save(
            update_fields=[
                'is_active',
                'updated_at',
            ]
        )

        return Response(
            {
                'msg': 'Product deactivated',
                'status': status.HTTP_200_OK,
            }
        )


class ActiveProduct(APIView):
    permission_classes = [IsOwnerOrManager]

    def patch(self, request, pk):
        product = Product.objects.filter(pk=pk).first()

        if not product:
            return Response(
                {
                    'msg': 'Product not found',
                    'status': status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(
            request,
            product,
        )

        product.is_active = True

        product.save(
            update_fields=[
                'is_active',
                'updated_at',
            ]
        )

        return Response(
            {
                'msg': 'Product activated',
                'status': status.HTTP_200_OK,
            }
        )


class DeleteProduct(APIView):
    permission_classes = [IsOwnerOrManager]

    def delete(self, request, pk):
        product = Product.objects.filter(pk=pk).first()

        if not product:
            return Response(
                {
                    'msg': 'Product not found',
                    'status': status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(
            request,
            product,
        )

        product.is_deleted = True
        product.is_active = False

        product.save(
            update_fields=[
                'is_deleted',
                'is_active',
                'updated_at',
            ]
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )