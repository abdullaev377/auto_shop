from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Comment, Saved, ProductView
from .serializer import CommentSerializer
from product.models import Product


class CommentListCreateView(APIView):
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

	def get(self, request, product_id):
		return Response(CommentSerializer(Comment.objects.filter(product_id=product_id), many=True).data)

	def post(self, request, product_id):
		serializer = CommentSerializer(data={**request.data, 'product': product_id})
		serializer.is_valid(raise_exception=True)
		serializer.save(user=request.user)
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	def delete(self, request, product_id):
		comment = Comment.objects.filter(product_id=product_id, user=request.user, pk=request.data.get('id')).first()
		if not comment:
			return Response({'detail': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
		comment.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class SavedView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, product_id=None):
		products = Product.objects.filter(saved_by__user=request.user, is_deleted=False).prefetch_related('images')
		from product.serilizer import ProductSerializer
		return Response(ProductSerializer(products, many=True, context={'request': request}).data)

	def post(self, request, product_id):
		product = Product.objects.filter(pk=product_id, is_deleted=False).first()
		if not product:
			return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
		saved, created = Saved.objects.get_or_create(user=request.user, product=product)
		if not created:
			saved.delete()
		return Response({'is_favorite': created})


class ProductViewCreate(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request, product_id):
		product = Product.objects.filter(pk=product_id).first()
		if not product:
			return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
		ProductView.objects.update_or_create(product=product, user=request.user if request.user.is_authenticated else None)
		return Response(status=status.HTTP_204_NO_CONTENT)
