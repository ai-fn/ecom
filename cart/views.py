from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Sum

from rest_framework import status, permissions, viewsets, views
from rest_framework.response import Response 
from rest_framework.decorators import action

from account.models import CustomUser
from cart.models import Order, ProductsInOrder, CartItem
from api.serializers import CartItemSerializer, OrderSerializer
from api.serializers import ProductDetailSerializer
from shop.models import Product


def add_to_cart(request):
    path = request.GET.get('next')

    if request.method == 'POST':
        product_id = request.GET.get('product_id')

        if 'cart' not in request.session:
            request.session['cart'] = {}

        cart = request.session.get('cart')

        if product_id in cart:
            cart[product_id]['quantity'] += 1

        else:
            cart[product_id] = {
                'quantity': 1
            }

    request.session.modified = True
    return redirect(path)


# def view_cart(request):
#     path = request.GET.get('next')

#     context = {
#         'next': path,
#     }

#     cart = request.session.get('cart', None)

#     if cart:
#         products = {}
#         product_list = Product.objects.filter(pk__in=cart.keys()).values('id', 'title', 'description')

#         for product in product_list:
#             products[str(product['id'])] = product

#         for key in cart.keys():
#             cart[key]['product'] = products[key]

#         context['cart'] = cart

#     return render(request, 'cart/cart.html', context)


# @login_required(login_url='login')
# def view_order(request):
#     if request.method == 'POST':
#         user_id = request.user.pk
#         customer = CustomUser.objects.get(pk=user_id)

#         cart = request.session['cart']

#         if len(cart) > 0:
#             order = Order.objects.create(customer=customer)

#             for key, value in cart.items():
#                 product = Product.objects.get(pk=key)
#                 quantity = value['quantity']
#                 ProductsInOrder.objects.create(order=order, product=product, quantity=quantity)

#             request.session['cart'] = {}
#             request.session.modified = True

#             messages.success(request, 'Заказ принят')

#     return redirect('cart:cart')

class OrderViewSet(viewsets.ModelViewSet):
    
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        customer = request.user
        cart_items = CartItem.objects.filter(customer=customer)

        if not cart_items.exists():
            return  Response({"error": "Корзина пуста."}, status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
            order = Order.objects.create(customer=customer)
            for item in cart_items:
                ProductsInOrder.objects.create(order=order, product=item.product, quantity=item.quantity)
                item.delete()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'cartitemsdetail':
            return ProductDetailSerializer
        
        return super().get_serializer_class()

    @action(detail=False, methods=["get"])
    def cartitemsdetail(self, request):
        id_lists = list(CartItem.objects.filter(customer=request.user).values_list("product", flat=True))
        queryset = Product.objects.filter(id__in=id_lists)

        if queryset.exists():

            serialized_data = self.get_serializer(queryset, many=True).data

            return Response(serialized_data, status=status.HTTP_200_OK)
        
        return Response({'message': 'Cart items for user with pk %s not found' % request.user.pk}, status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        # Returns only the cart items that belong to the current user.
        return CartItem.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        # Associates the new cart item with the current user.
        serializer.save(customer=self.request.user)


class CartCountView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = CartItem.objects.filter(customer=request.user)
        if queryset.exists():
            return Response({'count': queryset.aggregate(total_quantity=Sum("quantity"))['total_quantity']}, status=status.HTTP_200_OK)
        
        return Response({'messsage': 'Cart items for user with pk %s not found' % request.user.pk})
