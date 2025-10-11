from django.contrib import admin
from .models import Product, Category, HeroSlide, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ("image", "alt_text", "sort_order")
    ordering = ("sort_order", "id")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','sku','price','stock','active','is_latest','is_super_sale','is_flash_sale','is_mega_sale')
    search_fields = ('name','sku')
    list_filter = ('active','category')
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ('is_latest','is_super_sale','is_flash_sale','is_mega_sale')
    inlines = [ProductImageInline]


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('title','is_active','display_order')
    list_editable = ('is_active','display_order')
