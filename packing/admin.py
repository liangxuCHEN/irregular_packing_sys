from django.contrib import admin

from packing.models import DxfModel, PackDetail, Project


class DxfModelAdmin(admin.ModelAdmin):
    list_display = ('model_guid', 'name', 'uploads')


class PackDetailAdmin(admin.ModelAdmin):
    list_display = ('material_code', 'areas', 'created')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('comment', 'created')

admin.site.register(DxfModel, DxfModelAdmin)
admin.site.register(PackDetail, PackDetailAdmin)
admin.site.register(Project, ProjectAdmin)
