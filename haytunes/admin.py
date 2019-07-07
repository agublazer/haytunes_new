from django.contrib import admin

# Register your models here.
from haytunes.models import Profile, Category, Product


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


class ProductsInstanceInline(admin.TabularInline):
    model = Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [ProductsInstanceInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'author', 'type', 'category', 'display_owner', 'content', 'id']
    list_filter = ['type']