from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from foodapp.models import Restaurant,FoodItem


class CustumerRegistrationForm(UserCreationForm):
    class Meta:
        model=User
        fields=["username","email","password1","password2"]

class CustumerLoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField()

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'contact_number','password','image']
        widgets={
            'name':forms.TextInput(attrs={"class":"form-control"}),
            'address':forms.TextInput(attrs={"class":"form-control"}),
            'contact_number':forms.TextInput(attrs={"class":"form-control"}),
        }

class RestaurantLoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')



class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'description', 'price', 'image','active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}), 
        }
