from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class SimpleUserCreationForm(UserCreationForm):
    """Simplified user creation form with minimal help text"""

    referral_code = forms.CharField(
        max_length=10,
        required=False,
        help_text='Optional: Enter a friend\'s referral code',
        widget=forms.TextInput(attrs={'placeholder': 'Referral code (optional)'})
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'referral_code')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = 'At least 8 characters'
        self.fields['password2'].help_text = None
