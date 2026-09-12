from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('product/', include('product.urls')),
    path('category/', include('category.urls')),
    path('comment/', include('comment.urls')),
    path('card/', include('card.urls')),
    path('order/', include('order.urls')),
]

if settings.FRONTEND_DIR.exists():
    urlpatterns += [
        path('', TemplateView.as_view(template_name='index.html')),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)