from rest_framework import serializers
from .models import Category, MenuItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    
    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description', 'price', 'category', 'image')