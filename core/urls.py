from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('finance.urls')),
    path('api/auth/', include('authentication.urls')),
    path('api/dev/', include('developersOnly.urls')),
    path('', include('client.urls')),
    path('api/v2/', include('group.urls')),

    path('test/', include('wizard.urls')),
    path('select2/', include('django_select2.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)