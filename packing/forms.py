# encoding=utf8
import json
from django import forms
from packing.models import DxfModel

from packing.no_fit_polygon import sql


class DxfForm(forms.ModelForm):
    class Meta:
        model = DxfModel
        fields = ['name', 'rotation', 'material_guid', 'uploads']

    material_list = [(data['Guid'], "{} {}".format(data['MaterialCode'], data['MaterialName']))
                     for data in json.loads(sql.material_list())]
    # print material_list
    material_guid = forms.CharField(
        label=u'材料选择',
        widget=forms.Select(
            choices=material_list,
            attrs={
                'class': 'selectpicker',
                'data-live-search': "true",
                'data-actions-box': "true",
                'data-showtick': "true",
                'onchange': "changetype1(this)",
                'data-live-search-placeholder': "Search",
            }
        )
    )

    name = forms.CharField(label=u'模型名字', widget=forms.TextInput(attrs={'class': 'form-control'}))

