# -*- coding:utf8 -*-
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea

from core.admin import ApproxAdmin
from core.filters import DateScheduleFilter, DateFieldListFilter
from shopapp.smsmgr.models import SMSPlatform, SMSRecord, SMSActivity


class SMSPlatformAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'user_id', 'account', 'remainums', 'sendnums', 'is_default')
    # list_editable = ('update_time','task_type' ,'is_success','status')

    list_display_links = ('code', 'name',)

    search_fields = ['code', 'name', 'account']


# def get_readonly_fields(self, request, obj=None):
#        readonly_fields = self.readonly_fields+('code',)
#        return readonly_fields


admin.site.register(SMSPlatform, SMSPlatformAdmin)


class SMSRecordAdmin(ApproxAdmin):
    list_display = (
    'id', 'task_name', 'task_type', 'platform', 'task_id', 'countnums', 'succnums', 'created', 'modified', 'status')
    # list_editable = ('update_time','task_type' ,'is_success','status')

    list_display_links = ('task_name',)

    list_filter = ('task_type', 'platform', 'status', ('created', DateFieldListFilter))
    search_fields = ['id', 'mobiles', 'task_name', ]
    list_per_page = 40


admin.site.register(SMSRecord, SMSRecordAdmin)


class SMSActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'sms_type', 'text_tmpl', 'status')
    # list_editable = ('update_time','task_type' ,'is_success','status')

    list_filter = ('sms_type', 'status',)
    search_fields = ['text_tmpl']

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 4, 'cols': 60})},
    }


admin.site.register(SMSActivity, SMSActivityAdmin)
