from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('logistics/', include('apps.logistics.urls', namespace='logistics')),
    path('store/', include('apps.store.urls', namespace='store')),
    path('moderation/', include('apps.moderation.urls', namespace='moderation')),
    path('owner/', include('apps.owner.urls', namespace='owner')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
