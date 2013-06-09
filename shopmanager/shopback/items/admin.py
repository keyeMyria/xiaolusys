#-*- coding:utf8 -*-
import json
import datetime
from django.contrib import admin
from django.db import models
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms import TextInput, Textarea
from shopback.items.models import Item,Product,ProductSku
from shopback.trades.models import MergeTrade,MergeOrder
from shopback import paramconfig as pcfg
from shopback.base import log_action,User, ADDITION, CHANGE
import logging 

logger =  logging.getLogger('tradepost.handler')

class ProductSkuInline(admin.TabularInline):
    
    model = ProductSku
    fields = ('outer_id','properties_name','properties_alias','quantity','warn_num','remain_num','wait_post_num','cost','std_purchase_price','std_sale_price'
                    ,'agent_price','staff_price','sync_stock','is_assign','is_split','is_match','status','buyer_prompt')
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'10'})},
        models.FloatField: {'widget': TextInput(attrs={'size':'8'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    }


class ItemAdmin(admin.ModelAdmin):
    list_display = ('num_iid','user','outer_id','type','category','title','price','has_showcase','list_time','last_num_updated','approve_status','status')
    list_display_links = ('num_iid', 'title')
    #list_editable = ('update_time','task_type' ,'is_success','status')

    date_hierarchy = 'last_num_updated'
    #ordering = ['created_at']

    list_filter = ('user','approve_status')
    search_fields = ['num_iid', 'outer_id', 'title']


admin.site.register(Item, ItemAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','outer_id','name','collect_num','category','warn_num','remain_num','wait_post_num','cost','std_purchase_price'
                    ,'std_sale_price','agent_price','sync_stock','is_assign','is_split','is_match','modified','status')
    list_display_links = ('id','outer_id',)
    list_editable = ('name',)
    
    date_hierarchy = 'modified'
    #ordering = ['created_at']
    
    inlines = [ProductSkuInline]
    
    list_filter = ('status','sync_stock','is_split','is_match','is_assign',)
    search_fields = ['outer_id', 'name']
    
    #--------设置页面布局----------------
    fieldsets =(('商品基本信息:', {
                    'classes': ('expand',),
                    'fields': (('outer_id','name','category','pic_path','status')
                               ,('collect_num','warn_num','remain_num','wait_post_num')
                               ,('cost','std_purchase_price','std_sale_price','agent_price','staff_price')
                               ,('weight','sync_stock','is_assign','is_split','is_match','memo','buyer_prompt'))
                }),)
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'16'})},
        models.FloatField: {'widget': TextInput(attrs={'size':'16'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }
    
    #更新用户线上商品入库
    def sync_items_stock(self,request,queryset):
        
        from shopapp.syncnum.tasks import updateItemNum
        from shopback.items.tasks import updateUserProductSkuTask
        
        dt   =   datetime.datetime.now()
        sync_items = []
        for prod in queryset:
            pull_dict = {'outer_id':prod.outer_id,'name':prod.name}
            try:
                items = Item.objects.filter(outer_id=prod.outer_id)
                #更新商品信息
                for item in items:
                    Item.get_or_create(item.user.visitor_id,item.num_iid,force_update=True)
                    
                items = items.filter(approve_status=pcfg.ONSALE_STATUS)
                if items.count() < 1:
                    raise Exception(u'请确保商品在售')
                #更新商品线上SKU状态
                updateUserProductSkuTask(outer_ids=[i.outer_id for i in items if i.outer_id ])
                #更新商品及SKU库存
                for item in items:
                    updateItemNum(item.user.visitor_id,item.num_iid)
            except Exception,exc:
                logger.error(exc.message,exc_info=True)
                pull_dict['success']=False
                pull_dict['errmsg']=exc.message or '%s'%exc  
            else:
                pull_dict['success']=True
            sync_items.append(pull_dict)
       
        return render_to_response('items/product_action.html',{'prods':sync_items,'action_name':u'更新线上库存'},
                                  context_instance=RequestContext(request),mimetype="text/html")
    
    sync_items_stock.short_description = u"同步淘宝线上库存"
    
    #根据线上商品SKU 更新系统商品SKU
    def update_items_sku(self,request,queryset):
        
        from shopback.items.tasks import updateUserProductSkuTask
        sync_items = []
        for prod in queryset:
            pull_dict = {'outer_id':prod.outer_id,'name':prod.name}
            try:
                items = Item.objects.filter(outer_id=prod.outer_id)
                for item in items:
                    Item.get_or_create(item.user.visitor_id,item.num_iid,force_update=True)    
                
                updateUserProductSkuTask(outer_ids=[prod.outer_id])
                item_sku_outer_ids = set()
                items = Item.objects.filter(outer_id=prod.outer_id)
                for item in items:
                    sku_dict = json.loads(item.skus or '{}')
                    if sku_dict:
                        sku_list = sku_dict.get('sku')
                        item_sku_outer_ids.update([ sku.get('outer_id','') for sku in sku_list])
                prod.prod_skus.exclude(outer_id__in=item_sku_outer_ids).update(status=pcfg.REMAIN)
            except Exception,exc:
                pull_dict['success']=False
                pull_dict['errmsg']=exc.message or '%s'%exc  
            else:
                pull_dict['success']=True
            sync_items.append(pull_dict)
       
        return render_to_response('items/product_action.html',{'prods':sync_items,'action_name':u'更新商品SKU'},
                                  context_instance=RequestContext(request),mimetype="text/html")
    
    update_items_sku.short_description = u"更新系统商品SKU"    
    
    #取消该商品缺货订单
    def cancle_items_out_stock(self,request,queryset):
        
        sync_items = []
        for prod in queryset:
            pull_dict = {'outer_id':prod.outer_id,'name':prod.name}
            try:
                orders = MergeOrder.objects.filter(outer_id=prod.outer_id,out_stock=True)
                for order in orders:
                    order.out_stock = False
                    order.save()
                    log_action(request.user.id,order.merge_trade,CHANGE,u'取消子订单（%d）缺货'%order.id)
            except Exception,exc:
                pull_dict['success']=False
                pull_dict['errmsg']=exc.message or '%s'%exc  
            else:
                pull_dict['success']=True
            sync_items.append(pull_dict)
       
        return render_to_response('items/product_action.html',{'prods':sync_items,'action_name':u'取消商品对应订单缺货状态'},
                                  context_instance=RequestContext(request),mimetype="text/html")
        
    cancle_items_out_stock.short_description = u"取消商品订单缺货"
    
    #聚划算入仓商品
    def juhuasuan_instock_product(self,request,queryset):
        
        from shopapp.juhuasuan.models import PinPaiTuan
        sync_items = []
        for prod in queryset:
            pull_dict = {'outer_id':prod.outer_id,'name':prod.name}
            try:
                for sku in prod.prod_skus.all():
                    prod_sku_name = '%s--%s'%(prod.name,sku.properties_alias or sku.properties_name)
                    PinPaiTuan.objects.get_or_create(outer_id=prod.outer_id,outer_sku_id=sku.outer_id,prod_sku_name=prod_sku_name)
            except Exception,exc:
                pull_dict['success']=False
                pull_dict['errmsg']=exc.message or '%s'%exc  
            else:
                pull_dict['success']=True
            sync_items.append(pull_dict)
       
        return render_to_response('items/product_action.html',{'prods':sync_items,'action_name':u'聚划算入仓商品'},
                                  context_instance=RequestContext(request),mimetype="text/html")
        
    juhuasuan_instock_product.short_description = u"加聚划算入仓商品"
    
    actions = ['sync_items_stock','update_items_sku','cancle_items_out_stock','juhuasuan_instock_product']

admin.site.register(Product, ProductAdmin)


class ProductSkuAdmin(admin.ModelAdmin):
    list_display = ('id','outer_id','product','quantity','warn_num','remain_num','wait_post_num','cost','std_purchase_price','std_sale_price'
                    ,'agent_price','staff_price','sync_stock','is_assign','is_split','is_match','properties_name','properties_alias','status')
    list_display_links = ('outer_id',)
    list_editable = ('quantity',)

    date_hierarchy = 'modified'
    #ordering = ['created_at']
    

    list_filter = ('status','sync_stock','is_split','is_match','is_assign',)
    search_fields = ['outer_id','product__outer_id','properties_name']
    
    #取消该商品缺货订单
    def cancle_items_out_stock(self,request,queryset):
        
        sync_items = []
        for prod in queryset:
            pull_dict = {'outer_id':prod.outer_id,'name':prod.properties_name}
            try:
                orders = MergeOrder.objects.filter(outer_id=prod.product.outer_id,outer_sku_id=prod.outer_id,out_stock=True)
                for order in orders:
                    order.out_stock = False
                    order.save()
                    log_action(request.user.id,order.merge_trade,CHANGE,u'取消子订单（%d）缺货'%order.id)
            except Exception,exc:
                pull_dict['success']=False
                pull_dict['errmsg']=exc.message or '%s'%exc  
            else:
                pull_dict['success']=True
            sync_items.append(pull_dict)
       
        return render_to_response('items/product_action.html',{'prods':sync_items,'action_name':u'取消规格对应订单缺货状态'},
                                  context_instance=RequestContext(request),mimetype="text/html")
        
    cancle_items_out_stock.short_description = u"取消规格订单缺货"
    
    actions = ['cancle_items_out_stock']


admin.site.register(ProductSku, ProductSkuAdmin)
  


