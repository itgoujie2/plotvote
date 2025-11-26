from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import hashlib
import random
import string


class UserProfile(models.Model):
    """Extended user profile with credit tracking"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Credit system
    credits = models.IntegerField(default=0, help_text="Available chapter generation credits")
    total_credits_purchased = models.IntegerField(default=0, help_text="Total credits purchased (lifetime)")
    total_credits_earned = models.IntegerField(default=0, help_text="Total credits earned (free)")
    total_credits_used = models.IntegerField(default=0, help_text="Total credits used (lifetime)")

    # Daily login tracking
    last_login_date = models.DateField(null=True, blank=True)
    consecutive_login_days = models.IntegerField(default=0)

    # Referral system
    referral_code = models.CharField(max_length=10, unique=True, blank=True)
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} - {self.credits} credits"

    def add_credits(self, amount, source='purchased'):
        """Add credits to user account"""
        self.credits += amount
        if source == 'purchased':
            self.total_credits_purchased += amount
        elif source == 'earned':
            self.total_credits_earned += amount
        self.save()

    def deduct_credits(self, amount):
        """Deduct credits from user account"""
        if self.credits >= amount:
            self.credits -= amount
            self.total_credits_used += amount
            self.save()
            return True
        return False

    def has_credits(self, amount=1):
        """Check if user has enough credits"""
        return self.credits >= amount

    def generate_referral_code(self):
        """Generate a unique referral code for this user"""
        if not self.referral_code:
            # Create a short code based on username + random string
            base = f"{self.user.username}{random.randint(1000, 9999)}"
            code = hashlib.md5(base.encode()).hexdigest()[:8].upper()
            self.referral_code = code
            self.save()
        return self.referral_code

    def check_daily_login_reward(self):
        """Check if user is eligible for daily login reward and award it"""
        today = timezone.now().date()

        # First login ever
        if not self.last_login_date:
            self.last_login_date = today
            self.consecutive_login_days = 1
            self._award_daily_login_credit()
            self.save()
            return True

        # Already claimed today
        if self.last_login_date == today:
            return False

        # Consecutive day
        yesterday = today - timezone.timedelta(days=1)
        if self.last_login_date == yesterday:
            self.consecutive_login_days += 1
        else:
            # Streak broken
            self.consecutive_login_days = 1

        self.last_login_date = today
        self._award_daily_login_credit()
        self.save()
        return True

    def _award_daily_login_credit(self):
        """Award 0.5 credits for daily login (implemented as 1 credit every 2 days)"""
        # To handle 0.5 credits, we'll give 1 credit every 2 days
        if self.consecutive_login_days % 2 == 0:
            # Check monthly cap (15 credits max from daily login)
            current_month_daily_credits = CreditTransaction.objects.filter(
                user=self.user,
                transaction_type='earned',
                description__contains='Daily login',
                created_at__year=timezone.now().year,
                created_at__month=timezone.now().month
            ).aggregate(models.Sum('amount'))['amount__sum'] or 0

            if current_month_daily_credits < 15:
                self.add_credits(1, source='earned')
                CreditTransaction.objects.create(
                    user=self.user,
                    amount=1,
                    transaction_type='earned',
                    description=f'Daily login reward (Day {self.consecutive_login_days})',
                    balance_after=self.credits
                )

    def has_active_subscription(self):
        """Check if user has an active subscription"""
        try:
            return self.user.subscription.is_active
        except UserSubscription.DoesNotExist:
            return False

    def should_see_ads(self):
        """
        Determine if user should see ads before chapter reads

        Returns False (no ads) if:
        - User has active subscription
        - User is willing to spend 0.2 credits to skip

        Returns True (show ads) if:
        - No subscription
        - Not enough credits to skip (or doesn't want to spend)
        """
        # Subscribers never see ads
        if self.has_active_subscription():
            return False

        # Free users see ads
        return True

    def can_skip_ad_with_credits(self):
        """Check if user has enough credits to skip an ad (0.2 credits)"""
        # We'll use 1 credit to skip 5 ads (0.2 per ad)
        # For simplicity, require at least 1 credit
        return self.credits >= 1


class CreditTransaction(models.Model):
    """Track all credit transactions for auditing"""

    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('earned', 'Earned'),
        ('spent', 'Spent'),
        ('refund', 'Refund'),
        ('bonus', 'Bonus'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_transactions')
    amount = models.IntegerField(help_text="Positive for add, negative for deduct")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)

    # Reference to related objects
    story = models.ForeignKey('stories.Story', on_delete=models.SET_NULL, null=True, blank=True)
    chapter = models.ForeignKey('stories.Chapter', on_delete=models.SET_NULL, null=True, blank=True)

    balance_after = models.IntegerField(help_text="Credit balance after transaction")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} credits"


class CreditPackage(models.Model):
    """Predefined credit packages for purchase"""

    name = models.CharField(max_length=50, help_text="Package name (e.g., Starter, Popular)")
    credits = models.IntegerField(help_text="Number of credits in this package")
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Price in USD")

    # Stripe integration
    stripe_price_id = models.CharField(max_length=100, blank=True, help_text="Stripe Price ID")

    # Display settings
    is_popular = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0, help_text="Order to display packages")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'price']

    def __str__(self):
        return f"{self.name} - {self.credits} credits (${self.price})"

    @property
    def price_per_credit(self):
        """Calculate price per credit"""
        return float(self.price) / self.credits if self.credits > 0 else 0

    @property
    def savings_percent(self):
        """Calculate savings compared to base price of $0.30"""
        base_price = 0.30
        if self.credits > 0:
            current_price = float(self.price) / self.credits
            savings = ((base_price - current_price) / base_price) * 100
            return max(0, int(savings))
        return 0


class Purchase(models.Model):
    """Track credit purchases"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    package = models.ForeignKey(CreditPackage, on_delete=models.SET_NULL, null=True)

    credits = models.IntegerField(help_text="Credits purchased")
    amount = models.DecimalField(max_digits=6, decimal_places=2, help_text="Amount paid in USD")

    # Stripe details
    stripe_checkout_session_id = models.CharField(max_length=200, unique=True)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.credits} credits - ${self.amount} ({self.status})"


class ChapterView(models.Model):
    """Track chapter views for reading rewards"""

    chapter = models.ForeignKey('stories.Chapter', on_delete=models.CASCADE, related_name='views')
    reader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chapter_views')

    # Reading engagement tracking
    read_percentage = models.IntegerField(default=0, help_text="Percentage of chapter read (0-100)")
    time_spent_seconds = models.IntegerField(default=0, help_text="Time spent reading in seconds")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('chapter', 'reader')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reader.username} read {self.chapter} ({self.read_percentage}%)"

    @property
    def is_qualified_read(self):
        """Check if this view qualifies for reading rewards (60%+ completion)"""
        return self.read_percentage >= 60


class SocialShare(models.Model):
    """Track social media shares for credit rewards"""

    PLATFORM_CHOICES = [
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('reddit', 'Reddit'),
        ('linkedin', 'LinkedIn'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_shares')
    story = models.ForeignKey('stories.Story', on_delete=models.CASCADE, related_name='social_shares')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)

    # Track if credit was awarded
    credit_awarded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} shared {self.story.title} on {self.platform}"


class SubscriptionPlan(models.Model):
    """Subscription plans for monthly recurring billing"""

    TIER_CHOICES = [
        ('reader', 'Reader'),
        ('writer', 'Writer'),
        ('pro', 'Pro'),
    ]

    name = models.CharField(max_length=50, help_text="Plan name (e.g., Reader, Writer, Pro)")
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Monthly price in USD")

    # Benefits
    monthly_credits = models.IntegerField(help_text="Credits included per month")
    ad_free_reading = models.BooleanField(default=True)
    priority_generation = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    analytics_access = models.BooleanField(default=False)
    remove_watermark = models.BooleanField(default=False)

    # Stripe integration
    stripe_price_id = models.CharField(max_length=100, blank=True, help_text="Stripe Price ID for subscriptions")

    # Display
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    is_popular = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'price']

    def __str__(self):
        return f"{self.name} - ${self.price}/month"


class UserSubscription(models.Model):
    """Track active user subscriptions"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'),
        ('expired', 'Expired'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)

    # Stripe details
    stripe_subscription_id = models.CharField(max_length=200, unique=True, blank=True)
    stripe_customer_id = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Billing cycle
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)

    # Credit tracking
    credits_used_this_period = models.IntegerField(default=0)
    last_credit_reset = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'} ({self.status})"

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'active' and self.current_period_end > timezone.now()

    @property
    def credits_remaining(self):
        """Calculate remaining credits for this billing period"""
        if not self.plan:
            return 0
        return max(0, self.plan.monthly_credits - self.credits_used_this_period)

    def refresh_monthly_credits(self):
        """Reset credits at start of new billing period"""
        self.credits_used_this_period = 0
        self.last_credit_reset = timezone.now()
        self.save()


class AdView(models.Model):
    """Track ad views for revenue calculation"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ad_views', null=True, blank=True)
    chapter = models.ForeignKey('stories.Chapter', on_delete=models.CASCADE, related_name='ad_views')

    # Ad details
    ad_duration_seconds = models.IntegerField(default=15)
    watched_full = models.BooleanField(default=False, help_text="Did user watch ad to completion")
    skipped_with_credits = models.BooleanField(default=False)

    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['chapter', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.chapter} (Watched: {self.watched_full})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        profile = UserProfile.objects.create(user=instance)
        # Generate referral code
        profile.generate_referral_code()
        # Give new users 10 free credits
        profile.add_credits(10, source='earned')
        CreditTransaction.objects.create(
            user=instance,
            amount=10,
            transaction_type='bonus',
            description='Welcome bonus - 10 free chapters',
            balance_after=profile.credits
        )
