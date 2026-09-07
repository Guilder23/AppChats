from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Profile


def home(request):
	return redirect('chat:home') if request.user.is_authenticated else redirect('accounts:login')


def logout_user(request):
	if request.user.is_authenticated:
		Profile.objects.update_or_create(user=request.user, defaults={'last_seen': timezone.now()})
	logout(request)
	return redirect('accounts:login')


def profile(request):
	if not request.user.is_authenticated:
		return redirect('accounts:login')
	user_profile, _ = Profile.objects.get_or_create(user=request.user)
	error = None
	if request.method == 'POST':
		name = request.POST.get('display_name', '').strip()
		bio = request.POST.get('bio', '').strip()
		avatar = request.FILES.get('avatar')
		if len(name) > 80 or len(bio) > 160:
			error = 'El nombre o la información son demasiado largos.'
		elif avatar and avatar.size > 5 * 1024 * 1024:
			error = 'La foto debe pesar menos de 5 MB.'
		else:
			user_profile.display_name = name
			user_profile.bio = bio
			if avatar:
				user_profile.avatar = avatar
			user_profile.save()
			return redirect('accounts:profile')
	return render(request, 'accounts/profile.html', {'profile': user_profile, 'error': error})


def register(request):
	if request.user.is_authenticated:
		return redirect('chat:home')
	error = None
	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		email = request.POST.get('email', '').strip()
		password = request.POST.get('password', '')
		if not username or not password:
			error = 'Completa usuario y contraseña.'
		elif User.objects.filter(username__iexact=username).exists():
			error = 'Ese usuario ya existe.'
		else:
			user = User.objects.create_user(username=username, email=email, password=password)
			login(request, user)
			return redirect('chat:home')
	return render(request, 'accounts/register.html', {'error': error})
