from django.core.management.base import BaseCommand
from menu.models import Category, MenuItem
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Load initial menu data'
    
    def handle(self, *args, **kwargs):
        # Clear existing data (optional)
        MenuItem.objects.all().delete()
        Category.objects.all().delete()
        
        # Create categories
        burger_cat = Category.objects.create(name='Burger')
        pizza_cat = Category.objects.create(name='Pizza')
        pasta_cat = Category.objects.create(name='Pasta')
        
        # Create menu items - 5 per category
        # Pizzas
        MenuItem.objects.create(
            name='Seafood Pizza',
            description='Loaded with shrimp, crab sticks, squid, and onions on a cheesy crust.',
            price=170,
            category=pizza_cat,
            image='menu_images/seafood_pizza.jpg'
        )
        MenuItem.objects.create(
            name='Margherita Pizza',
            description='Classic pizza with tomato sauce, mozzarella, and basil.',
            price=150,
            category=pizza_cat,
            image='menu_images/margherita.jpg'
        )
        MenuItem.objects.create(
            name='Pepperoni Pizza',
            description='Spicy pepperoni with extra cheese and tomato sauce.',
            price=160,
            category=pizza_cat,
            image='menu_images/pepperoni.jpg'
        )
        MenuItem.objects.create(
            name='Vegetarian Pizza',
            description='Mixed vegetables with mozzarella cheese.',
            price=140,
            category=pizza_cat,
            image='menu_images/vegetarian.jpg'
        )
        MenuItem.objects.create(
            name='BBQ Chicken Pizza',
            description='Grilled chicken with BBQ sauce and red onions.',
            price=180,
            category=pizza_cat,
            image='menu_images/bbq_chicken.jpg'
        )
        
        # Burgers
        MenuItem.objects.create(
            name='Classic Cheeseburger',
            description='Juicy beef patty with melted cheese and special sauce.',
            price=120,
            category=burger_cat,
            image='menu_images/cheeseburger.jpg'
        )
        MenuItem.objects.create(
            name='Beef Burger',
            description='Beef patty with crispy cheddar cheese.',
            price=140,
            category=burger_cat,
            image='menu_images/beef_burger.jpg'
        )
        MenuItem.objects.create(
            name='Chicken Burger',
            description='Grilled chicken fillet with lettuce and mayo.',
            price=110,
            category=burger_cat,
            image='menu_images/chicken_burger.jpg'
        )
        MenuItem.objects.create(
            name='Mushroom Swiss Burger',
            description='Beef patty with sautéed mushrooms and Swiss cheese.',
            price=130,
            category=burger_cat,
            image='menu_images/mushroom_burger.jpg'
        )
        MenuItem.objects.create(
            name='Double Deluxe Burger',
            description='Two beef patties with special sauce and pickles.',
            price=150,
            category=burger_cat,
            image='menu_images/double_burger.jpg'
        )
        
        # Pastas
        MenuItem.objects.create(
            name='Spaghetti Bolognese',
            description='Classic spaghetti with rich meat sauce.',
            price=150,
            category=pasta_cat,
            image='menu_images/bolognese.jpg'
        )
        MenuItem.objects.create(
            name='Fettuccine Alfredo',
            description='Creamy Alfredo sauce with parmesan cheese.',
            price=160,
            category=pasta_cat,
            image='menu_images/alfredo.jpg'
        )
        MenuItem.objects.create(
            name='Penne Arrabiata',
            description='Spicy tomato sauce with garlic and chili.',
            price=140,
            category=pasta_cat,
            image='menu_images/arrabiata.jpg'
        )
        MenuItem.objects.create(
            name='Lasagna',
            description='Layered pasta with meat sauce and béchamel.',
            price=170,
            category=pasta_cat,
            image='menu_images/lasagna.jpg'
        )
        MenuItem.objects.create(
            name='Carbonara',
            description='Creamy sauce with pancetta and egg yolk.',
            price=165,
            category=pasta_cat,
            image='menu_images/carbonara.jpg'
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded expanded menu data'))