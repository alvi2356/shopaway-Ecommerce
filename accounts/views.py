from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'accounts/profile.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', { 'form': form })
