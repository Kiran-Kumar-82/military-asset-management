from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/accounts/login/')


@login_required(login_url='login')
def settings(request):
    """User profile settings"""
    if request.method == 'POST':
        user = request.user
        action = request.POST.get('action')
        
        if action == 'update_profile':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            
            # Basic validation
            if not email:
                messages.error(request, 'Email is required.')
            elif email != user.email and User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already in use.')
            else:
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('settings')
        
        elif action == 'change_password':
            old_password = request.POST.get('old_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if not old_password:
                messages.error(request, 'Current password is required.')
            elif not user.check_password(old_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully!')
                return redirect('login')
    
    context = {
        'user': request.user,
    }
    return render(request, 'accounts/settings.html', context)


urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=AuthenticationForm
    ), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', settings, name='settings'),
]
