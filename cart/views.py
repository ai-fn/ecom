from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Sum
from api.serializers import SimplifiedCartItemSerializer

from rest_framework import status, permissions, viewsets, views
from rest_framework.response import Response
from rest_framework.decorators import action

from account.models import CustomUser
from cart.models import Order, ProductsInOrder, CartItem
from api.serializers import CartItemSerializer, OrderSerializer
from api.serializers import ProductDetailSerializer
from shop.models import Product
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


def add_to_cart(request):
    path = request.GET.get("next")

    if request.method == "POST":
        product_id = request.GET.get("product_id")

        if "cart" not in request.session:
            request.session["cart"] = {}

        cart = request.session.get("cart")

        if product_id in cart:
            cart[product_id]["quantity"] += 1

        else:
            cart[product_id] = {"quantity": 1}

    request.session.modified = True
    return redirect(path)


class OrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        customer = request.user
        cart_items = CartItem.objects.filter(customer=customer)

        if not cart_items.exists():
            return Response(
                {"error": "Корзина пуста."}, status=status.HTTP_404_NOT_FOUND
            )

        with transaction.atomic():
            order = Order.objects.create(customer=customer)
            for item in cart_items:
                ProductsInOrder.objects.create(
                    order=order, product=item.product, quantity=item.quantity
                )
                item.delete()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "cartitemsdetail":
            return ProductDetailSerializer

        return super().get_serializer_class()

    @extend_schema(
        request=CartItemSerializer(many=True),
        responses={
            201: SimplifiedCartItemSerializer(many=True)
        },  # Change response serializer here
        description="Merge provided cart items with the existing cart, then return the updated cart.",
    )
    def create(self, request, *args, **kwargs):
        # Get current user's cart items
        existing_cart_items = CartItem.objects.filter(customer=request.user)

        # Transform existing cart items into a dictionary using product_id for easier processing
        existing_cart_dict = {item.product.id: item for item in existing_cart_items}

        # Process incoming data
        for incoming_item in request.data:
            product_id = incoming_item.get("product_id")
            new_quantity = incoming_item.get("quantity", 0)

            # Update existing item or create a new one
            if product_id in existing_cart_dict:
                # Update quantity of existing item
                existing_item = existing_cart_dict[product_id]
                existing_item.quantity = new_quantity  # Add to the existing quantity
                existing_item.save()
            else:
                # Create a new cart item for this user
                CartItem.objects.create(
                    customer=request.user, product_id=product_id, quantity=new_quantity
                )

        # After updating the cart, return the updated cart items for the user
        updated_cart_items = CartItem.objects.filter(customer=request.user)
        response_serializer = SimplifiedCartItemSerializer(
            updated_cart_items, many=True
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Retrieve cart items details",
        responses={200: ProductDetailSerializer(many=True)},
        methods=["GET"],
        description="Returns a detailed list of products in the user's cart",
    )
    @action(detail=False, methods=["get"])
    def cartitemsdetail(self, request):
        id_lists = list(
            CartItem.objects.filter(customer=request.user).values_list(
                "product", flat=True
            )
        )
        queryset = Product.objects.filter(id__in=id_lists)

        if queryset.exists():

            serialized_data = self.get_serializer(queryset, many=True).data

            return Response(serialized_data, status=status.HTTP_200_OK)

        return Response(
            {"message": "Cart items for user with pk %s not found" % request.user.pk},
            status=status.HTTP_404_NOT_FOUND,
        )

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
            return Response(
                {
                    "count": queryset.aggregate(total_quantity=Sum("quantity"))[
                        "total_quantity"
                    ]
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"messsage": "Cart items for user with pk %s not found" % request.user.pk}
        )
