"""plotvote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from users import views as user_views
from stories.sitemaps import StaticViewSitemap, StorySitemap, ChapterSitemap

# Sitemap configuration
sitemaps = {
    'static': StaticViewSitemap,
    'stories': StorySitemap,
    'chapters': ChapterSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stories.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),

    # Payment callbacks (need to be at root level for Stripe redirects)
    path('credits/success', user_views.payment_success, name='payment_success'),
    path('credits/cancel', user_views.payment_cancel, name='payment_cancel'),

    # Stripe webhook (at root level)
    path('webhooks/stripe/', user_views.stripe_webhook, name='stripe_webhook'),

    # SEO: Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # SEO: Robots.txt
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots_txt'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
