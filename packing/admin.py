from django.contrib import admin

from packing.models import DxfModel


class DxfModelAdmin(admin.ModelAdmin):
    list_display = ('model_guid', 'name', 'uploads')

admin.site.register(DxfModel, DxfModelAdmin)
