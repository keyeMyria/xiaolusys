#-*- coding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import hashlib
import inspect
import copy
import time
import datetime
import json
import urllib
import urllib2
from django.conf import settings
from django.core.cache import cache

from shopapp.weixin.models import WeiXinAccount
from common.utils import (randomString,
                          update_model_fields,
                          randomString,
                          getSignatureWeixin,
                          process_lock)

REFRESH_WX_TOKEN_CACHE_KEY = 'REFRESH_WX_TOKEN_KEY'

class WeiXinRequestException(Exception):
    
    def __init__(self,code=None,msg=None):
        self.code = code
        self.msg  = msg
  
    def __str__(self):
        return u'微信API错误:(%s,%s)'%(str(self.code),self.msg)


class WeiXinAPI(object):
    
    _token_uri          = "/cgi-bin/token"
    _user_info_uri      = "/cgi-bin/user/info"
    _create_groups_uri  = "/cgi-bin/groups/create"
    _get_grounps_uri    = "/cgi-bin/groups/get"
    _get_user_group_uri = "cgi-bin/groups/getid"
    _update_group_uri   = "/cgi-bin/groups/update"
    _update_group_member_uri  = "/cgi-bin/groups/members/update"
    _get_user_info_uri  = "/cgi-bin/user/info"
    _get_followers_uri  = "/cgi-bin/user/get"
    _create_menu_uri    = "/cgi-bin/menu/create"
    _get_menu_uri       = "/cgi-bin/menu/get"
    _detele_menu_uri    = "/cgi-bin/menu/delete"
    _create_qrcode_uri  = "/cgi-bin/qrcode/create"
    _media_get_uri      = "/cgi-bin/media/get"
    _js_ticket_uri      = "/cgi-bin/ticket/getticket"
    
    #微信小店接口
    _merchant_get_uri   = "/merchant/get"
    _merchant_getbystatus_uri   = "/merchant/getbystatus"
    _merchant_stock_add_uri   = "/merchant/stock/add"
    _merchant_stock_reduce_uri   = "/merchant/stock/reduce"
    _merchant_order_getbyid_uri   = "/merchant/order/getbyid"
    _merchant_order_getbyfilter_uri   = "/merchant/order/getbyfilter"
    _merchant_order_setdelivery_uri   = "/merchant/order/setdelivery"
    
    #微信原生支付URL
    _native_url   = "weixin://wxpay/bizpayurl"
    _deliver_notify_url = "/pay/delivernotify"
    
    
    def __init__(self):
        self._wx_account = WeiXinAccount.getAccountInstance()
        
    def getAccountId(self):
        
        if self._wx_account.isNone():
            return None
        
        return self._wx_account.account_id
        
    def getAbsoluteUrl(self,uri,token):
        url = settings.WEIXIN_API_HOST + uri
        return token and '%s?access_token=%s'%(url,self.getAccessToken()) or url+'?'
        
    def checkSignature(self,signature,timestamp,nonce):
        
        import time
        import hashlib
        
        if time.time() - int(timestamp) > 300:
            return False
        
        sign_array = [self._wx_account.token,timestamp,nonce]
        sign_array.sort()
        
        sha1_value = hashlib.sha1(''.join(sign_array))

        return sha1_value.hexdigest() == signature
        
    def handleRequest(self,uri,params={},method="GET",token=True):
        
        absolute_url = self.getAbsoluteUrl(uri,token)
        
        if method.upper() == 'GET':
            url = '%s&%s'%(absolute_url,urllib.urlencode(params))
            req = urllib2.urlopen(url)
            resp = req.read()
            
        else:
            rst = urllib2.Request(absolute_url)
            req = urllib2.urlopen(rst,type(params)==dict and 
                                  urllib.urlencode(params) or params)
            resp = req.read()

        content = json.loads(resp,strict=False)
        
        if content.has_key('errcode') and content['errcode'] != 0:
            raise WeiXinRequestException(content['errcode'],content['errmsg'])
        
        return content
    
    @process_lock
    def refresh_token(self):
        
        if not self._wx_account.isExpired():
            return self._wx_account.access_token
        
        params = {'grant_type':'client_credential',
                  'appid':self._wx_account.app_id,
                  'secret':self._wx_account.app_secret}
        
        content = self.handleRequest(self._token_uri, params,token=False)
        
        self._wx_account.access_token = content['access_token']
        self._wx_account.expired      = datetime.datetime.now()
        self._wx_account.expires_in   = content['expires_in']
        update_model_fields(self._wx_account,
                            update_fields=['access_token','expired','expired_in'])
        
        return content['access_token']
    
    def getAccessToken(self):
        
        if not self._wx_account.isExpired():
            return self._wx_account.access_token
        
        return self.refresh_token()
    
    def getCustomerInfo(self,openid,lang='zh_CN'):
        return self.handleRequest(self._user_info_uri, {'openid':openid,'lang':lang})
    
    
    def createGroups(self,name):
        name = type(name)==unicode and name.encode('utf8') and name
        return self.handleRequest(self._create_groups_uri, {'name':name}, method='POST')
    
    
    def getGroups(self):
        return self.handleRequest(self._get_groups_uri)
    
    def getUserGroupById(self,openid):
        return self.handleRequest(self._get_user_group_uri, {'openid':openid}, method='POST')
        
    def updateGroupName(self,id,name):
        name = type(name)==unicode and name.encode('utf8') and name
        return self.handleRequest(self._update_group_uri, {'id':id,'name':name}, method='POST')    
        
    def updateGroupMember(self,openid,to_groupid):
        return self.handleRequest(self._update_group_member_uri, {'openid':openid,
                                                      'to_groupid':to_groupid}, 
                                  method='POST')   
    
    def getUserInfo(self,openid):
        return self.handleRequest(self._get_user_info_uri, {'openid':openid},method='GET') 
        
    def getFollowersID(self,next_openid=''):
        return self.handleRequest(self._get_followers_uri, {'next_openid':next_openid}, 
                                  method='GET') 
        
    def createMenu(self,params):
        assert type(params) == dict
        jmenu = json.dumps(params,ensure_ascii=False)
        return self.handleRequest(self._create_menu_uri, str(jmenu), method='POST')
        
    def getMenu(self):
        return self.handleRequest(self._get_menu_uri, {},method='GET')
    
    def deleteMenu(self):
        return self.handleRequest(self._detele_menu_uri, {},method='GET')
    
    def createQRcode(self,action_name,action_info,scene_id,expire_seconds=0):
        
        action_name = (type(action_name)==unicode and 
                       action_name.encode('utf8') and 
                       action_name)
        
        params = {"action_name": action_name ,
                  "action_info": {"scene": {"scene_id": scene_id}}}
        
        if action_name=='QR_SCENE':
            params.update(expire_seconds=expire_seconds)
            
        return self.handleRequest(self._create_qrcode_uri, 
                                  params,method='POST')
        
    
    def getMerchant(self,product_id):
        
        params   = json.dumps({'product_id':product_id})
                    
        response = self.handleRequest(self._merchant_get_uri, 
                                      str(params),
                                      method='POST')
        return response['product_info']
    
        
    def getMerchantByStatus(self,status):

        params = json.dumps({'status':status},
                            ensure_ascii=False)
        response = self.handleRequest(self._merchant_getbystatus_uri, 
                                  str(params),
                                  method='POST')
        return response['products_info']
    
        
    def addMerchantStock(self,product_id,quantity,sku_info=''):
        
        params = json.dumps({'product_id':product_id,                                            
                             'quantity':quantity,                                               
                             'sku_info':sku_info},                                              
                            ensure_ascii=False)
        return self.handleRequest(self._merchant_stock_add_uri, 
                                  str(params),
                                  method='POST')
        
    def reduceMerchantStock(self,product_id,quantity,sku_info=''):
        
        params = json.dumps({'product_id':product_id,                                                 
                             'quantity':quantity,                                                     
                             'sku_info':sku_info},                                                    
                            ensure_ascii=False)
        return self.handleRequest(self._merchant_stock_reduce_uri, 
                                  str(params),
                                  method='POST')
        
    def getOrderById(self,order_id):
        
        params = json.dumps({'order_id':str(order_id)},ensure_ascii=False)
        response = self.handleRequest(self._merchant_order_getbyid_uri, 
                                  str(params),
                                  method='POST')
        return response['order']
        
    def getOrderByFilter(self,status=None,begintime=None,endtime=None):
        
        params = {}
        
        if status:
            params.update(status=status)
            
            if begintime:
                params.update(begintime=begintime)
                
            if endtime:
                params.update(endtime=endtime)
                
        params_str = json.dumps(params,
                            ensure_ascii=False)

        response = self.handleRequest(self._merchant_order_getbyfilter_uri, 
                                      str(params_str),
                                      method='POST')
        return response['order_list']
        
    def deliveryOrder(self,order_id,delivery_company,delivery_track_no,is_others=0):

        params = json.dumps({'order_id':order_id,
                             'delivery_company':delivery_company,
                             'delivery_track_no':delivery_track_no,
                             'is_others':is_others},
                            ensure_ascii=False)
        return self.handleRequest(self._merchant_order_setdelivery_uri, 
                                  str(params),
                                  method='POST')
        
    def deliverNotify(self,open_id,trans_id,out_trade_no,
                      deliver_status=1,deliver_msg="ok"):
        
        params = {"appid":self._wx_account.app_id,
                  "appkey":self._wx_account.pay_sign_key,
                  "openid":open_id,
                  "transid":trans_id,
                  "out_trade_no":out_trade_no,
                  "deliver_timestamp":"%.0f"%time.time(),
                  "deliver_status":deliver_status,
                  "deliver_msg":deliver_msg}
        
        params['app_signature'] = getSignatureWeixin(params)
        params['sign_method'] = 'sha1'
        
        params.pop('appkey')
        
        return self.handleRequest(self._deliver_notify_url, 
                           str(json.dumps(params)), 
                           method='POST')
        
    def getJSTicket(self):
        
        if not self._wx_account.isJSTicketExpired():
            return self._wx_account.js_ticket
        
        return self.refreshJSTicket()
        
    def refreshJSTicket(self):
        
        if not self._wx_account.isJSTicketExpired():
            return self._wx_account.js_ticket
        
        js_url = self.getAbsoluteUrl(self._js_ticket_uri, self.getAccessToken())+'&type=jsapi'

        req = urllib2.urlopen(js_url)
        content = json.loads(req.read())
        
        self._wx_account.js_ticket = content['ticket']
        self._wx_account.js_expired   = datetime.datetime.now()
        update_model_fields(self._wx_account,
                            update_fields=['js_ticket','js_expired'])
        
        return content['ticket']

    def getShareSignParams(self,share_url):
        
        sign_params = {"noncestr":randomString(),
                       "jsapi_ticket":self.getJSTicket(),
                       "timestamp":int(time.time()),
                       "url":share_url }
        key_pairs = ["%s=%s"%(k,v) for k,v in sign_params.iteritems()]
        key_pairs.sort()
        
        sign_params['signature'] = hashlib.sha1('&'.join(key_pairs)).hexdigest()
        sign_params['app_id'] = self._wx_account.app_id
        
        return sign_params

    def genNativeSignParams(self,product_id):
        
        signString = {'appid':self._wx_account.app_id,
                      'timestamp':str(int(time.time())),
                      'noncestr':randomString(),
                      'productid':str(product_id),
                      'appkey':self._wx_account.app_secret
                      }
        signString.update(sign, getSignatureWeixin(signString))
        signString.pop('appkey')
        
        return signString
    
    def genPaySignParams(self,package):
        
        signString = {'appid':self._wx_account.app_id,
                      'timestamp':str(int(time.time())),
                      'noncestr':randomString(),
                      'package':package,
                      'appkey':self._wx_account.pay_sign_key
                      }
        signString.update(sign, getSignatureWeixin(signString))
        signString.pop('appkey')
        
        return signString
    
    def genPackageSignParams(self,package):
        
        return 
    
    def getMediaDownloadUrl(self,media_id):
        
        return '%s%s?access_token=%s&media_id=%s'%(settings.WEIXIN_MEDIA_HOST,
                                                   self._media_get_uri,
                                                   self.getAccessToken(),
                                                   media_id)
    