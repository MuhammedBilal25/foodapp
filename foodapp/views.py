from django.shortcuts import render,redirect
from foodapp.forms import RestaurantForm,RestaurantLoginForm,FoodItemForm,CustumerRegistrationForm,CustumerLoginForm
from django.views.generic import View,TemplateView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from foodapp.models import FoodItem,Restaurant,Cart,CartItem,Order,OrderItems
from django.contrib import messages
import razorpay
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from foodapp.decorators import signinrequired,owner_permission_required

KEY_ID="rzp_test_oCFtiK9xM2H3af"
KEY_SECRET="YWr76dRt69Km2Ld5rcwV5o1J"



# Create your views here.

class FirstView(TemplateView):
    template_name="basic_index.html"
    



# RESTURANT VIEWS====================================
class RestaurantSignUpView(View):
    def get(self,request,*args,**kwargs):
        form=RestaurantForm()
        return render(request,"restaurant_registration.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=RestaurantForm(request.POST,request.FILES)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['name'], password=form.cleaned_data['password'])
            restaurant = form.save(commit=False)
            restaurant.user = user
            restaurant.save()
            return redirect("restaurant-signin")
        else:
            return render(request,"restaurant_registration.html",{"form":form})

class RestaurantSignInView(View):
    def get(self, request, *args, **kwargs):
        form = RestaurantLoginForm()
        return render(request, "restaurant_signin.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = RestaurantLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and hasattr(user, 'restaurant'):  # Check if the user has a restaurant profile
                login(request, user)
                return redirect("restaurant-home") 
            else:
                return render(request, "restaurant_signin.html", {"form": form, "error_message": "Invalid username or password."})
        else:
            return render(request, "restaurant_signin.html", {"form": form})
        
class ResturantFoodItemListView(View):
    def get(self, request,*args, **kwargs):
        id=request.user.id
        rest=Restaurant.objects.get(user_id=id)
        qs=FoodItem.objects.filter(restaurant=rest)
        return render(request,"resturanthome.html",{"data":qs})


class FoodItemCreateView(View):
    def get(self, request,*args, **kwargs):
        form = FoodItemForm()
        return render(request, 'create_food_item.html', {'form': form})

    def post(self, request,*args,**kwargs):
        form = FoodItemForm(request.POST,request.FILES)
        if form.is_valid():
            form.instance.restaurant=request.user.restaurant
            form.save()
            return redirect('restaurant-home')
        else:
            return render(request, 'create_food_item.html', {'form': form})
        
class FoodItemupdateView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        form=FoodItemForm(instance=FoodItem.objects.get(id=id))
        return render(request,"food_edit.html",{"form":form})
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        form=FoodItemForm(request.POST,request.FILES,instance=FoodItem.objects.get(id=id))
        if form.is_valid():
            form.save()
            return redirect("restaurant-home")
        return render(request,"food_edit.html",{"form":form})
        

# -==========================CUSTUMER VIEWS==================
class SignupView(View):
    def get(self,request,*args,**kwargs):
        form=CustumerRegistrationForm()
        return render(request,"custumer_login.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=CustumerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("custumer-login")
        else:
            return render(request,"custumer_login.html",{"form":form})
        
class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=CustumerLoginForm
        return render(request,"custumer_login.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=CustumerLoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=u_name,password=pwd)
            if user_object:
                login(request,user_object)
                return redirect("custumer-home")
        messages.error(request,"invalid credential")
        return render(request,"custumer_login.html",{"form":form})
    
@method_decorator([signinrequired,never_cache],name="dispatch")   
class CustumerHomeView(View):
    def get(self,request,*args,**kwargs):
        qs=Restaurant.objects.all()
        return render(request,"custumer_homepage.html",{"data":qs})




@method_decorator([signinrequired,never_cache],name="dispatch")
class FoodItemListView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=FoodItem.objects.filter(restaurant=id,active=True)
        cart=Cart.objects.get(user=request.user)
        qss=CartItem.objects.filter(cart=cart)
        return render(request,"custumer_fooditemlist.html",{"data":qs,"cart":qss})

@method_decorator([signinrequired,never_cache],name="dispatch")
class AddToCartView(View):

    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        food_item_object=FoodItem.objects.get(id=id)
        CartItem.objects.create(
            food_item=food_item_object,
            cart=request.user.cart
        )
        rest_id=food_item_object.restaurant
        qs=FoodItem.objects.filter(restaurant=rest_id,active=True)
        cart=Cart.objects.get(user=request.user)
        qss=[]
        ci=cart.get_cart_items
        for c in ci:
            qss.append(c.food_item)
        return render(request,"custumer_fooditemlist.html",{"data":qs,"cart":qss})


@method_decorator([signinrequired,never_cache],name="dispatch")    
class BasketItemListView(View):

    def get(self,request,*args,**kwargs):
        qs=request.user.cart.items.filter(is_order_placed=False)
        return render(request,"cart_list.html",{"data":qs})


@method_decorator([signinrequired,owner_permission_required,never_cache],name="dispatch")
class BasketItemRemoveView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        basket_item_object=CartItem.objects.get(id=id)
        basket_item_object.delete()
        return redirect("cart-list")
    

@method_decorator([signinrequired,owner_permission_required,never_cache],name="dispatch")
class CartItemUpdateQuandityView(View):
    def post(self,request,*args,**kwargs):
        action= request.POST.get("counterbutton")
        print(action)
        id=kwargs.get("pk")
        basket_item_object=CartItem.objects.get(id=id)
        if action=="+":
            basket_item_object.quantity+=1
            basket_item_object.save()
        else:
            basket_item_object.quantity-=1
            basket_item_object.save()
        return redirect("cart-list")
    

@method_decorator([signinrequired,never_cache],name="dispatch")
class CheckOutView(View):
    def get(self,request,*args,**kwargs):
        return render(request,"checkout.html")
    def post(self,request,*args,**kwargs):
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        address=request.POST.get("address")
        payment_method=request.POST.get("payment")

        # creating order item instance
        order_obj=Order.objects.create(
            user_object=request.user,
            delivery_address=address,
            phone=phone,
            email=email,
            total=request.user.cart.cart_total,
            payment=payment_method     
        )
         
        
        try:
            basket_items=request.user.cart.get_cart_items
            for bi in basket_items:
                OrderItems.objects.create(
                order_object=order_obj,
                basket_item_object=bi,
                )
                bi.is_order_placed=True
                bi.save()
        except:
            order_obj.delete()
        finally:
            if payment_method=="online" and order_obj:
                client = razorpay.Client(auth=(KEY_ID,KEY_SECRET))
                amt=int(order_obj.get_order_total*100)
                data = {"amount": amt, "currency": "INR", "receipt": "order_rcptid_11"}
                payment = client.order.create(data=data)
                order_obj.order_id=payment.get("id")
                order_obj.save()
                context={
                    "key":KEY_ID,
                    "order_id":payment.get("id"),
                    "amount":payment.get("amount")
                }
                return render(request,"payment.html",{"context":context})
            return redirect("order-summary")

@method_decorator([signinrequired,never_cache],name="dispatch")
class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("first-page")
    
class OrderSummaryView(View):
    def get(self,request,*args,**kwargs):
        qs=Order.objects.filter(user_object=request.user).exclude(status="cancelled")
        return render (request,"ordersummary.html",{"data":qs})

class OrderItemRemoveView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        OrderItems.objects.get(id=id).delete()
        return redirect("order-summary")
    
@method_decorator(csrf_exempt,name="dispatch")
class PaymentVerificationView(View):
    def post(self,request,*args,**kwargs):
        client = razorpay.Client(auth=(KEY_ID,KEY_SECRET))
        data=request.POST
        try:
        
            client.utility.verify_payment_signature(data)
            print(data)
            order_obj=Order.objects.get(order_id=data.get("razorpay_order_id"))
            order_obj.is_paid=True
            order_obj.save()
            print("=========TRANSATION COMPLETE=======")
        except:
            print("=======TRANSACTION FAILED=====")
        return render(request,"success.html")