"""irregual_packing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from packing import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from django.conf import settings


urlpatterns = [
    url(r'^$', views.home_page, name='index'),
    url(r'^dxf_models$', views.DxfModelIndexView.as_view(), name='dxf_index'),
    url(r'^projects$', views.ProjectIndexView.as_view(), name='project_list'),
    url(r'^add_dxf_model$', views.add_dxf_model, name='add_dxf_model'),
    url(r'^calc_shape_num$', views.calc_shape_num, name='calc_shape_num'),
    url(r'^calc_shape_use$', views.calc_shape_use, name='calc_shape_use'),
    url(r'^shape_use_task$', views.shape_use_task, name='shape_use_task'),
    url(r'^product_detail/(?P<p_id>\d+)/$', views.show_project, name='show_project'),
    url(r'^admin/', admin.site.urls),

    url(r'^irregular/dxf$', views.dxf_json, name='dxf_list'),
    url(r'^irregular/jobs_list$', views.get_jobs_list, name='jobs_list'),
]

urlpatterns += staticfiles_urlpatterns()

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

