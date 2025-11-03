from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SimpleUserCreationForm(UserCreationForm):
    """Simplified user creation form with minimal help text"""

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = 'At least 8 characters'
        self.fields['password2'].help_text = None
