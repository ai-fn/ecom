from rest_framework import generics, permissions, response, status
from api.serializers import ProductCatalogSerializer
from shop.models import Product


class SimilarProducts(generics.GenericAPIView):
    
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductCatalogSerializer
    queryset = Product.objects.all()

    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist as err:
            return response.Response({'error': err}, status=status.HTTP_400_BAD_REQUEST)
        
        serialized_products = self.serializer_class(product.similar_products, many=True).data
        return response.Response({'products': serialized_products}, status=status.HTTP_200_OK)
