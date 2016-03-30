# -*- coding:utf-8 -*-
import os
import re
import urllib
import time
import datetime

from rest_framework import views
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from flashsale.pay.models import Register, Customer
from shopapp.smsmgr.tasks import task_register_code
from django.contrib.auth.models import User as DjangoUser
import logging
logger = logging.getLogger('django.request')

PHONE_NUM_RE = re.compile(r'^0\d{2,3}\d{7,8}$|^1[34578]\d{9}$|^147\d{8}', re.IGNORECASE)
TIME_LIMIT = 360
RESEND_TIME_LIMIT = 180
SYSTEMOA_ID = 641
MAX_DAY_LIMIT = 5

def check_day_limit(reg):
    """
    whether or not the day_limit is reached.
    """
    if reg.code_time:
        date1 = datetime.datetime.now().date()
        date2 = reg.code_time.date()
        if date1 == date2:
            if reg.verify_count > MAX_DAY_LIMIT:
                return True
        else:
            reg.verify_count = 0
            reg.save()
    return False


def get_register(mobile):
    """
    get register record by mobile, create one if not exists.
    return [register, created]
    if created == True, this means register just got created.
    """
    regs = Register.objects.filter(vmobile=mobile)
    if regs.count() > 0:
        return regs[0], False
    reg = Register(vmobile=mobile)
    reg.save()

    return reg, True


def validate_code(mobile, verify_code):
    """
    Only indicate whether or not verify_code is valid.
    """
    current_time = datetime.datetime.now()
    earliest_send_time = current_time - datetime.timedelta(seconds=TIME_LIMIT)
    regs = Register.objects.filter(vmobile=mobile)
    
    if regs.count() <= 0:
        return False
    
    reg = regs[0]
    if not reg.code_time:
        return False
    if not reg.verify_code:
        return False
    
    reg.submit_count += 1     #提交次数加一    
    reg.save()

    if reg.code_time > earliest_send_time and reg.verify_code == verify_code:
        return True

    return False


def get_customer(request, mobile):
    """
    1) get customer by authenticated user (if logged in);
    2) get customer by mobile if otherwise.
    """
    user = request.user
    if user and user.is_authenticated():
        customers = Customer.objects.filter(user=user)
    else:
        customers = Customer.objects.filter(mobile=mobile)
    if customers.count() > 0:
        return customers[0]
    return None


def validate_mobile(mobile):
    """
    check mobile format
    """
    if re.match(PHONE_NUM_RE, mobile):  # 进行正则判断
        return True
    return False


def validate_action(action):
    """
    check whether the action is legal.
    """
    d = ["register", "find_pwd", "change_pwd", "bind", "sms_login"]
    if action in d:
        return True
    return False


def customer_exists(mobile):
    """
    check customer existance by mobile.
    """
    customers = Customer.objects.filter(mobile=mobile)
    if customers.count() > 0:
        return True
    return False


def should_resend_code(reg):
    """
    whether or not the system should resend code
    """
    if reg.verify_count <= 0:
        return True

    current_time = datetime.datetime.now()
    earliest_send_time = current_time - datetime.timedelta(seconds=RESEND_TIME_LIMIT)
    if reg.code_time and reg.code_time > earliest_send_time:
        return False
    return True


    
class SendCodeView(views.APIView):
    """
    处理所有和验证码相关的请求，暂有5类：
    register，sms_login, find_pwd, change_pwd, bind.
    
    /send_code
    mobile: mobile number
    action: one of 5 actions (register，sms_login, find_pwd, change_pwd, bind)
    """
    
    def post(self, request): 
        content = request.REQUEST
        mobile = content.get("mobile", "0")
        action = content.get("action", "")
    
        if not validate_mobile(mobile):
            return Response({"rcode": 1, "msg": u"亲，手机号码错啦！"})
        
        if not validate_action(action):
            return Response({"rcode": 1, "msg": u"亲，操作错误！"})
        
        customer = get_customer(request, mobile)
        
        if customer:
            if action == 'register':
                return Response({"rcode": 2, "msg": u"该用户已经存在啦！"})
        else:
            if action == 'find_pwd' or action == 'change_pwd' or action == 'bind':
                return Response({"rcode": 3, "msg": u"该用户还不存在呢！"})
        
        reg, created = get_register(mobile)
        if not created:
            # if reg is not just created, we have to check 
            # day limit and resend condition.
            if check_day_limit(reg):
                return Response({"rcode": 4, "msg": u"当日验证次数超过限制!"})
            if not should_resend_code(reg):
                return Response({"rcode": 5, "msg": u"验证码刚发过咯，请等待下哦！"})
        
        reg.verify_code = reg.genValidCode()
        reg.code_time = datetime.datetime.now()
        reg.save()
        task_register_code.s(mobile, "3")()
        return Response({"rcode": 0, "msg": u"验证码已发送！"})
    

class VerifyCodeView(views.APIView):    
    """
    verify code under 5 action cases:
    register, find_pwd, change_pwd, bind, sms_login
    
    /verify_code
    mobile: mobile number
    action: one of 5 actions (register，sms_login, find_pwd, change_pwd, bind)
    """

    def post(self, request): 
        content = request.REQUEST
        mobile = content.get("mobile", "0")
        action = content.get("action", "")
        verify_code = content.get("verify_code", "")
        
        if not validate_mobile(mobile):
            return Response({"rcode": 1, "msg": u"亲，手机号码错啦！"})

        if not validate_action(action):
            return Response({"rcode": 1, "msg": u"亲，操作错误！"})
    
        customer = get_customer(request, mobile)
        if customer:
            if action == 'register':
                return Response({"rcode": 2, "msg": u"该用户已经存在啦！"})  # 已经有用户了
        else:
            if action == 'find_pwd' or action == 'change_pwd' or action == 'bind':
                return Response({"rcode": 3, "msg": u"该用户还不存在呢！"})
    
        if not validate_code(mobile, verify_code):
            return Response({"rcode": 4, "msg": u"验证码不对或过期啦！"})  # 验证码过期或者不对
        
        if not customer:
            django_user,state = DjangoUser.objects.get_or_create(username=mobile, is_active=True)
            customer,state = Customer.objects.get_or_create(user=django_user)
    
        customer.mobile = mobile
        customer.save()
    
        if action == 'register' or action == 'msm_login':
            # force to use SMSLoginBackend for authentication
            content['sms_code'] = verify_code 
            
            user = authenticate(request=request, **content)
            if not user or user.is_anonymous():
                return Response({"code": 5, "message": u'登录异常！'})

            login(request, user)
            return Response({"rcode": 0, "msg": u"登录成功！"})  
        
        return Response({"rcode": 0, "msg": u"验证码校验通过！"}) 
    

class ResetPasswordView(views.APIView):    
    """
    Reset password:
    
    /reset_password?mobile=xxx&password1=xxx&password2=xxx&verify_code=xxx
    """
    def post(self, request):
        """
        reset password after verifying code
        """
        content = request.REQUEST
        mobile = content.get("mobile", "0")
        pwd1 = content.get("password1", "")
        pwd2 = content.get("password2", "")
        verify_code = content.get("verify_code", "")
        
        if not validate_mobile(mobile):
            return Response({"rcode": 1, "msg": u"亲，手机号码错啦！"})
    
        if not mobile or not pwd1 or not pwd2 or not verify_code or pwd1 != pwd2:
            return Response({"rcode": 2, "msg": "提交的参数有误呀！"})
    
        if len(pwd1) < 6:
            return Response({"rcode": 2, "msg": "密码长度不得少于6位！"})
        
        customer = get_customer(request, mobile)
        if not customer:
            return Response({"rcode": 3, "msg": u"该用户还不存在呢！"})
    
        if not validate_code(mobile, verify_code):
            return Response({"rcode": 4, "msg": u"验证码不对或过期啦！"})  # 验证码过期或者不对
        
        django_user = customer.user
        django_user.set_password(pwd1)
        django_user.save()
        
        return Response({"rcode": 0, "msg": u"密码设置成功啦！"})
    

class PasswordLoginView(views.APIView):
    """
    User login with username and password. She can login either via APP or H5 Web.
    
    """
    def get(self, request):
        content = request.POST
        username = content.get('username','0')
        password = content.get('password', '')
        next_url = content.get('next', '/index.html')
        if not username or not password:
            return Response({"code": 1, "message": u"用户名和密码不全呢！", 'next': ''})

        customers = Customer.objects.filter(mobile=username)
        if customers.count() == 1:
            # 若是微信授权创建的账户，django user的username不是手机号。
            username = customers[0].user.username

        user = authenticate(username=username, password=password)
        if not user or user.is_anonymous():
            return Response({"code": 2, "message": u"用户名或密码错误呢！", 'next': ''})
        login(request, user)
        
        return Response({"code": 0, "message": u"登录成功", "next": next_url})


def check_sign(request):
    """
    功能：微信app 登录接口数据校验算法:
    参数：params = {'a':1,'c':2,'b':3}
    时间戳：timestamp = 1442995986
    随机字符串：noncestr = 8位随机字符串，如abcdef45
        　 　secret : 3c7b4e3eb5ae4c (测试值)

       签名步骤:
       1，获得所有签名参数：　sign_params = {timestamp:时间戳,noncestr:随机值,secret:密钥值}
        如　{'timestamp':'1442995986','noncestr':'1442995986abcdef','secret':'3c7b4e3eb5ae4c'}
       2,根据参数的字符串key，进行升序排列,并组装成新的字符串，如：
        sign_string = '&'.join(sort([k=v for k,v in sign_params],asc=true))
       如　'noncestr=1442995986abcdef&secret=3c7b4e3eb5ae4c&timestamp=1442995986'
       3,签名算法
        sign = hash.sha1(sign_string).hexdigest()
        如　签名值＝'39ae931c59394c9b4b0973b3902956f63a35c21e'
       4,最后传递给服务器的参数：
       URL:~?noncestr=1442995986abcdef&timestamp=1442995986&sign=366a83819b064149a7f4e9f6c06f1e60eaeb02f7
       POST: 'a=1&b=3&c=2'
    """
    CONTENT = request.GET
    params = {}
    for k, v in CONTENT.iteritems():
        params[k] = v
    timestamp = params.get('timestamp')
    if not timestamp or time.time() - int(timestamp) > 30:
        return False
    origin_sign = params.pop('sign')
    new_sign = options.gen_wxlogin_sha1_sign(params, settings.WXAPP_SECRET)
    if origin_sign and origin_sign == new_sign:
        return True
    params.update({'sign': origin_sign})
    logger.error('%s' % params)
    return False


class WeixinAppLoginView(views.APIView):
    """
    User login with Weixin authorization via APP.
    
    """
    def get(self, request):
        """
        app客户端微信授权登陆
        """
        if not check_sign(request):
            return Response({"code": 1, "message": u'登录失败'})

        params = request.POST
        user = authenticate(request=request, **params)
        if not user or user.is_anonymous():
            return Response({"code": 2, "message": u'登录异常'})

        login(request, user)
        return Response({"code": 0, "message": u'登录成功'})