from django.urls import path
from .views import CategoryListView, MenuItemListView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('items/', MenuItemListView.as_view(), name='menu_item_list'),
]