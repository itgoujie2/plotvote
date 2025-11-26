from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import timezone
from django.db import models
from .forms import SimpleUserCreationForm
from .models import CreditPackage, Purchase, CreditTransaction, UserProfile, SocialShare
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Handle referral code
            referral_code = form.cleaned_data.get('referral_code', '').strip().upper()
            if referral_code:
                try:
                    referrer_profile = UserProfile.objects.get(referral_code=referral_code)
                    # Set referrer
                    user.profile.referred_by = referrer_profile.user
                    user.profile.save()

                    # Award bonus to new user (5 extra credits on top of the 10 welcome bonus)
                    user.profile.add_credits(5, source='earned')
                    CreditTransaction.objects.create(
                        user=user,
                        amount=5,
                        transaction_type='bonus',
                        description=f'Referral bonus from {referrer_profile.user.username}',
                        balance_after=user.profile.credits
                    )

                    # Award referrer (3 credits, check monthly cap)
                    current_month_referral_credits = CreditTransaction.objects.filter(
                        user=referrer_profile.user,
                        transaction_type='earned',
                        description__contains='Referral reward',
                        created_at__year=timezone.now().year,
                        created_at__month=timezone.now().month
                    ).aggregate(models.Sum('amount'))['amount__sum'] or 0

                    if current_month_referral_credits < 30:  # Monthly cap
                        referrer_profile.add_credits(3, source='earned')
                        CreditTransaction.objects.create(
                            user=referrer_profile.user,
                            amount=3,
                            transaction_type='earned',
                            description=f'Referral reward: {user.username} joined',
                            balance_after=referrer_profile.credits
                        )

                    messages.success(request, f'Welcome to PlotVote, {user.username}! You have 15 free credits (10 welcome + 5 referral bonus).')
                except UserProfile.DoesNotExist:
                    messages.warning(request, f'Invalid referral code. But welcome anyway, {user.username}! You have 10 free credits.')
            else:
                messages.success(request, f'Welcome to PlotVote, {user.username}! You have 10 free credits to start.')

            login(request, user)
            return redirect('stories:homepage')
    else:
        # Pre-fill referral code from URL parameter
        initial_data = {}
        ref_code = request.GET.get('ref', '')
        if ref_code:
            initial_data['referral_code'] = ref_code
        form = SimpleUserCreationForm(initial=initial_data)

    return render(request, 'users/register.html', {'form': form})


@login_required
def create_checkout_session(request, package_id):
    """Create a Stripe checkout session for purchasing credits"""
    package = get_object_or_404(CreditPackage, id=package_id, is_active=True)

    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(package.price * 100),  # Convert to cents
                    'product_data': {
                        'name': f'{package.name} Package',
                        'description': f'{package.credits} PlotVote Credits',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/credits/success?session_id={CHECKOUT_SESSION_ID}'),
            cancel_url=request.build_absolute_uri('/credits/cancel'),
            client_reference_id=str(request.user.id),
            metadata={
                'user_id': request.user.id,
                'package_id': package.id,
                'credits': package.credits,
            }
        )

        # Create purchase record
        Purchase.objects.create(
            user=request.user,
            package=package,
            credits=package.credits,
            amount=package.price,
            stripe_checkout_session_id=checkout_session.id,
            status='pending'
        )

        # Redirect to Stripe checkout
        return redirect(checkout_session.url)

    except Exception as e:
        messages.error(request, f'Error creating checkout session: {str(e)}')
        return redirect('stories:credits_dashboard')


@login_required
def payment_success(request):
    """Handle successful payment"""
    session_id = request.GET.get('session_id')

    # Check if session_id is the placeholder (Stripe didn't replace it)
    if session_id and session_id != '{CHECKOUT_SESSION_ID}':
        try:
            # Retrieve the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)

            # Find the purchase
            purchase = Purchase.objects.filter(
                stripe_checkout_session_id=session_id,
                user=request.user
            ).first()

            if purchase and purchase.status == 'pending':
                messages.info(request, 'Payment processing... Your credits will be added shortly.')
            elif purchase and purchase.status == 'completed':
                messages.success(request, f'Success! {purchase.credits} credits have been added to your account.')
            else:
                messages.success(request, 'Payment successful! Your credits have been added.')

        except Exception as e:
            # Don't show error to user - webhook will handle credit fulfillment
            messages.success(request, 'Payment successful! Your credits are being added to your account.')
    else:
        # Generic success message when session_id is not available
        messages.success(request, 'Payment successful! Your credits have been added to your account.')

    return redirect('stories:credits_dashboard')


@login_required
def payment_cancel(request):
    """Handle cancelled payment"""
    messages.warning(request, 'Payment was cancelled. No charges were made.')
    return redirect('stories:credits_dashboard')


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Get purchase record
        purchase = Purchase.objects.filter(
            stripe_checkout_session_id=session['id']
        ).first()

        if purchase and purchase.status == 'pending':
            # Update purchase
            purchase.stripe_payment_intent_id = session.get('payment_intent', '')
            purchase.status = 'completed'
            purchase.completed_at = timezone.now()
            purchase.save()

            # Add credits to user
            profile = purchase.user.profile
            profile.add_credits(purchase.credits, source='purchased')

            # Record transaction
            CreditTransaction.objects.create(
                user=purchase.user,
                amount=purchase.credits,
                transaction_type='purchase',
                description=f'Purchased {purchase.package.name} package',
                balance_after=profile.credits
            )

            print(f'Credits added: {purchase.user.username} received {purchase.credits} credits')

    return HttpResponse(status=200)


@login_required
def record_social_share(request, story_id, platform):
    """Record a social media share and award credit"""
    from stories.models import Story

    story = get_object_or_404(Story, id=story_id)

    # Only award credit if user is the story author
    if request.user == story.created_by:
        # Check if already shared on this platform today
        today = timezone.now().date()
        already_shared_today = SocialShare.objects.filter(
            user=request.user,
            story=story,
            platform=platform,
            created_at__date=today
        ).exists()

        if not already_shared_today:
            # Check monthly cap (5 credits max from social sharing)
            current_month_share_credits = CreditTransaction.objects.filter(
                user=request.user,
                transaction_type='earned',
                description__contains='Social share',
                created_at__year=timezone.now().year,
                created_at__month=timezone.now().month
            ).aggregate(models.Sum('amount'))['amount__sum'] or 0

            # Create share record
            share = SocialShare.objects.create(
                user=request.user,
                story=story,
                platform=platform
            )

            # Award credit if under monthly cap
            if current_month_share_credits < 5:
                profile = request.user.profile
                profile.add_credits(1, source='earned')

                CreditTransaction.objects.create(
                    user=request.user,
                    amount=1,
                    transaction_type='earned',
                    description=f'Social share: "{story.title}" on {platform}',
                    story=story,
                    balance_after=profile.credits
                )

                share.credit_awarded = True
                share.save()

                messages.success(request, f'Thanks for sharing! You earned 1 credit. ({5 - current_month_share_credits - 1} remaining this month)')
            else:
                messages.info(request, f'Thanks for sharing! (Monthly share credit limit reached)')

    return redirect('stories:story_detail', slug=story.slug)
