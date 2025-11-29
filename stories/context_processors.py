"""
Context processors for making data available to all templates
"""
from .models import SiteSettings


def beta_mode(request):
    """Add beta mode settings to all template contexts"""
    try:
        settings = SiteSettings.get_settings()
        return {
            'is_beta_mode': settings.beta_mode_enabled,
            'beta_message': settings.beta_message,
        }
    except Exception:
        # If table doesn't exist yet (during initial migration), return defaults
        return {
            'is_beta_mode': False,
            'beta_message': '',
        }
