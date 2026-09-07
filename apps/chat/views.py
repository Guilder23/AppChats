from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Conversation, Message


def conversation_rows(user):
	rows = []
	for item in user.conversations.prefetch_related('participants', 'messages'):
		rows.append({'item': item, 'other': item.participants.exclude(id=user.id).first()})
	return rows


@login_required
def home(request):
	rows = conversation_rows(request.user)
	return render(request, 'chat/home.html', {'conversation_rows': rows, 'selected': rows[0]['item'] if rows else None, 'selected_other': rows[0]['other'] if rows else None})


@login_required
def conversation(request, conversation_id):
	item = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
	return render(request, 'chat/home.html', {
		'conversation_rows': conversation_rows(request.user),
		'selected': item,
		'selected_other': item.participants.exclude(id=request.user.id).first(),
	})


@login_required
def users(request):
	return JsonResponse({'users': list(User.objects.exclude(id=request.user.id).values('id', 'username'))})


@login_required
@require_POST
def create_conversation(request):
	user_id = request.POST.get('user_id')
	other = get_object_or_404(User, id=user_id)
	existing = Conversation.objects.filter(participants=request.user).filter(participants=other).distinct().first()
	item = existing or Conversation.objects.create()
	if not existing:
		item.participants.set([request.user, other])
	return JsonResponse({'id': item.id, 'url': f'/chat/conversacion/{item.id}/'})


@login_required
def messages(request, conversation_id):
	item = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
	data = [{'id': message.id, 'body': message.body, 'sender': message.sender.username,
			 'mine': message.sender_id == request.user.id,
			 'time': message.created_at.strftime('%H:%M')} for message in item.messages.select_related('sender')]
	return JsonResponse({'messages': data})
