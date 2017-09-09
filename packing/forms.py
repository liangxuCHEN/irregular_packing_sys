# encoding=utf8
import os
from django import forms
from packing.models import DxfModel


class DxfForm(forms.ModelForm):
    class Meta:
        model = DxfModel
        fields = ['name', 'model_guid', 'material_guid', 'uploads']
