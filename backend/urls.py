"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  # ← include is needed
from django.conf.urls.static import static  # Add this import
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/procurement/', include('procurement.urls')),
    path('api/receipts/', include('receipts.urls')),
    path('api/rentals/', include('rentals.urls')),  # ✅ corrected line
    path('api/settings/', include('settings.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/warehouse/', include('warehouse.urls')),
    path('api/product-documentation/', include('product_documentation.urls')),
    path('api/chat/', include('chat.urls', namespace='chat')),
   

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
