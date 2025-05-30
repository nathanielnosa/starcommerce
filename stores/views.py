from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,serializers

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings

import requests

from . serializers import *
from . models import *
from .paystack import Paystack

# CATEGORY POST & GET
class CategoryView(APIView):
    def post(self,request):
        try:
            serializers = CategorySerializer(data = request.data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get(self,request):
        try:
            category = Category.objects.all()
            serializers = CategorySerializer(category,many=True)
            return Response(serializers.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# CATEGORY GET & PUT & DELETE
class CategoryDetailView(APIView):
    def get(self,request,id):
        try:
            category = get_object_or_404(Category,id=id)
            serializers = CategorySerializer(category)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self,request,id):
        try:
            category = get_object_or_404(Category,id=id)
            serializers = CategorySerializer(category,data=request.data, partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self,request,id):
        try:
            category = get_object_or_404(Category,id=id)
            category.delete()
            return Response({'message':'category deleted!'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# PRODUCT POST & GET
class ProductView(APIView):
    def post(self,request):
        try:
            serializers = ProductSerializer(data = request.data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get(self,request):
        try:
            product = Product.objects.all()
            serializers = ProductSerializer(product,many=True)
            return Response(serializers.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# PRODUCT GET & PUT & DELETE
class ProductDetailView(APIView):
    def get(self,request,id):
        try:
            product = get_object_or_404(Product,id=id)
            serializers = ProductSerializer(product)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self,request,id):
        try:
            product = get_object_or_404(Product,id=id)
            serializers = ProductSerializer(product,data=request.data, partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self,request,id):
        try:
            product = get_object_or_404(Product,id=id)
            product.delete()
            return Response({'message':'product deleted!'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# ADD TO CART
class AddToCartView(APIView):
    def post(self,request,id):
        try:
            # get the product
            product = get_object_or_404(Product,id=id)
            # get the cart id
            cart_id = request.session.get('cart_id',None)
            # use price or discount
            price = product.discount_price if product.discount_price else product.price
            with transaction.atomic():
                if cart_id:
                    cart = Cart.objects.filter(id=cart_id).first()
                    if cart is None:
                        cart = Cart.objects.create(total =0)
                        request.session['cart_id'] = cart.id
                    
                    this_product_in_cart = cart.cartproduct_set.filter(product=product)
                    # assigning cart to a user
                    if request.user.is_authenticated and hasattr(request.user,'profile'):
                        cart.profile = request.user.profile
                        cart.save()

                    if this_product_in_cart.exists():
                        cartproduct = this_product_in_cart.last()
                        cartproduct.quantity+=1
                        cartproduct.subtotal+=price
                        cartproduct.save()
                        # update cart
                        cart.total+=price
                        cart.save()
                        return Response({'message':'Item increase in cart'})

                    else:
                        cartproduct = CartProduct.objects.create(cart=cart,product=product,quantity=1,subtotal=price)
                        cartproduct.save()
                        # update our cart
                        cart.total+=price
                        cart.save()
                        return Response({'message':'Item added to cart'})
                else:
                    # create a cart
                    cart = Cart.objects.create(total=0)
                    request.session['cart_id'] = cart.id
                    cartproduct = CartProduct.objects.create(cart=cart,product=product,quantity=1,subtotal=price)
                    cartproduct.save()
                    # update our cart
                    cart.total+=price
                    cart.save()
                    return Response({'message':'New Item added to cart'})
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# ::: USERS CART ::::
class MyCartView(APIView):
    def get(self, request):
        try:
            cart_id = request.session.get('cart_id',None)
            if cart_id:
                cart = get_object_or_404(Cart,id = cart_id)
                # assigning cart to a user
                if request.user.is_authenticated and hasattr(request.user,'profile'):
                    cart.profile = request.user.profile
                    cart.save()
                serializers = CartSerializer(cart)
                return Response(serializers.data, status=status.HTTP_200_OK)
            return Response({"Message: Cart not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
#:::: MANAGE USER CART ::::
class ManageCartView(APIView):
    def post(self,request,id):
        action = request.data.get('action')
        try:
            cart_obj = get_object_or_404(CartProduct, id= id)
            cart = cart_obj.cart
             # use price or discount
            price = cart_obj.product.discount_price if cart_obj.product.discount_price else cart_obj.product.price
            
            if action == "inc":
                cart_obj.quantity +=1
                cart_obj.subtotal += price
                cart_obj.save()
                cart.total += price
                cart.save()
                return Response({"Message":"quantity increase"}, status=status.HTTP_200_OK)
            elif action == "dcr":
                cart_obj.quantity -=1
                cart_obj.subtotal -= price
                cart_obj.save()
                cart.total -= price
                cart.save()
                if cart_obj.quantity == 0:
                    cart_obj.delete()
                return Response({"Message":"quantity decrease"}, status=status.HTTP_200_OK)
            elif action == "rmv":
                cart.total -= price
                cart.save()
                cart_obj.delete()
                return Response({"Message":"item removed"}, status=status.HTTP_200_OK)
            
            return Response({"Message":"item not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#:::: CHECKOUT ::::
class CheckoutView(APIView):
    def post(self,request):
        cart_id = request.session.get('cart_id',None)
        if not cart_id:
            return Response({"Error":"Cart not found"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart_obj = get_object_or_404(Cart,id=cart_id)
        except Cart.DoesNotExist:
            return Response({"Error":"Cart does not exist"},status=status.HTTP_400_BAD_REQUEST)   
        
        serializers = CheckoutSerializer(data=request.data)
        if serializers.is_valid():
            order = serializers.save(
                cart = cart_obj,
                amount = cart_obj.total,
                subtotal = cart_obj.total,
                order_status = 'pending'
            )
            del request.session['cart_id']

            if order.payment_method == 'paystack':
                payment_url = reverse('payment', args=[order.id])
                return Response({'redirect url':payment_url}, status=status.HTTP_200_OK)
            return Response({"Message":"Order created successful"})
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)

# ::: PAYMENT VERIFICATION ::
class PaymentView(APIView):
    def get(self,request,id):
        try:
            order = get_object_or_404(Order,id=id)
        except Order.DoesNotExist:
            return Response({'Error':'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        # Create payment request
        url = "https://api.paystack.co/transaction/initialize"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        data = {
            "amount": order.amount * 100,
            "email": order.email,
            "reference": order.ref
        }

        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()

        if response_data["status"]:
            paystack_url = response_data["data"]["authorization_url"]

            return Response({
                'order': order.id,
                'total': order.amount_value(),
                'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
                'paystack_url': paystack_url
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)      


# :::: VERIFY PAYMENT
class VerifyPaymentView(APIView):
    def get(self,request,ref):
        try:
            order = get_object_or_404(Order,ref=ref)
            url = f'https://api.paystack.co/transaction/verify/{ref}'
            headers = {"Authorization":f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            response = requests.get(url,headers=headers)
            response_data = response.json()

            if response_data["status"] and response_data['data']['status'] == "success":
                order.payment_complete =True
                order.order_status = "complete"
                order.save()
                return Response({"Message":"Payment successful"}, status=status.HTTP_200_OK)
            elif response_data['data']['status']== "abandoned":
                order.order_status = "pending"
                order.save()
                return Response({"Message":"Payment not successful"}, status=status.HTTP_304_NOT_MODIFIED)
            else:
                return Response({"Error":"Payment Failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({"Error":"Invalid payment reference id"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            


    

