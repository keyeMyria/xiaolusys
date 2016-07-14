# coding=utf-8
__author__ = 'yan.huang'
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.forms import forms
from rest_framework.response import Response
from rest_framework import generics, viewsets, permissions, authentication, renderers
from rest_framework.decorators import detail_route, list_route
from rest_framework import exceptions
from core.weixin.mixins import WeixinAuthMixin
from .models import XiaoluAdministrator, GroupMamaAdministrator, GroupFans, ActivityUsers
from .serializers import XiaoluAdministratorSerializers, GroupMamaAdministratorSerializers, GroupFansSerializers,\
    MamaGroupsSerializers
from flashsale.promotion.models import ActivityEntry
from flashsale.xiaolumm.models import XiaoluMama
from flashsale.xiaolumm.serializers import XiaoluMamaSerializer
from shopapp.weixin.models import WeixinUserInfo
from .forms import GroupFansForm


class XiaoluAdministratorViewSet(WeixinAuthMixin, viewsets.GenericViewSet):
    """
        小鹿微信群管理员
    """
    queryset = XiaoluAdministrator.objects.all()
    serializer_class = XiaoluAdministratorSerializers
    authentication_classes = (authentication.SessionAuthentication, authentication.BasicAuthentication)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @list_route(methods=['POST', 'GET'])
    def mama_join(self, request):
        if not request.user.is_anonymous():
            xiaoumama = request.user.customer.getXiaolumm() if request.user.customer else None
        else:
            # 1. check whether event_id is valid
            self.set_appid_and_secret(settings.WXPAY_APPID, settings.WXPAY_SECRET)
            # 2. get openid from cookie
            openid, unionid = self.get_cookie_openid_and_unoinid(request)
            if not self.valid_openid(unionid):
                # 3. get openid from gf'debug' or from using 'code' (if code exists)
                userinfo = self.get_auth_userinfo(request)
                unionid = userinfo.get("unionid")
                openid = userinfo.get("openid")
                if not self.valid_openid(unionid):
                    # 4. if we still dont have openid, we have to do oauth
                    redirect_url = self.get_snsuserinfo_redirct_url(request)
                    return redirect(redirect_url)
            xiaoumama = XiaoluMama.objects.filter(openid=unionid).first()
        if not xiaoumama:
            raise exceptions.ValidationError(u'您不是小鹿妈妈或者你的微信号未和小鹿妈妈账号绑定')
        mama_id = xiaoumama.id
        administrastor_id = request.POST.get('administrastor_id') or request.GET.get('administrastor_id')
        if GroupMamaAdministrator.objects.filter(mama_id=mama_id).exists():
            admin = GroupMamaAdministrator.objects.filter(mama_id=mama_id).first().admin
        elif administrastor_id:
            admin = XiaoluAdministrator.objects.filter(id=administrastor_id).first()
            if not admin:
                raise exceptions.NotFound(u'指定的管理员不存在')
        else:
            admin = XiaoluAdministrator.get_group_mincnt_admin()
        group = GroupMamaAdministrator.get_or_create(admin=admin, mama_id=mama_id)
        return Response(self.get_serializer(admin).data)

    @list_route(methods=['GET'])
    def mamawx_join(self, request):
        if not request.user.is_anonymous():
            xiaoumama = request.user.customer.getXiaolumm() if request.user.customer else None
        else:
            # 1. check whether event_id is valid
            self.set_appid_and_secret(settings.WXPAY_APPID, settings.WXPAY_SECRET)
            # 2. get openid from cookie
            openid, unionid = self.get_cookie_openid_and_unoinid(request)
            if not self.valid_openid(unionid):
                # 3. get openid from gf'debug' or from using 'code' (if code exists)
                userinfo = self.get_auth_userinfo(request)
                unionid = userinfo.get("unionid")
                openid = userinfo.get("openid")
                if not self.valid_openid(unionid):
                    # 4. if we still dont have openid, we have to do oauth
                    redirect_url = self.get_snsuserinfo_redirct_url(request)
                    return redirect(redirect_url)
            xiaoumama = XiaoluMama.objects.filter(openid=unionid).first()
        if not xiaoumama:
            raise exceptions.ValidationError(u'您不是小鹿妈妈或者你的微信号未和小鹿妈妈账号绑定')
        mama_id = xiaoumama.id
        administrastor_id = request.GET.get('administrastor_id')
        if GroupMamaAdministrator.objects.filter(mama_id=mama_id).exists():
            admin = GroupMamaAdministrator.objects.filter(mama_id=mama_id).first().admin
        elif administrastor_id:
            admin = XiaoluAdministrator.objects.filter(id=administrastor_id).first()
            if not admin:
                raise exceptions.NotFound(u'指定的管理员不存在')
        else:
            admin = XiaoluAdministrator.get_group_mincnt_admin()
        group = GroupMamaAdministrator.get_or_create(admin=admin, mama_id=mama_id)
        return redirect("/july_event/html/mama_attender.html?unionid=" + xiaoumama.openid)

    @list_route(methods=['GET'])
    def get_xiaolu_administrator(self, request):
        administrastor_id = request.GET.get('administrastor_id')
        if GroupMamaAdministrator.objects.filter(id=request.user.id).exists():
            admin = GroupMamaAdministrator.objects.filter(mama_id=request.user.id).first().admin
        elif administrastor_id:
            admin = GroupMamaAdministrator.objects.filter(id=administrastor_id).first()
            if not admin:
                raise exceptions.NotFound(u'指定的管理员不存在')
        else:
            admin = XiaoluAdministrator.get_group_mincnt_admin()
        return Response(self.get_serializer(admin).data)


class GroupMamaAdministratorViewSet(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        小鹿微信群
    """
    queryset = GroupMamaAdministrator.objects.all()
    serializer_class = MamaGroupsSerializers
    authentication_classes = (authentication.SessionAuthentication, authentication.BasicAuthentication)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @detail_route(methods=['GET'])
    def detail(self, request, pk):
        group = get_object_or_404(GroupMamaAdministrator, pk=pk)
        res = self.get_serializer(group).data
        res['mama'] = XiaoluMamaSerializer(group.mama).data
        return Response(res)

    @detail_route(methods=['GET'])
    def groups(self, requenst, pk):
        mama = XiaoluMama.objects.filter(openid=pk).first()
        if not mama:
            raise exceptions.NotFound(u'未能找到指定的小鹿妈妈')
        groups = GroupMamaAdministrator.objects.filter(mama_id=mama.id)
        if not groups.first():
            raise exceptions.NotFound(u'此小鹿妈妈尚未报名到微信群')
        res = {}
        admin = groups.first().admin
        res['admin'] = XiaoluAdministratorSerializers(admin).data
        res['groups'] = self.get_serializer(groups, many=True).data
        res = Response(res)
        res['Access-Control-Allow-Origin'] = '*'
        return res


class LiangXiActivityViewSet(WeixinAuthMixin, viewsets.GenericViewSet):
    """
        凉席活动后台支持
    """
    ACTIVITY_NAME = u"7月送万件宝宝凉席活动"
    queryset = GroupFans.objects.all()
    serializer_class = GroupFansSerializers
    authentication_classes = (authentication.SessionAuthentication, authentication.BasicAuthentication)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @property
    def activity(self):
        if not hasattr(self, '_activity_'):
            self._activity_ = ActivityEntry.objects.filter(title=LiangXiActivityViewSet.ACTIVITY_NAME).first()
        return self._activity_

    @detail_route(methods=['GET'])
    def detail(self, request, pk):
        fans = get_object_or_404(GroupFans, pk=pk)
        group = self.get_serializer(fans.group).data
        return Response(group)

    @list_route(methods=['GET'])
    def get_group_users(self, request):
        group_id = request.GET.get('group_id')
        group = GroupMamaAdministrator.objects.filter(id=group_id).first()
        if not group:
            raise exceptions.NotFound(u'指定的小鹿妈妈群不存在')
        queryset = self.filter_queryset(group.fans.all())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['POST', 'GET'])
    def join(self, request):
        form = GroupFansForm(request.DATA)
        if form.is_valid():
            raise exceptions.ValidationError(form.error_message)
        if not self.activity.is_on():
            raise exceptions.ValidationError(u"凉席活动暂不可使用")
        group_id = form.cleaned_data['group_id']
        # mama_id = form.cleaned_data['mama_id']
        group = GroupMamaAdministrator.objects.filter(group_uni_key=group_id).first()
        if not group:
            raise exceptions.NotFound(u'此妈妈尚未加入微信群组')
        self.set_appid_and_secret(settings.WXPAY_APPID, settings.WXPAY_SECRET)

        # get openid from cookie
        openid, unionid = self.get_cookie_openid_and_unoinid(request)

        userinfo = {}
        userinfo_records = WeixinUserInfo.objects.filter(unionid=unionid)
        record = userinfo_records.first()
        if record:
            userinfo.update({"unionid":record.unionid, "nickname":record.nick, "headimgurl":record.thumbnail})
        else:
            # get openid from 'debug' or from using 'code' (if code exists)
            userinfo = self.get_auth_userinfo(request)
            unionid = userinfo.get("unionid")
            openid = userinfo.get("openid")
            if not self.valid_openid(unionid):
                # if we still dont have openid, we have to do oauth
                redirect_url = self.get_snsuserinfo_redirct_url(request)
                return redirect(redirect_url)
        self.set_cookie_openid_and_unionid(unionid, openid)
        # if user already join a group, change group
        fans = GroupFans.objects.filter(
            union_id=userinfo.get('unionid')
        ).first()
        # 不许换群
        # if fans:
        #     fans.group_id = group.id
        #     fans.head_img_url = userinfo.get('headimgurl')
        #     fans.nick = userinfo.get('nickname')
        #     fans.save()
        # else:
        if not fans:
            fans = GroupFans.create(group, request.user.id, userinfo.get('headimgurl'), userinfo.get('nickname'),
                                userinfo.get('unionid'), userinfo.get('open_id'))
            ActivityUsers.join(self.activity, request.user.id, fans.group_id)
        group = GroupMamaAdministrator.objects.get(id=fans.group_id)
        return Response(GroupMamaAdministratorSerializers(group).data)