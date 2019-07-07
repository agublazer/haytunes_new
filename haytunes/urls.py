from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('add_credits/', views.add_credits, name='add_credits'),
    path('create_discount/', views.create_discount, name='create_discount'),
    path('search_client/', views.search_client, name='search_client'),
    path('view_list/', views.view_list, name='view_list'),
    path('clients/<int:id>', views.client_detail, name='client-detail'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('category/<int:pk>', views.CategoryDetailView.as_view(), name='category-detail'),
    path('category/create/', views.CategoryCreate.as_view(), name='category_create'),
    path('category/<int:pk>/update/', views.CategoryUpdate.as_view(), name='category_update'),
    path('category/<int:pk>/delete/', views.CategoryDelete.as_view(), name='category_delete'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('product/<uuid:pk>', views.ProductDetailView.as_view(), name='product-detail'),
    path('product/create/', views.ProductCreate.as_view(), name='product_create'),
    path('product/<uuid:pk>/update/', views.ProductUpdate.as_view(), name='product_update'),
    path('product/<uuid:pk>/delete/', views.ProductDelete.as_view(), name='product_delete'),
]