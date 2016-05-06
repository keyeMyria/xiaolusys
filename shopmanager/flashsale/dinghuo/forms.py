# coding: utf-8
import json

from django import forms

from core.forms import BaseForm


class InBoundListForm(BaseForm):
    supplier = forms.CharField(required=False)
    express_no = forms.CharField(required=False)
    target_id = forms.IntegerField(required=False, initial=0)
    sent_from = forms.IntegerField(required=False, initial=1)
    inbound_id = forms.IntegerField(required=False, initial=0)

    @property
    def json(self):
        ca = self.cleaned_attrs
        return {
            'supplier': ca.supplier,
            'express_no': ca.express_no,
            'target_id': ca.target_id,
            'sent_from': ca.sent_from,
            'inbound_id': ca.inbound_id
        }


class EditInBoundForm(InBoundListForm):
    inbound_id = forms.IntegerField(required=False, initial=0)
    skus = forms.CharField(required=False, initial='[]')
    details = forms.CharField(required=False, initial='[]')
    images = forms.CharField(required=False, initial='[]')
    memo = forms.CharField(required=False, initial='')


class AdvanceDingHuoForm(BaseForm):
    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)


class InBoundForm(BaseForm):
    inbound_id = forms.IntegerField(required=False, initial=0)
    supplier_id = forms.IntegerField(required=False, initial=0)
    orderlist_id = forms.IntegerField(required=False, initial=0)
    express_no = forms.CharField(required=False, initial='')


class MatchOrderListsForm(BaseForm):
    inbound_skus = forms.CharField(required=False, initial='{}')


class CreateInBoundForm(BaseForm):
    inbound_skus = forms.CharField(required=False, initial='{}')
    express_no = forms.CharField(required=False, initial='')
    orderlist_id = forms.CharField(required=False, initial=0)
    supplier_id = forms.IntegerField()
    inbound_id = forms.IntegerField(required=False, initial=0)
    memo = forms.CharField(required=False, initial='')


class SaveMemoForm(BaseForm):
    inbound_id = forms.IntegerField()
    memo = forms.CharField(required=False)
    inbound_skus = forms.CharField(required=False)


class SaveDistrictsForm(BaseForm):
    inbound_id = forms.IntegerField()
    inbound_skus = forms.CharField(required=False)
