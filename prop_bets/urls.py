from django.conf.urls import include, url, handler404, handler500
from django.contrib import admin
from ui import views as ui_views

handler404='ui.views.page_not_found'
handler500='ui.views.server_error'

urlpatterns = [
  url(r'^api/', include('api.urls')),
  url(r'^ui/', include('ui.urls')),
  url(r'^admin/', admin.site.urls),
  url(r'^accounts/', include('django.contrib.auth.urls')),
  url(r'^$', ui_views.home, name='home')
]
