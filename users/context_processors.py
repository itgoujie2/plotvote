"""
Context processors for PlotVote users app
"""
from django.contrib import messages


def daily_login_check(request):
    """
    Check daily login reward on every page load for authenticated users
    """
    if request.user.is_authenticated:
        # Check if user earned daily login reward
        rewarded = request.user.profile.check_daily_login_reward()

        # Only show message on first page load of the day
        if rewarded and request.user.profile.consecutive_login_days % 2 == 0:
            # User earned a credit (every 2 days)
            messages.success(
                request,
                f'🎁 Daily login reward! You earned 1 credit. (Streak: {request.user.profile.consecutive_login_days} days)'
            )
        elif rewarded and request.user.profile.consecutive_login_days == 1:
            # First day or streak just started
            messages.info(
                request,
                f'Welcome back! Keep logging in daily to earn credits. (Streak: 1 day)'
            )

    return {}
