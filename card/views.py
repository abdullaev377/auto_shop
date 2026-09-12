from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Card, CardItem
from product.models import Product
from .serializer import CardSerializer


class CardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_card(self, user):
        card, _ = Card.objects.get_or_create(user=user)
        return card

    def get(self, request):
        return Response(CardSerializer(self.get_card(request.user)).data)

    def post(self, request):
        product = Product.objects.filter(pk=request.data.get('product'), is_active=True, is_deleted=False).first()
        if not product:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            count = int(request.data.get('count', 1))
        except (TypeError, ValueError):
            return Response({'detail': 'count must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        if count < 1:
            return Response({'detail': 'count must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        if count > product.quantity:
            return Response({'detail': 'Requested quantity is not available'}, status=status.HTTP_400_BAD_REQUEST)
        card = self.get_card(request.user)
        item, created = CardItem.objects.get_or_create(card=card, product=product, defaults={'count': count})
        if not created:
            if item.count + count > product.quantity:
                return Response({'detail': 'Requested quantity is not available'}, status=status.HTTP_400_BAD_REQUEST)
            item.count += count
            item.save(update_fields=['count'])
        return Response(CardSerializer(card).data, status=status.HTTP_201_CREATED)


class CardItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        deleted, _ = CardItem.objects.filter(pk=pk, card__user=request.user).delete()
        if not deleted:
            return Response({'detail': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        item = CardItem.objects.filter(pk=pk, card__user=request.user).first()
        if not item:
            return Response({'detail': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            count = int(request.data.get('count', item.count))
        except (TypeError, ValueError):
            return Response({'detail': 'count must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        if count < 1:
            return Response({'detail': 'count must be positive'}, status=status.HTTP_400_BAD_REQUEST)
        if count > item.product.quantity:
            return Response({'detail': 'Requested quantity is not available'}, status=status.HTTP_400_BAD_REQUEST)
        item.count = count
        item.save(update_fields=['count'])
        return Response(CardSerializer(item.card).data)
        

