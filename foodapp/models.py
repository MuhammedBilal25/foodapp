from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save



# Create your models here.
class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant')
    name = models.CharField(max_length=500)
    contact_number = models.CharField(max_length=20)
    address = models.CharField(max_length=500)
    password=models.CharField(max_length=20,null=True)
    image=models.ImageField(upload_to="resturant_images",default="default.jpg",null=True,blank=True)


    def __str__(self):
        return self.name
    
class FoodItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image=models.ImageField(upload_to="food_images",default="default.jpg",null=True,blank=True)
    active=models.BooleanField(default=True,null=True)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_cart_items(self):
        return self.items.filter(is_order_placed=False)
    @property
    def cart_item_count(self):
        return self.get_cart_items.count()
    
    @property
    def cart_total(self):
        basket_items=self.get_cart_items
        if basket_items:
            total=sum([bi.item_total for bi in basket_items])
            return total
        return 0
    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_order_placed=models.BooleanField(default=False)

    
    @property
    def item_total(self):
        return self.quantity*self.food_item.price

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name} in cart for {self.cart.user.username}"

def create_basket(sender,instance,created,**kwargs):
    if created:
        Cart.objects.create(user=instance)

post_save.connect(create_basket,sender=User)



class Order(models.Model):

    user_object=models.ForeignKey(User,on_delete=models.CASCADE,related_name="purchase")
    delivery_address=models.CharField(max_length=200)
    phone=models.CharField(max_length=12)
    email=models.CharField(max_length=200,null=True)
    is_paid=models.BooleanField(default=False)
    total=models.PositiveIntegerField()
    order_id=models.CharField(max_length=200,null=True)

    options=(
        ("cod","cod"),
        ("online","online")
    )
    payment=models.CharField(max_length=200,choices=options,default="cod")
    option=(
        ("order-placed","order-placed"),
        ("Preparing-food","Preparing-food"),
        ("out-for-delivery","out-for-delivery"),
        ("delivered","delivered"),
        ("cancelled","cancelled")
    )
    status=models.CharField(max_length=200,choices=option,default="order-placed")

    @property
    def get_order_items(self):
        return self.purchaseitems.all()
    
    @property
    def get_order_total(self):
        purchase_items=self.get_order_items
        order_total=0
        if purchase_items:
            order_total=sum([pi.basket_item_object.item_total for pi in purchase_items])
        return order_total

class OrderItems(models.Model):

    order_object=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="purchaseitems")
    basket_item_object=models.ForeignKey(CartItem,on_delete=models.CASCADE)
