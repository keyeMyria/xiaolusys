#-*- encoding:utf8 -*-

from django.db import models
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User,AnonymousUser
from django.contrib.auth.backends import RemoteUserBackend
from django.core.urlresolvers import reverse

from .models import Customer
from .options import get_user_unionid
from .tasks import task_Update_Sale_Customer
from shopapp.weixin.views import valid_openid
from shopapp.weixin.models import WeiXinUser

import logging
logger = logging.getLogger('django.request')


class FlashSaleBackend(RemoteUserBackend):
    
    create_unknown_user = False
    upports_inactive_user = False
    supports_object_permissions = False

    def authenticate(self, request, **kwargs):
        
        if not request.path.endswith(reverse('flashsale_login')):
            return None
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.add_message(request, messages.ERROR, u'请输入用户名及密码')
            return AnonymousUser()
        
        try:
            customer = Customer.objects.get(models.Q(email=username)|models.Q(mobile=username)
                                            ,status=Customer.NORMAL)
            user = customer.user 
            
            if not user.check_password(password):
                messages.add_message(request, messages.ERROR, u'用户名或密码错误')
                return AnonymousUser()
        except Customer.DoesNotExist:
            messages.add_message(request, messages.ERROR, u'用户名或密码错误')
            return AnonymousUser()
        except Customer.MultipleObjectsReturned:
            messages.add_message(request, messages.ERROR, u'帐号异常，请联系管理员')
            return AnonymousUser()
            
        try:
            wxuser = WeiXinUser.objects.get(mobile=username)
            customer.nick   = wxuser.nickname
            customer.save()
        except:
            pass 

        return user
    

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
        

class WeixinPubBackend(RemoteUserBackend):
    
    create_unknown_user = True
    upports_inactive_user = False
    supports_object_permissions = False

    def authenticate(self, request, **kwargs):
        
        if not request.path.startswith(("/mm/","/rest/")) or kwargs.get('username'):
            return None
        
        code = request.GET.get('code')
        openid,unionid = get_user_unionid(code,appid=settings.WXPAY_APPID,
                                          secret=settings.WXPAY_SECRET,request=request)
        
        if not valid_openid(openid) or not valid_openid(unionid):
            return AnonymousUser()
        
        try:
            profile = Customer.objects.get(unionid=unionid,status=Customer.NORMAL)
            #如果openid有误，则重新更新openid
            if profile.openid != openid:
                task_Update_Sale_Customer.s(unionid,openid=openid,app_key=settings.WXPAY_APPID)()
                
            if profile.user:
                if not profile.user.is_active:
                    profile.user.is_active = True
                    profile.user.save()
                return profile.user
            else:
                user,state = User.objects.get_or_create(username=unionid,is_active=True)
                profile.user = user
                profile.save()
            
        except Customer.DoesNotExist:
            if not self.create_unknown_user:
                return AnonymousUser()
            
            user,state = User.objects.get_or_create(username=unionid,is_active=True)
            profile,state = Customer.objects.get_or_create(unionid=unionid,openid=openid,user=user)
            
        task_Update_Sale_Customer.s(unionid,openid=openid,app_key=settings.WXPAY_APPID)()
        
        return user
    

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
  
