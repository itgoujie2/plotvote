from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),

    # Stripe payment URLs
    path('checkout/<int:package_id>/', views.create_checkout_session, name='checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),

    # Social sharing
    path('share/<int:story_id>/<str:platform>/', views.record_social_share, name='record_share'),
]
