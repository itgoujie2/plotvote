"""
Context processors for making data available to all templates
"""
from .models import SiteSettings


def beta_mode(request):
    """Add beta mode settings to all template contexts"""
    settings = SiteSettings.get_settings()
    return {
        'is_beta_mode': settings.beta_mode_enabled,
        'beta_message': settings.beta_message,
    }
