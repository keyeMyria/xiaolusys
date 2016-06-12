from django.contrib import admin
from flashsale.mmexam.models import Question, Choice, Result, MamaDressResult, DressProduct


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class Qestiondmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'question_types', 'start_time', 'real_answer')
    ordering = ['id']
    list_filter = ['start_time']
    inlines = [ChoiceInline]


class Choicedmin(admin.ModelAdmin):
    list_display = ('question', 'choice_title', 'choice_text',)


class Resultdmin(admin.ModelAdmin):
    search_fields = ['daili_user']
    list_display = ('customer_id', 'daili_user', 'exam_state', 'sheaves', 'exam_date')


admin.site.register(Question, Qestiondmin)
admin.site.register(Choice, Choicedmin)
admin.site.register(Result, Resultdmin)


class MamaDressResultAdmin(admin.ModelAdmin):
    list_display = ('user_unionid', 'mama_nick', 'exam_score', 'exam_date', 'exam_state')
    search_fields = ['=user_unionid', '=referal_from']


admin.site.register(MamaDressResult, MamaDressResultAdmin)


class DressProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'age_min', 'age_max', 'category', 'product_id', 'modified', 'in_active')
    search_fields = ['=product_id']

    list_filter = ['in_active', 'created', 'category']


admin.site.register(DressProduct, DressProductAdmin)
