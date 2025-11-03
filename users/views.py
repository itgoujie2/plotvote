from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import SimpleUserCreationForm


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to PlotVote, {user.username}!')
            return redirect('stories:homepage')
    else:
        form = SimpleUserCreationForm()

    return render(request, 'users/register.html', {'form': form})
