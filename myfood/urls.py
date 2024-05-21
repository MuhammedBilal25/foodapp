"""
URL configuration for myfood project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from foodapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("restaurant/registration/",views.RestaurantSignUpView.as_view(),name="restaurant-signup"),
    path("restaurant/login/",views.RestaurantSignInView.as_view(),name="restaurant-signin"),
    path("food/create/",views.FoodItemCreateView.as_view(),name="addfood"),
    path("restaurant/home/",views.ResturantFoodItemListView.as_view(),name="restaurant-home"),
    path("",views.FirstView.as_view(),name="first-page"),
    path("custumer/login/",views.SignInView.as_view(),name="custumer-login"),
    path("custumer/signup/",views.SignupView.as_view(),name="custumer-signup"),
    path("custumer/home/",views.CustumerHomeView.as_view(),name="custumer-home"),
    path("food_items/<int:pk>/",views.FoodItemListView.as_view(),name='food-list'),
    path("resturant/food/<int:pk>/update/",views.FoodItemupdateView.as_view(),name="food-edit"),
    path("food/addtobasket/<int:pk>/",views.AddToCartView.as_view(),name='add-to-cart'),
    path("cart/list/",views.BasketItemListView.as_view(),name="cart-list"),
    path("cart/items/<int:pk>/remove",views.BasketItemRemoveView.as_view(),name="cartitem-remove"),
    path("cart/quantity/update/<int:pk>",views.CartItemUpdateQuandityView.as_view(),name="cart-qty-update"),
    path("cart/checkout/",views.CheckOutView.as_view(),name="checkout"),
    path('signout/',views.SignOutView.as_view(),name="signout"),
    path('order/summary/',views.OrderSummaryView.as_view(),name="order-summary"),
    path('orders/item/<int:pk>/remove/',views.OrderItemRemoveView.as_view(),name="order-remove"),
    path('payment/verification/',views.PaymentVerificationView.as_view(),name="verification"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# media url and media root
