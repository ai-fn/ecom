from rest_framework import generics, permissions, response, status
from api.serializers import ProductCatalogSerializer
from shop.models import Product


class SimilarProducts(generics.GenericAPIView):
    
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductCatalogSerializer
    queryset = Product.objects.all()

    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist as err:
            return response.Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)
        
        serialized_products = self.serializer_class(product.similar_products, many=True).data
        return response.Response({'similar_products': serialized_products}, status=status.HTTP_200_OK)
