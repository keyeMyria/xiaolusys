from django.contrib import admin
from shopback.items.models import Item,Product,ProductSku



class ItemAdmin(admin.ModelAdmin):
    list_display = ('num_iid','product','category','price','user','title','pic_url')
    list_display_links = ('num_iid', 'title')
    #list_editable = ('update_time','task_type' ,'is_success','status')

    #date_hierarchy = 'modified'
    #ordering = ['created_at']


    list_filter = ('approve_status',)
    search_fields = ['num_iid', 'title']


admin.site.register(Item, ItemAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('outer_id','name','user','category','collect_num','price','created','modified')
    list_display_links = ('outer_id', 'name')
    #list_editable = ('update_time','task_type' ,'is_success','status')

    date_hierarchy = 'modified'
    #ordering = ['created_at']


    list_filter = ('category','user')
    search_fields = ['outer_id', 'name']


admin.site.register(Product, ProductAdmin)


class ProductSkuAdmin(admin.ModelAdmin):
    list_display = ('outer_id','product','quantity','properties_name','properties','status')
    list_display_links = ('outer_id', 'product')
    #list_editable = ('update_time','task_type' ,'is_success','status')

    #date_hierarchy = 'modified'
    #ordering = ['created_at']


    list_filter = ('status',)
    search_fields = ['outer_id', 'product']


admin.site.register(ProductSku, ProductSkuAdmin)
  