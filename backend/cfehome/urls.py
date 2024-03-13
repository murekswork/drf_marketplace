from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title='Application PI',
        default_version='v1',
        description='Application PI Description',
        contact=openapi.Contact(email='murekswork@gmail.com'),
        license=openapi.License(name='MIT LICENSE')
    ),
    public=True,
    permission_classes=(AllowAny, ),
)

urlpatterns = [

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/search', include('search.urls')),
    path('api/v2/', include('cfehome.routers')),
    path('__debug__/', include('debug_toolbar.urls')),
]
