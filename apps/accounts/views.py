from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


def home(request):
	return redirect('chat:home') if request.user.is_authenticated else redirect('accounts:login')


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
