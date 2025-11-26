from django.contrib import admin
from .models import (UserProfile, CreditTransaction, CreditPackage, Purchase,
                     ChapterView, SocialShare, SubscriptionPlan, UserSubscription, AdView)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'credits', 'consecutive_login_days', 'referral_code', 'total_credits_purchased', 'total_credits_earned', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'referral_code')
    readonly_fields = ('total_credits_purchased', 'total_credits_earned', 'total_credits_used', 'referral_code', 'created_at', 'updated_at')


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'description', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)


@admin.register(CreditPackage)
class CreditPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'credits', 'price', 'price_per_credit', 'savings_percent', 'is_popular', 'is_active', 'display_order')
    list_filter = ('is_active', 'is_popular')
    list_editable = ('is_popular', 'is_active', 'display_order')
    search_fields = ('name',)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'credits', 'amount', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'stripe_checkout_session_id', 'stripe_payment_intent_id')
    readonly_fields = ('created_at', 'stripe_checkout_session_id', 'stripe_payment_intent_id')


@admin.register(ChapterView)
class ChapterViewAdmin(admin.ModelAdmin):
    list_display = ('reader', 'chapter', 'read_percentage', 'time_spent_seconds', 'created_at')
    list_filter = ('created_at', 'read_percentage')
    search_fields = ('reader__username', 'chapter__story__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SocialShare)
class SocialShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'story', 'platform', 'credit_awarded', 'created_at')
    list_filter = ('platform', 'credit_awarded', 'created_at')
    search_fields = ('user__username', 'story__title')
    readonly_fields = ('created_at',)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'price', 'monthly_credits', 'ad_free_reading', 'is_popular', 'is_active', 'display_order')
    list_filter = ('is_active', 'is_popular', 'tier')
    list_editable = ('is_popular', 'is_active', 'display_order')
    search_fields = ('name', 'tier')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'current_period_start', 'current_period_end', 'cancel_at_period_end')
    list_filter = ('status', 'cancel_at_period_end', 'plan')
    search_fields = ('user__username', 'stripe_subscription_id')
    readonly_fields = ('created_at', 'updated_at', 'stripe_subscription_id', 'stripe_customer_id')


@admin.register(AdView)
class AdViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter', 'ad_duration_seconds', 'watched_full', 'skipped_with_credits', 'created_at')
    list_filter = ('watched_full', 'skipped_with_credits', 'created_at')
    search_fields = ('user__username', 'chapter__story__title')
    readonly_fields = ('created_at', 'ip_address', 'user_agent')
