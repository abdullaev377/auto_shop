from rest_framework import generics, permissions
from shared.permissions import IsManager
from .models import Category
from .serializers import CategorySerializer


class CategoryListCreateView(generics.ListCreateAPIView):
	queryset = Category.objects.all().order_by('title')
	serializer_class = CategorySerializer

	def get_permissions(self):
		return [IsManager()] if self.request.method == 'POST' else [permissions.AllowAny()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	permission_classes = [IsManager]
